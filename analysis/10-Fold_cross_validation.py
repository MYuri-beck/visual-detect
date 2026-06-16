import os
import yaml
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import KFold
from ultralytics import YOLO
import torch
import sys

# Desabilita multiprocessing do PyTorch para evitar problemas no Windows
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
torch.set_num_threads(1)

# Define o metodo de inicialização do multiprocessing
if sys.platform.startswith('win'):
    try:
        torch.multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass

# =========================================================
# 1. CONFIGURAÇÃO (Aponte para os seus arquivos atuais)
# =========================================================
PATH_DATA_YAML = Path("C:\\Users\\yurim\\Desktop\\Software Visual Detect\\VisualDetect\\trainings\\data.yaml") # O seu arquivo atual
PATH_ARGS_FENECIT = Path("C:\\Users\\yurim\\Desktop\\Software Visual Detect\\VisualDetect\\trainings\\runs\\detect\\treio_yolov8m_fenecit2\\args.yaml")
NOME_PROJETO = "Validacao_Cruzada_Fenecit2"

# Detecta automaticamente o device disponível
def detectar_device():
    """Detecta automaticamente se CUDA está disponível"""
    if torch.cuda.is_available():
        device = 0
        device_name = f"GPU: {torch.cuda.get_device_name(0)}"
    else:
        device = "cpu"
        device_name = "CPU"
    print(f"🖥️  Device detectado: {device_name}\n")
    return device

def main():
    # =========================================================
    # CHECKPOINT: VERIFICAR SE HÁ RESULTADOS PARCIAIS
    # =========================================================
    output_dir = Path("Validacao_Cruzada_Fenecit2")
    checkpoint_file = output_dir / "checkpoint_resultados.csv"

    resultados_lista = []
    fold_inicial = 1

    if checkpoint_file.exists():
        print("=" * 60)
        print("🔄 CHECKPOINT DETECTADO!")
        print("=" * 60)
        print(f"📁 Carregando resultados parciais de: {checkpoint_file}")

        df_checkpoint = pd.read_csv(checkpoint_file)
        resultados_lista = df_checkpoint.to_dict('records')
        fold_inicial = len(resultados_lista) + 1

        print(f"✅ {len(resultados_lista)} folds já concluídos")
        print(f"🚀 Continuando do Fold {fold_inicial}/10\n")
    else:
        print("=" * 60)
        print("🆕 INICIANDO NOVO TREINAMENTO 10-FOLD")
        print("=" * 60)
    print("=" * 60)
    print("🔍 VALIDANDO ARQUIVOS DE CONFIGURAÇÃO...")
    print("=" * 60)

    if not PATH_DATA_YAML.exists():
        print(f"❌ ERRO: Arquivo {PATH_DATA_YAML} não encontrado!")
        sys.exit(1)

    if not PATH_ARGS_FENECIT.exists():
        print(f"❌ ERRO: Arquivo {PATH_ARGS_FENECIT} não encontrado!")
        print("⚠️  Usando configurações padrão...")
        args_orig = {
            'epochs': 100,
            'imgsz': 640,
            'batch': 16,
            'patience': 20,
            'device': 0
        }
    else:
        with open(PATH_ARGS_FENECIT, 'r') as f:
            args_orig = yaml.safe_load(f) or {}

    # =========================================================
    # 3. LER CONFIGURAÇÕES ORIGINAIS
    # =========================================================
    with open(PATH_DATA_YAML, 'r') as f:
        data_orig = yaml.safe_load(f)

    if not data_orig or 'nc' not in data_orig or 'names' not in data_orig:
        print("❌ ERRO: data.yaml inválido!")
        sys.exit(1)

    print(f"✅ Configurações carregadas com sucesso!")
    print(f"   Classes: {data_orig['nc']}")
    print(f"   Nomes: {data_orig['names']}\n")

    # =========================================================
    # 4. LOCALIZAR E COLETAR TODAS AS IMAGENS
    # =========================================================
    print("=" * 60)
    print("📂 COLETANDO DATASET...")
    print("=" * 60)

    # Nova lógica robusta para lidar com data.yaml sem a chave 'path'
    if 'path' in data_orig:
        base_path = Path(data_orig['path'])
        train_dir = base_path / data_orig['train']
        val_dir = base_path / data_orig.get('val', data_orig['train'])
    else:
        # Se o yaml não tiver 'path', lê direto do 'train' e 'val'
        train_dir = Path(data_orig['train'])
        val_dir = Path(data_orig.get('val', data_orig['train']))

    # Se o caminho no YAML não for absoluto (C:\...), ele procura na mesma pasta do data.yaml
    if not train_dir.is_absolute():
        train_dir = PATH_DATA_YAML.parent / train_dir
    if not val_dir.is_absolute():
        val_dir = PATH_DATA_YAML.parent / val_dir

    print(f"  📁 Train: {train_dir}")
    print(f"  📁 Val: {val_dir}")

    # Coleta todas as imagens (juntando treino e validação do dataset original)
    img_files = []
    exts_allowed = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}

    if train_dir.exists():
        train_imgs = [f for f in train_dir.glob("*.*") if f.suffix.lower() in exts_allowed]
        img_files.extend(train_imgs)
        print(f"  ✅ {len(train_imgs)} imagens encontradas em train/")

    if val_dir.exists() and val_dir.resolve() != train_dir.resolve():
        val_imgs = [f for f in val_dir.glob("*.*") if f.suffix.lower() in exts_allowed]
        img_files.extend(val_imgs)
        print(f"  ✅ {len(val_imgs)} imagens encontradas em val/")

    # Remove possíveis fotos duplicadas e organiza a lista
    img_files = sorted(list(set(img_files)))

    if len(img_files) == 0:
        print("❌ ERRO: Nenhuma imagem encontrada! Verifique os caminhos dentro do seu data.yaml.")
        sys.exit(1)

    print(f"\n✅ Total de {len(img_files)} imagens prontas para a divisão 10-Fold.\n")

    # =========================================================
    # 5. LOOP 10-FOLD COM TREINAMENTO AUTOMÁTICO
    # =========================================================
    device = detectar_device()

    # Configuração base para treinamento
    batch_size = args_orig.get('batch', 16)
    epochs = args_orig.get('epochs', 100)
    imgsz = args_orig.get('imgsz', 640)

    # Ajusta batch size se usar CPU
    if device == "cpu" and batch_size > 8:
        batch_size = 8
        print(f"⚠️  Batch size reduzido para {batch_size} (CPU)\n")

    print("=" * 60)
    print("🚀 INICIANDO TREINAMENTO 10-FOLD CROSS-VALIDATION")
    print("=" * 60)
    print(f"Epochs: {epochs} | ImgSize: {imgsz} | Batch: {batch_size}\n")

    kf = KFold(n_splits=10, shuffle=True, random_state=42)
    # Pula os folds já concluídos
    folds_to_process = list(enumerate(kf.split(img_files), 1))[fold_inicial-1:]

    for fold, (train_idx, val_idx) in folds_to_process:
        try:
            print(f"\n{'='*60}")
            print(f"📊 FOLD {fold}/10 - {len(train_idx)} treino | {len(val_idx)} validação")
            print(f"{'='*60}")
            
            # Criar pasta e arquivos do fold
            fold_dir = Path(f"temp_kfold/fold_{fold}")
            fold_dir.mkdir(parents=True, exist_ok=True)
            
            train_txt = fold_dir / "train.txt"
            val_txt = fold_dir / "val.txt"
            
            # Escreve caminhos absolutos das imagens
            with open(train_txt, 'w') as f:
                f.write('\n'.join([str(img_files[i].absolute()) for i in train_idx]))
            with open(val_txt, 'w') as f:
                f.write('\n'.join([str(img_files[i].absolute()) for i in val_idx]))
        
            print(f"✅ Arquivos de split criados")
        
            # CRIA O YAML ESPECÍFICO DO FOLD (Herdando classes do original)
            fold_yaml = fold_dir / "data_fold.yaml"
            with open(fold_yaml, 'w') as f:
                yaml.dump({
                    'path': str(fold_dir.absolute()),
                    'train': "train.txt",
                    'val': "val.txt",
                    'nc': data_orig['nc'],
                    'names': data_orig['names']
                }, f)
        
            print(f"✅ YAML do fold criado")
            
            # TREINAMENTO (Herdando argumentos do Fenecit 2)
            print(f"🔄 Iniciando treinamento...")
            model = YOLO("yolov8m.pt")
            
            results = model.train(
                data=str(fold_yaml),
                project="Validacao_Cruzada_Fenecit2",
                name=f"Fold_{fold}",
                epochs=epochs,
                imgsz=imgsz,
                batch=batch_size,
                device=device,  # Usa device detectado automaticamente
                patience=20,
                save=True,
                verbose=True,
                workers=0  # Desabilita multiprocessing para evitar erros no Windows
            )
            
            # Coleta métricas com validação
            if results.results_dict:
                m = results.results_dict
                fold_metrics = {
                    'Fold': fold,
                    'mAP50': m.get('metrics/mAP50(B)', 0),
                    'Precisao': m.get('metrics/precision(B)', 0),
                    'Recall': m.get('metrics/recall(B)', 0),
                    'Status': '✅ Sucesso'
                }
                resultados_lista.append(fold_metrics)

                # SALVA CHECKPOINT APÓS CADA FOLD BEM-SUCEDIDO
                output_dir.mkdir(exist_ok=True)
                df_checkpoint = pd.DataFrame(resultados_lista)
                df_checkpoint.to_csv(checkpoint_file, index=False)
                print(f"💾 Checkpoint salvo: {len(resultados_lista)} folds concluídos")

                print(f"✅ Fold {fold} concluído!")
                print(f"   mAP50: {fold_metrics['mAP50']:.4f}")
                print(f"   Precision: {fold_metrics['Precisao']:.4f}")
                print(f"   Recall: {fold_metrics['Recall']:.4f}")
            else:
                print(f"⚠️  Fold {fold}: Sem resultados de métricas")
                resultados_lista.append({
                    'Fold': fold,
                    'mAP50': 0,
                    'Precisao': 0,
                    'Recall': 0,
                    'Status': '⚠️  Incompleto'
                })
            
        except Exception as e:
            print(f"❌ ERRO no Fold {fold}: {str(e)}")
            fold_metrics = {
                'Fold': fold,
                'mAP50': 0,
                'Precisao': 0,
                'Recall': 0,
                'Status': f'❌ Erro: {str(e)[:50]}'
            }
            resultados_lista.append(fold_metrics)

            # SALVA CHECKPOINT MESMO COM ERRO (para não perder progresso)
            output_dir.mkdir(exist_ok=True)
            df_checkpoint = pd.DataFrame(resultados_lista)
            df_checkpoint.to_csv(checkpoint_file, index=False)
            print(f"💾 Checkpoint salvo (com erro): {len(resultados_lista)} folds processados")

    # =========================================================
    # 6. FINALIZAÇÃO: TABELAS, ESTATÍSTICAS E GRÁFICOS
    # =========================================================
    print("\n" + "=" * 60)
    print("📈 PROCESSANDO RESULTADOS...")
    print("=" * 60)

    # Cria DataFrame com resultados
    df = pd.DataFrame(resultados_lista)

    # Filtra apenas folds bem-sucedidos para estatísticas
    df_validos = df[df['Status'] == '✅ Sucesso'].copy()

    # Garante pasta de saída
    output_dir = Path("Validacao_Cruzada_Fenecit2")
    output_dir.mkdir(exist_ok=True)

    # Salva tabela completa
    csv_path = output_dir / "resultados_completos.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Tabela completa salva em: {csv_path}")

    # Remove checkpoint após conclusão bem-sucedida
    if checkpoint_file.exists():
        checkpoint_file.unlink()
        print(f"🗑️  Checkpoint removido (treinamento concluído)")

    # Gera resumo estatístico
    if len(df_validos) > 0:
        resumo = pd.DataFrame({
            'Métrica': ['mAP50', 'Precisao', 'Recall'],
            'Média': [
                df_validos['mAP50'].mean(),
                df_validos['Precisao'].mean(),
                df_validos['Recall'].mean()
            ],
            'Desvio Padrão': [
                df_validos['mAP50'].std(),
                df_validos['Precisao'].std(),
                df_validos['Recall'].std()
            ],
            'Min': [
                df_validos['mAP50'].min(),
                df_validos['Precisao'].min(),
                df_validos['Recall'].min()
            ],
            'Max': [
                df_validos['mAP50'].max(),
                df_validos['Precisao'].max(),
                df_validos['Recall'].max()
            ]
        })
        
        resumo_path = output_dir / "resumo_estatistico.csv"
        resumo.to_csv(resumo_path, index=False)
        print(f"✅ Resumo estatístico salvo em: {resumo_path}")
        
        print("\n" + "=" * 60)
        print("📊 RESUMO FINAL - 10-FOLD CROSS-VALIDATION")
        print("=" * 60)
        print(resumo.to_string(index=False))
        
        # Gera Gráfico melhorado
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Gráfico 1: Barras com erro
        ax1 = axes[0]
        metricas = resumo['Métrica'].values
        medias = resumo['Média'].values
        desvios = resumo['Desvio Padrão'].values
        
        bars = ax1.bar(metricas, medias, yerr=desvios, capsize=10, 
                        color=['#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.8)
        ax1.set_ylabel('Score', fontsize=12)
        ax1.set_title('Métricas Médias com Desvio Padrão', fontsize=14, fontweight='bold')
        ax1.set_ylim(0, 1)
        ax1.grid(axis='y', alpha=0.3)
        
        # Adiciona valores nas barras
        for bar, media in zip(bars, medias):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{media:.4f}', ha='center', va='bottom', fontsize=10)
        
        # Gráfico 2: Evolução por fold
        ax2 = axes[1]
        fold_nums = df_validos['Fold'].values
        ax2.plot(fold_nums, df_validos['mAP50'].values, marker='o', label='mAP50', linewidth=2)
        ax2.plot(fold_nums, df_validos['Precisao'].values, marker='s', label='Precisão', linewidth=2)
        ax2.plot(fold_nums, df_validos['Recall'].values, marker='^', label='Recall', linewidth=2)
        ax2.set_xlabel('Fold', fontsize=12)
        ax2.set_ylabel('Score', fontsize=12)
        ax2.set_title('Performance por Fold', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(alpha=0.3)
        ax2.set_ylim(0, 1)
        
        plt.tight_layout()
        
        graph_path = output_dir / "grafico_validacao.png"
        plt.savefig(graph_path, dpi=300, bbox_inches='tight')
        print(f"\n✅ Gráfico salvo em: {graph_path}")
        plt.close()
    else:
        print("⚠️  Nenhum fold completado com sucesso!")

    print("\n" + "=" * 60)
    print(f"✅ VALIDAÇÃO CRUZADA CONCLUÍDA!")
    print(f"📁 Todos os resultados salvos em: {output_dir.absolute()}")
    print("=" * 60)


if __name__ == '__main__':
    main()