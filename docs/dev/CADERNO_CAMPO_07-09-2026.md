# Caderno de Campo - VisualDetect

**Data:** 07 de setembro de 2026  
**Responsáveis:** Yuri Mendes | Andrei Krug  
**Instituição:** SENAI / NUDEP - Curso Técnico em Desenvolvimento de Sistemas  
**Sessão:** Engenharia de Software & Interação Homem-Máquina (IHM / Touchscreen)

---

## Registro de Alterações - Software v1.2

### Contexto e Motivação

Com o avanço do desenvolvimento do protótipo físico do **VisualDetect**, duas novas demandas de engenharia surgiram para aprimorar o sistema:

1. **Formalização da Arquitetura (Diagramas de Sequência):**  
   Necessidade de documentar formalmente a troca de mensagens, ciclo de vida das threads concorrentes e fluxo de dados entre os componentes do software (UI CustomTkinter, Sessão de Captura, Câmera OpenCV, Inferência YOLO e Controle HID).

2. **Adaptação para Display Touchscreen (`TOUCH_MODE`):**  
   O protótipo inicial utilizava um controle físico cabeado/sem fio baseado no microcontrolador Raspberry Pi Pico 2W enviando teclas de teclado (setas direcionais e ENTER). Para suportar a evolução do hardware com display sensível ao toque (touchscreen), a interface gráfica precisava se tornar totalmente operável por toques diretos, sem perder a compatibilidade com a navegação física já consolidada.

---

### Alterações Realizadas

#### 1. Mapeamento de Sequência do Sistema (`docs/dev/DIAGRAMAS_SEQUENCIA.md`)

Foi elaborada a documentação completa dos fluxos de execução do sistema em 5 diagramas de sequência modulares no formato Mermaid:

- **Parte 1 — Inicialização e Bootstrap:** Ciclo de vida desde o `main.py`, instanciação do backend, thread da câmera, pré-carregamento do modelo YOLO durante a `ScreenLoading` e transição para a tela institucional `ScreenT0`.
- **Parte 2 — Navegação e Configuração:** Fluxo de seleção no menu principal (`ScreenT1`), navegação interativa no wizard de dois passos (`ScreenT2`) e conferência de parâmetros com feed da câmera ao vivo (`ScreenT3`).
- **Parte 3 — Pipeline de Captura Assíncrona:** Comunicação entre a interface (`ScreenT4`) e a thread em segundo plano `_capture_loop`, sincronização por temporizador de alta precisão e barra de progresso em tempo real.
- **Parte 4 — Inferência YOLO e Persistência:** Interrupção temporária do feed para liberação de recursos de CPU/RAM, execução síncrona do modelo no `VisionAnalyzer`, geração das imagens anotadas e gravação estruturada do `detections.json` antes de exibir a `ScreenT5`.
- **Parte 5 — Galeria e Protocolo HID:** Navegação hierárquica em 3 níveis da galeria de exames e decodificação das interrupções HID provenientes do firmware do Pico 2W.

---

#### 2. Implementação do Suporte a Touchscreen (`TOUCH_MODE`)

No arquivo [`app/ui.py`](file:///c:/Users/Yuri%20Mendes/Desktop/Desktop/visual-detect/app/ui.py), foi introduzida a flag de configuração para desenvolvedores:

```python
# TOUCH_MODE: True  → navegação por toque/clique (display touchscreen)
#             False → navegação por teclado/HID Pico 2W (padrão de produto)
TOUCH_MODE = True
```

Quando `TOUCH_MODE = False`, o sistema permanece 100% retrocompatível com teclado/HID. Quando `TOUCH_MODE = True`, as telas adaptam-se dinamicamente:

* **ScreenT0 (Boas-vindas):** O rótulo *"Pressione ENTER para continuar"* é substituído por um botão de ação destacado **`CONTINUAR →`**.
* **ScreenT1 (Splash / Menu):** Os botões **`INICIAR`** e **`GALERIA`** tornam-se imediatamente clicáveis via atributo `command`, dispensando a necessidade de seleção prévia com foco.
* **ScreenT2 (Wizard de Configuração):**
  * Inclusão de botões visíveis de ajuste fino **`＋`** e **`－`** ao lado dos valores numéricos.
  * Inclusão de botões de navegação no rodapé: **`← VOLTAR`** e **`PRÓXIMO →`** (ou **`CONFIRMAR →`** no passo final).
  * Ocultação de textos instrucionais de teclado (*"Setas ajustam, ENTER avança"*).
* **ScreenT3 (Revisão e Feed):**
  * Botões **`← VOLTAR`** e **`INICIAR →`** recebem handlers de clique direto.
  * Texto de instrução atualizado para orientar o toque direto no botão de início.
* **ScreenT4 e ScreenT4b (Captura e Inferência):**
  * Permanecem bloqueadas tanto para teclado quanto para toque, garantindo que o exame e a análise da rede neural não sofram interrupções inesperadas.
* **ScreenT5 (Conclusão do Exame):**
  * Botões **`NOVO EXAME`** e **`VER GALERIA`** recebem eventos de clique direto.
* **ScreenGaleria (Biblioteca de Exames):**
  * **Header:** Adicionado botão persistente **`← VOLTAR`** no canto superior esquerdo para transição entre níveis (Nível 3 $\rightarrow$ Nível 2 $\rightarrow$ Nível 1 $\rightarrow$ Tela de Origem).
  * **Nível 1 & Nível 2:** Evento `<Button-1>` vinculado diretamente a cada linha e seus respectivos componentes filhos, permitindo abrir o exame ou a análise com um simples toque.
  * **Nível 3 (Visualizador com Detecções):** Adicionados botões de navegação **`◀ ANTERIOR`** e **`PRÓXIMO ▶`** no rodapé para permitir folhear todas as fotos analisadas.
* **Prevenção de Conflitos:** Todos os métodos `handle_key` das telas ignoram eventos físicos quando `TOUCH_MODE = True`, impedindo duplo acionamento ou dessincronização de estado.

---

### Testes e Validação

1. **Validação Estática e Compilação:**
   * Verificação via `python -m py_compile app/ui.py` concluída com sucesso (código de saída 0, sem erros de sintaxe).
2. **Controle de Versão:**
   * Criado commit `62dab9f`: *docs: adiciona diagramas de sequencia completos (5 partes)*
   * Criado commit `5f7b6ef`: *feat(ui): adicionar suporte a tela touch via flag TOUCH_MODE*
   * Sincronização remota via `git push origin main` concluída com sucesso.

---

### Procedimento de Execução e Teste no Raspberry Pi

Para testar as alterações no protótipo embarcado:

```bash
# 1. Atualizar o código no Raspberry Pi
git pull

# 2. Ativar o ambiente virtual e executar com aceleração visual
source .venv/bin/activate
python app/main.py --fullscreen
```

---

### Próximos Passos

- [ ] Validação de campo do toque capacitivo/resistivo no display oficial do Raspberry Pi.
- [ ] Teste de tempo de resposta da troca de telas via toque.
- [ ] Calibração da área de toque dos botões caso haja necessidade para dedos enluvados em ambiente clínico.
