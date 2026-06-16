"""
Script isolado para completar a validação cruzada 10-fold
Executa o fold 10 e combina com os resultados dos folds 1-9
Gera relatório final com estatísticas e gráficos
"""

import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from ultralytics import YOLO
import torch
import sys

# Desabilita multiprocessing do PyTorch para evitar problemas no Windows
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
torch.set_num_threads(1)

if sys.platform.startswith('win'):
    try:
        torch.multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass


def main():
    print("=" * 70)
    print("🚀 COMPLETANDO VALIDAÇÃO CRUZADA 10-FOLD")
    print("=" * 70)
    
    # =========================================================
    # 1. CARREGAR CONFIGURAÇÕES
    # =========================================================
    PATH_DATA_YAML = Path("C:\\Users\\yurim\\Desktop\\Software Visual Detect\\VisualDetect\\trainings\\data.yaml")
    OUTPUT_DIR = Path("Validacao_Cruzada_Fenecit2")
    RUNS_DIR = Path("C:\\Users\\yurim\\Desktop\\Software Visual Detect\\VisualDetect\\runs\\detect\\Validacao_Cruzada_Fenecit2")
    
    print(f"\n🔍 Procurando folds em: {RUNS_DIR}")
    print(f"   Caminho existe: {RUNS_DIR.exists()}")
    
    print("\n📂 Carregando configurações...")
    with open(PATH_DATA_YAML, 'r') as f:
        data_orig = yaml.safe_load(f)
    
    print(f"✅ Classes: {data_orig['nc']}")
    print(f"✅ Nomes: {data_orig['names']}")
    
    # =========================================================
    # 2. CARREGAR RESULTADOS DOS FOLDS 1-9
    # =========================================================
    print("\n" + "=" * 70)
    print("📊 COLETANDO RESULTADOS DOS FOLDS 1-9")
    print("=" * 70)
    
    resultados_lista = []
    folds_encontrados = 0
    
    for fold_num in range(1, 10):
        fold_dir = RUNS_DIR / f"Fold_{fold_num}"
        results_file = fold_dir / "results.csv"
        
        if fold_dir.exists():
            print(f"📁 Fold {fold_num}: ", end="")
            try:
                # Tentar ler o arquivo results.csv do YOLO
                if results_file.exists():
                    df = pd.read_csv(results_file)
                    # Pega a última linha (melhor resultado)
                    last_row = df.iloc[-1]
                    
                    fold_result = {
                        'Fold': fold_num,
                        'mAP50': last_row.get('metrics/mAP50(B)', 0),
                        'Precisao': last_row.get('metrics/precision(B)', 0),
                        'Recall': last_row.get('metrics/recall(B)', 0),
                        'Status': '✅ Carregado'
                    }
                    resultados_lista.append(fold_result)
                    print(f"✅ mAP50={fold_result['mAP50']:.4f}")
                    folds_encontrados += 1
                else:
                    print(f"⚠️  Sem arquivo results.csv")
            except Exception as e:
                print(f"⚠️  Erro ao ler: {str(e)[:30]}")
        else:
            print(f"Fold {fold_num}: ❌ Pasta não encontrada em {fold_dir}")
    
    print(f"\n✅ {folds_encontrados} folds carregados com sucesso")
    
    # =========================================================
    # 3. TREINAR FOLD 10
    # =========================================================
    print("\n" + "=" * 70)
    print("🔄 TREINANDO FOLD 10")
    print("=" * 70)
    
    fold_yaml = Path("temp_kfold/fold_10/data_fold.yaml")
    
    if not fold_yaml.exists():
        print(f"❌ ERRO: {fold_yaml} não encontrado!")
        sys.exit(1)
    
    print(f"📁 Usando arquivos de split do fold 10")
    
    # Carregar argumentos do Fold 10 anterior se existir
    PATH_ARGS_FOLD_10 = RUNS_DIR / "Fold_10" / "args.yaml"
    if PATH_ARGS_FOLD_10.exists():
        print(f"📋 Usando parâmetros do Fold 10 anterior")
        with open(PATH_ARGS_FOLD_10, 'r') as f:
            args_fold_10 = yaml.safe_load(f)
    else:
        print(f"⚠️  Arquivo de argumentos não encontrado, usando padrão")
        args_fold_10 = {}
    
    print(f"\n🚀 Iniciando treinamento...")
    model = YOLO("yolov8m.pt")
    
    results = model.train(
        data=str(fold_yaml),
        project="Validacao_Cruzada_Fenecit2",
        name="Fold_10_Final",
        epochs=args_fold_10.get('epochs', 350),
        imgsz=args_fold_10.get('imgsz', 640),
        batch=args_fold_10.get('batch', 8),
        device=int(str(args_fold_10.get('device', 0))),
        patience=args_fold_10.get('patience', 20),
        save=args_fold_10.get('save', True),
        verbose=args_fold_10.get('verbose', True),
        workers=args_fold_10.get('workers', 0),
        amp=args_fold_10.get('amp', True),
        deterministic=args_fold_10.get('deterministic', True),
        lr0=args_fold_10.get('lr0', 0.01),
        lrf=args_fold_10.get('lrf', 0.01),
        momentum=args_fold_10.get('momentum', 0.937),
        weight_decay=args_fold_10.get('weight_decay', 0.0005),
        warmup_epochs=args_fold_10.get('warmup_epochs', 3.0),
        warmup_momentum=args_fold_10.get('warmup_momentum', 0.8),
        warmup_bias_lr=args_fold_10.get('warmup_bias_lr', 0.1),
        box=args_fold_10.get('box', 7.5),
        cls=args_fold_10.get('cls', 0.5),
        dfl=args_fold_10.get('dfl', 1.5),
        hsv_h=args_fold_10.get('hsv_h', 0.015),
        hsv_s=args_fold_10.get('hsv_s', 0.7),
        hsv_v=args_fold_10.get('hsv_v', 0.4),
        degrees=args_fold_10.get('degrees', 0.0),
        translate=args_fold_10.get('translate', 0.1),
        scale=args_fold_10.get('scale', 0.5),
        fliplr=args_fold_10.get('fliplr', 0.5),
        mosaic=args_fold_10.get('mosaic', 1.0),
        close_mosaic=args_fold_10.get('close_mosaic', 10),
        erasing=args_fold_10.get('erasing', 0.4),
        auto_augment=args_fold_10.get('auto_augment', 'randaugment'),
        plots=args_fold_10.get('plots', True),
        pretrained=args_fold_10.get('pretrained', True),
        val=args_fold_10.get('val', True)
    )
    
    # =========================================================
    # 4. ADICIONAR RESULTADO DO FOLD 10
    # =========================================================
    print("\n" + "=" * 70)
    print("📊 RESULTADO DO FOLD 10")
    print("=" * 70)
    
    if results.results_dict:
        m = results.results_dict
        fold_10_result = {
            'Fold': 10,
            'mAP50': m.get('metrics/mAP50(B)', 0),
            'Precisao': m.get('metrics/precision(B)', 0),
            'Recall': m.get('metrics/recall(B)', 0),
            'Status': '✅ Treinado'
        }
        
        resultados_lista.append(fold_10_result)
        print(f"✅ Fold 10 concluído!")
        print(f"   mAP50: {fold_10_result['mAP50']:.4f}")
        print(f"   Precision: {fold_10_result['Precisao']:.4f}")
        print(f"   Recall: {fold_10_result['Recall']:.4f}")
    else:
        print(f"❌ Sem resultados de métricas!")
        fold_10_result = {
            'Fold': 10,
            'mAP50': 0,
            'Precisao': 0,
            'Recall': 0,
            'Status': '❌ Erro no treinamento'
        }
        resultados_lista.append(fold_10_result)
    
    # =========================================================
    # 5. GERAR ESTATÍSTICAS FINAIS
    # =========================================================
    print("\n" + "=" * 70)
    print("📈 ESTATÍSTICAS FINAIS - 10-FOLD CROSS-VALIDATION")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Salvar tabela completa
    df_completo = pd.DataFrame(resultados_lista)
    csv_completo = OUTPUT_DIR / "resultados_completos_10fold.csv"
    df_completo.to_csv(csv_completo, index=False)
    print(f"\n✅ Tabela completa salva: {csv_completo}")
    
    # Filtrar apenas folds bem-sucedidos
    df_validos = df_completo[df_completo['Status'].str.contains('✅|Treinado')].copy()
    
    if len(df_validos) > 0:
        # Gerar resumo estatístico
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
        
        resumo_path = OUTPUT_DIR / "resumo_estatistico_10fold.csv"
        resumo.to_csv(resumo_path, index=False)
        print(f"✅ Resumo estatístico salvo: {resumo_path}\n")
        
        print(resumo.to_string(index=False))
        
        # =========================================================
        # 6. GERAR GRÁFICOS
        # =========================================================
        print("\n📊 Gerando gráficos...")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Gráfico 1: Barras com erro
        ax1 = axes[0]
        metricas = resumo['Métrica'].values
        medias = resumo['Média'].values
        desvios = resumo['Desvio Padrão'].values
        
        bars = ax1.bar(metricas, medias, yerr=desvios, capsize=10, 
                        color=['#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.8)
        ax1.set_ylabel('Score', fontsize=12)
        ax1.set_title('Métricas Médias com Desvio Padrão (10-Fold)', fontsize=14, fontweight='bold')
        ax1.set_ylim(0, 1)
        ax1.grid(axis='y', alpha=0.3)
        
        for bar, media in zip(bars, medias):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{media:.4f}', ha='center', va='bottom', fontsize=10)
        
        # Gráfico 2: Evolução por fold
        ax2 = axes[1]
        fold_nums = df_validos['Fold'].values
        ax2.plot(fold_nums, df_validos['mAP50'].values, marker='o', label='mAP50', linewidth=2, markersize=8)
        ax2.plot(fold_nums, df_validos['Precisao'].values, marker='s', label='Precisão', linewidth=2, markersize=8)
        ax2.plot(fold_nums, df_validos['Recall'].values, marker='^', label='Recall', linewidth=2, markersize=8)
        ax2.set_xlabel('Fold', fontsize=12)
        ax2.set_ylabel('Score', fontsize=12)
        ax2.set_title('Performance por Fold', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(alpha=0.3)
        ax2.set_ylim(0, 1)
        ax2.set_xticks(range(1, 11))
        
        plt.tight_layout()
        
        graph_path = OUTPUT_DIR / "grafico_10fold_validacao.png"
        plt.savefig(graph_path, dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico salvo: {graph_path}")
        plt.close()
    else:
        print("❌ Nenhum fold completado com sucesso!")
    
    # =========================================================
    # 7. RELATÓRIO FINAL
    # =========================================================
    print("\n" + "=" * 70)
    print("✅ VALIDAÇÃO CRUZADA 10-FOLD CONCLUÍDA!")
    print("=" * 70)
    print(f"\n📁 Resultados salvos em:")
    print(f"   🗂️  {OUTPUT_DIR.absolute()}")
    print(f"\n📊 Arquivos gerados:")
    print(f"   📄 resultados_completos_10fold.csv")
    print(f"   📊 resumo_estatistico_10fold.csv")
    print(f"   📈 grafico_10fold_validacao.png")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
