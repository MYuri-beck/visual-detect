import os
import pandas as pd
from ultralytics import YOLO
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ==============================================================================
#  CONFIGURAÇÕES 
# ==============================================================================

# 1. Onde estão as fotos dos voluntários (Teste Prático)?
PASTA_IMAGENS = r"capturas_voluntarios_analisar"

# 2. Onde estão os treinamentos? (A pasta "principal" de todos)
#  vasculhar todas as subpastas daqui procurando 'best.pt'
PASTA_TREINAMENTOS = r"modelos-analise"

# 3. Onde salvar os resultados organizados
PASTA_SAIDA = r"Relatorios_Finais_Organizados"

# ==============================================================================
#  LÓGICA DO SCRIPT
# ==============================================================================

def calculate_iou(box1, box2):
    """Calcula sobreposição para diferenciar '2 olhos' de 'erro de dupla detecção'"""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    return intersection / union if union > 0 else 0

def encontrar_modelos_inteligente(pasta_raiz):
    """
    Varre as pastas e descobre o nome do modelo automaticamente.
    Ex: '.../YOLO_Medium/weights/best.pt' -> Nome: 'YOLO_Medium'
    """
    lista_modelos = []
    print(f"🔍 Escaneando modelos em: {pasta_raiz}...")
    
    for root, dirs, files in os.walk(pasta_raiz):
        if 'best.pt' in files:
            path_completo = os.path.join(root, 'best.pt')
            path_obj = Path(path_completo)
            
            # Lógica para pegar o nome correto da pasta
            # Se a estrutura for padrao YOLO (NomeModelo/weights/best.pt)
            if path_obj.parent.name == 'weights':
                nome_modelo = path_obj.parent.parent.name
            else:
                # Se o best.pt estiver solto na pasta do modelo
                nome_modelo = path_obj.parent.name
            
            lista_modelos.append((nome_modelo, path_completo))
            print(f"   -> Encontrado: {nome_modelo}")
            
    return lista_modelos

def gerar_grafico(nome, limpa, dupla, nao, acuracia, pasta_destino):
    fig, ax = plt.subplots(figsize=(9, 7))
    
    categorias = ['Correto', 'Dupla Detecção', 'Não Detectado']
    valores = [limpa, dupla, nao]
    cores = ['#27ae60', '#f39c12', '#c0392b'] # Verde, Laranja, Vermelho

    barras = ax.bar(categorias, valores, color=cores, edgecolor='black', alpha=0.8)

    ax.set_title(f'Desempenho: {nome}\nAcurácia Média: {acuracia:.1f}%', fontsize=12, fontweight='bold')
    ax.set_ylabel('Quantidade de Imagens')
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    for barra in barras:
        height = barra.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}',
                        xy=(barra.get_x() + barra.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(pasta_destino, f"grafico_{nome}.png"), dpi=300)
    plt.close()

def main():
    if not os.path.exists(PASTA_IMAGENS):
        print("ERRO: Pasta de imagens não encontrada.")
        return

    # 1. Encontrar Modelos
    modelos = encontrar_modelos_inteligente(PASTA_TREINAMENTOS)
    if not modelos:
        print("ERRO: Nenhum arquivo 'best.pt' encontrado.")
        return

    print(f"\n Iniciando análise de {len(modelos)} modelos...\n")
    
    imagens = [f for f in os.listdir(PASTA_IMAGENS) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

    # 2. Processar cada modelo
    for nome_modelo, path_modelo in modelos:
        print(f"Processando: {nome_modelo}...")
        
        # --- CRIA PASTA EXCLUSIVA PARA O MODELO ---
        pasta_saida_modelo = os.path.join(PASTA_SAIDA, f"Analise_{nome_modelo}")
        os.makedirs(pasta_saida_modelo, exist_ok=True)
        # ------------------------------------------

        try:
            model = YOLO(path_modelo)
        except:
            print(f"Falha ao carregar pesos de {nome_modelo}")
            continue

        dados = []
        confs_total = []
        c_limpa, c_dupla, c_nao = 0, 0, 0

        for img in imagens:
            # Inferência
            res = model(os.path.join(PASTA_IMAGENS, img), conf=0.25, verbose=False)[0]
            boxes = res.boxes.xyxy.cpu().numpy()
            qtd = len(boxes)

            if qtd > 0:
                confs_total.extend(res.boxes.conf.cpu().numpy())
            else:
                confs_total.append(0.0)

            tipo = "Sucesso"
            if qtd == 0:
                c_nao += 1; tipo = "Nao_Detectado"
            elif qtd == 1:
                c_limpa += 1
            else:
                overlap = False
                for i in range(qtd):
                    for j in range(i+1, qtd):
                        if calculate_iou(boxes[i], boxes[j]) > 0.5: overlap = True
                if overlap: c_dupla += 1; tipo = "Dupla_Deteccao"
                else: c_limpa += 1

            dados.append({'Imagem': img, 'Qtd': qtd, 'Resultado': tipo})

        # 3. Salvar Resultados
        acc = (sum(confs_total)/len(confs_total)*100) if confs_total else 0
        
        pd.DataFrame(dados).to_csv(os.path.join(pasta_saida_modelo, f"tabela_{nome_modelo}.csv"), index=False)
        gerar_grafico(nome_modelo, c_limpa, c_dupla, c_nao, acc, pasta_saida_modelo)
        
        print(f"  Relatório salvo em: {pasta_saida_modelo}\n")

    print("PROCESSO CONCLUÍDO! Verifique a pasta de saída.")

if __name__ == "__main__":
    main()