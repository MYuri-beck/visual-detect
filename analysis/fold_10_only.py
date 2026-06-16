import os
import yaml
import pandas as pd
from pathlib import Path
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

def main():
    print("=" * 60)
    print("🚀 TREINAMENTO FOLD 10 APENAS")
    print("=" * 60)
    
    # Carregar configurações originais
    PATH_DATA_YAML = Path("C:\\Users\\yurim\\Desktop\\Software Visual Detect\\VisualDetect\\trainings\\data.yaml")
    PATH_ARGS_FOLD_10 = Path("Validacao_Cruzada_Fenecit2/Fold_10/args.yaml")
    
    with open(PATH_DATA_YAML, 'r') as f:
        data_orig = yaml.safe_load(f)
    
    # Carregar argumentos do Fold 10 anterior
    if PATH_ARGS_FOLD_10.exists():
        print(f"📁 Carregando parâmetros do Fold 10 anterior...")
        with open(PATH_ARGS_FOLD_10, 'r') as f:
            args_fold_10 = yaml.safe_load(f)
    else:
        print(f"⚠️  Arquivo de argumentos não encontrado, usando padrão...")
        args_fold_10 = {}
    
    # Usar arquivos já criados do fold 10
    fold_yaml = Path("temp_kfold/fold_10/data_fold.yaml")
    
    if not fold_yaml.exists():
        print(f"❌ ERRO: {fold_yaml} não encontrado!")
        sys.exit(1)
    
    print(f"✅ Configuração carregada")
    print(f"📁 Usando dados do Fold 10")
    print(f"   Classes: {data_orig['nc']}")
    print(f"   Nomes: {data_orig['names']}\n")
    
    # Treinar apenas fold 10 COM OS MESMOS PARÂMETROS
    print("🔄 Iniciando treinamento do Fold 10...")
    model = YOLO("yolov8m.pt")
    
    results = model.train(
        data=str(fold_yaml),
        project="Validacao_Cruzada_Fenecit2",
        name="Fold_10",
        epochs=args_fold_10.get('epochs', 350),
        imgsz=args_fold_10.get('imgsz', 640),
        batch=args_fold_10.get('batch', 8),
        device=int(str(args_fold_10.get('device', 0))),  # Converte string para int se necessário
        patience=args_fold_10.get('patience', 20),
        save=args_fold_10.get('save', True),
        verbose=args_fold_10.get('verbose', True),
        workers=args_fold_10.get('workers', 0),
        amp=args_fold_10.get('amp', True),
        deterministic=args_fold_10.get('deterministic', True),
        # Parâmetros de aprendizado
        lr0=args_fold_10.get('lr0', 0.01),
        lrf=args_fold_10.get('lrf', 0.01),
        momentum=args_fold_10.get('momentum', 0.937),
        weight_decay=args_fold_10.get('weight_decay', 0.0005),
        warmup_epochs=args_fold_10.get('warmup_epochs', 3.0),
        warmup_momentum=args_fold_10.get('warmup_momentum', 0.8),
        warmup_bias_lr=args_fold_10.get('warmup_bias_lr', 0.1),
        # Parâmetros de loss
        box=args_fold_10.get('box', 7.5),
        cls=args_fold_10.get('cls', 0.5),
        dfl=args_fold_10.get('dfl', 1.5),
        # Parâmetros de augmentação
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
        # Outros
        plots=args_fold_10.get('plots', True),
        pretrained=args_fold_10.get('pretrained', True),
        val=args_fold_10.get('val', True)
    )
    
    # Salvar métricas do fold 10
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DO FOLD 10")
    print("=" * 60)
    
    if results.results_dict:
        m = results.results_dict
        fold_result = {
            'Fold': 10,
            'mAP50': m.get('metrics/mAP50(B)', 0),
            'Precisao': m.get('metrics/precision(B)', 0),
            'Recall': m.get('metrics/recall(B)', 0),
            'Status': '✅ Sucesso'
        }
        
        print(f"✅ Fold 10 concluído!")
        print(f"   mAP50: {fold_result['mAP50']:.4f}")
        print(f"   Precision: {fold_result['Precisao']:.4f}")
        print(f"   Recall: {fold_result['Recall']:.4f}\n")
        
        # Salvar resultado em CSV
        output_dir = Path("Validacao_Cruzada_Fenecit2")
        output_dir.mkdir(exist_ok=True)
        
        result_csv = output_dir / "fold_10_resultado.csv"
        df_result = pd.DataFrame([fold_result])
        df_result.to_csv(result_csv, index=False)
        print(f"✅ Resultado salvo em: {result_csv}")
    else:
        print(f"❌ Sem resultados de métricas!")
    
    print("=" * 60)


if __name__ == '__main__':
    main()