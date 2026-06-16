import os

# ===== CONFIGURAÇÕES =====
# Caminho da pasta onde ficam seus treinos
pasta_raiz = "C:/Users/yurim/OneDrive/Desktop/analisar" 

# Extensões que queremos renomear (Resultados são sempre PNG, CSV ou YAML)
extensoes_alvo = (".png", ".csv", ".yaml")

def renomear_universal():
    if not os.path.exists(pasta_raiz):
        print(f"❌ Erro: A pasta '{pasta_raiz}' não existe.")
        return

    print(f"📂 Varrendo a pasta: {pasta_raiz}...\n")
    
    # Lista apenas as pastas de treino
    pastas_treino = [f for f in os.listdir(pasta_raiz) if os.path.isdir(os.path.join(pasta_raiz, f))]
    contador = 0

    for nome_pasta in pastas_treino:
        caminho_pasta = os.path.join(pasta_raiz, nome_pasta)
        print(f"   wd  Entrando em: {nome_pasta}")
        
        arquivos = os.listdir(caminho_pasta)

        for arquivo in arquivos:
            # 1. Verifica se é um arquivo de resultado (PNG, CSV ou YAML)
            if arquivo.lower().endswith(extensoes_alvo):
                
                # 2. Pula se já estiver renomeado (começa com o nome da pasta)
                if arquivo.startswith(nome_pasta):
                    continue

                # 3. Renomeia
                caminho_antigo = os.path.join(caminho_pasta, arquivo)
                novo_nome = f"{nome_pasta}_{arquivo}"
                caminho_novo = os.path.join(caminho_pasta, novo_nome)
                
                try:
                    os.rename(caminho_antigo, caminho_novo)
                    print(f"      ✅ Renomeado: {arquivo} -> {novo_nome}")
                    contador += 1
                except Exception as e:
                    print(f"      ❌ Erro ao renomear {arquivo}: {e}")

    print("\n" + "="*40)
    print(f"🎉 Pronto! {contador} arquivos foram atualizados.")
    print("Agora seus 'BoxPR_curve.png' e 'results.csv' devem estar com o nome correto.")

if __name__ == "__main__":
    renomear_universal()