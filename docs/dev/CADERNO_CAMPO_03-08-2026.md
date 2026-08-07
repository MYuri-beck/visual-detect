# Caderno de Campo — VisualDetect

**Data:** 03 de agosto de 2026  
**Responsáveis:** Yuri Mendes | Andrei Krug  
**Instituição:** SENAI / NUDEP — Curso Técnico em Desenvolvimento de Sistemas  
**Sessão:** Desenvolvimento de Software — Iteração de Interface

---

## Registro de Alterações — Software v1.1

### Contexto

Durante testes de campo com o equipamento no Raspberry Pi, foram identificados dois problemas
funcionais que impactavam a experiência de uso e a estabilidade do sistema:

**Problema 1 — Conflito de recursos durante a análise YOLO**

Na versão anterior (v1.0), após a fase de captura de fotos, o sistema executava a análise do
modelo YOLO diretamente na tela T4 ("Capturando"), mantendo a câmera ativa e o temporizador
em execução. Esse comportamento gerava dois efeitos indesejados observados em campo:

- O **temporizador ficava "bugado"** — continuava contando mesmo após o fim das capturas,
  pois a análise YOLO bloqueia o loop de tempo sem interrompê-lo corretamente.
- A **câmera permanecia ativa** durante a análise, consumindo processamento do Raspberry Pi
  (leitura de frames a ~30 FPS) em paralelo com a inferência do modelo, o que degradava
  o desempenho da análise YOLO e aumentava o tempo total de espera.

**Problema 2 — Ausência de acesso histórico às análises**

Não havia nenhuma forma de revisar exames anteriores sem acessar o sistema de arquivos
manualmente via terminal. Isso tornava o equipamento dependente de um computador externo
para qualquer revisão de resultados, o que é incompatível com o uso em campo.

---

### Alterações Realizadas

#### 1. Nova Tela: T4b — Processando / Analisando

**Arquivo:** `app/ui.py` | `app/backend.py`

Foi criada uma tela intermediária que separa as fases de **captura** e **análise** no fluxo
de navegação do sistema.

**O que muda no fluxo:**

| Antes (v1.0) | Depois (v1.1) |
|---|---|
| T4 (captura + análise na mesma tela) → T5 | T4 (captura) → T4b (análise) → T5 |

**Como funciona tecnicamente:**

- Ao final da última captura, o backend sinaliza para a UI via callback `on_capture_done_callback`
- A UI troca imediatamente para a tela T4b
- T4b **para a câmera** (`CameraManager.stop()`) ao ser exibida, liberando o hardware
- T4b registra seus callbacks de progresso diretamente na sessão do backend
  (`session._ui_analyze_progress_cb`) — isso permite que a thread YOLO, já em execução,
  atualize a tela em tempo real sem necessidade de reiniciar o processo
- A análise é executada pelo backend com um atraso de 400ms (tempo suficiente para o
  tkinter trocar a tela e registrar os callbacks antes do YOLO começar)
- Uma barra de progresso âmbar mostra o avanço imagem a imagem ("Analisando: Analise 01...")
- Ao concluir, todos os indicadores viram verde e o sistema navega automaticamente para T5

**Por que parar a câmera é importante no Raspberry Pi:**

O Raspberry Pi 4B possui recursos de CPU limitados. A thread da câmera consome ~5–10% de CPU
continuamente (leitura de frames em 30 FPS). Durante a inferência YOLO, esse processamento
concorrente aumenta a latência de cada análise. Parando a câmera durante T4b, toda a
capacidade de processamento fica disponível para o modelo. A câmera é reiniciada
automaticamente ao entrar em T3 para um novo exame.

---

#### 2. Reorganização das imagens analisadas por exame

**Arquivo:** `app/backend.py` — método `_analyze_all()`

As imagens analisadas pelo YOLO passaram a ser salvas em **subpastas por exame**.

**Estrutura anterior (v1.0):**
```
capturas_analisadas_voluntarios/
  analyzed_20260803_143510_capture_1.jpg
  analyzed_20260803_143510_capture_2.jpg
  analyzed_20260803_151200_capture_1.jpg   <- exames misturados sem separação
```

**Estrutura nova (v1.1):**
```
capturas_analisadas_voluntarios/
  Exame 03-08-26 - 14:35/
    Analise 01.jpg
    Analise 02.jpg
    detections.json
  Exame 03-08-26 - 15:12/
    Analise 01.jpg
    ...
```

O arquivo `detections.json` registra os resultados numéricos (label + confiança) de cada
imagem, permitindo leitura posterior pela Galeria sem necessidade de re-executar o modelo.

---

#### 3. Nova Tela: Galeria — Biblioteca de Exames

**Arquivo:** `app/ui.py`

Foi criada uma tela de visualização de exames anteriores, acessível fora do ciclo
normal de uso (não interfere no fluxo de exame).

**Acesso:**
- Na tela inicial (T1): pressionar seta BAIXO seleciona o botão "GALERIA" e ENTER abre
- Na tela de conclusão (T5): pressionar seta BAIXO seleciona "VER GALERIA" e ENTER abre

**Navegação interna — 3 níveis:**

| Nível | Conteúdo | Controles |
|-------|----------|-----------|
| 1 — Lista de exames | Cards "Exame DD-MM-AA - HH:MM" com nº de análises | Cima/Baixo navega · ENTER abre · Esquerda volta |
| 2 — Lista de análises | "Analise 01", "Analise 02"... com resultado e confiança em % | Cima/Baixo navega · ENTER abre imagem · Esquerda volta |
| 3 — Visualização | Imagem com marcações YOLO, resultado em % no topo | Cima/Baixo troca imagem · Esquerda volta |

A tela lê diretamente do sistema de arquivos (pasta `capturas_analisadas_voluntarios/`),
sem banco de dados. Ordenação: mais recente primeiro.

---

#### 4. Ajustes em telas existentes

**T1 (Splash):**
- Adicionado botão "GALERIA" abaixo do "INICIAR", acessível com seta BAIXO
- Seta CIMA retorna a seleção para "INICIAR"
- ENTER confirma a opção selecionada

**T5 (Exame Concluído):**
- Removido botão único decorativo (era state="disabled", não interativo)
- Adicionados dois botões funcionais: "NOVO EXAME" (verde) e "VER GALERIA" (roxo)
- Seta CIMA/BAIXO alterna entre eles; ENTER confirma

**T3 (Revisão + Feed):**
- Ao entrar nesta tela, o sistema verifica se a câmera está ativa e a reinicia
  automaticamente se necessário (pois T4b a para durante a análise YOLO)

---

### Arquivos Modificados

| Arquivo | Tipo de alteração |
|---------|-------------------|
| `app/backend.py` | Modificado — nova lógica de callbacks, subpastas, JSON, galeria |
| `app/ui.py` | Modificado — novas telas T4b e Galeria; atualização de T1, T3, T5 |

Nenhum arquivo de configuração (`main.py`), serviço (`visualdetect.service`) ou
script de instalação foi alterado. A pasta de capturas brutas permanece inalterada.

---

### Fluxo de Uso Atualizado

```
[LIGAMENTO]
     |
  Loading -> T0 -> T1 ─────────────────────────────────── GALERIA <────┐
               |  (ENTER: INICIAR)                          ^            │
               |  (BAIXO + ENTER: GALERIA) ────────────────┘            │
              T2 (configuração) -> T3 (revisão/câmera) -> T4 (captura)  │
                                         ^                   |           │
                                         |           (fotos concluídas) │
                                   reinicia câmera           |           │
                                                           T4b (YOLO)   │
                                                             |           │
                                                     (análise concluída) │
                                                            T5 ──────────┘
                                                             |  (BAIXO: VER GALERIA)
                                                      (ENTER: NOVO EXAME)
                                                            T1
```

---

### Observações para Próximas Iterações

- A Galeria exibe apenas imagens já analisadas pelo YOLO. Imagens da pasta de capturas
  brutas (`capturas_voluntarios_analisar/`) não são visualizáveis por ela.
- O atraso de 400ms no backend (para garantir que T4b esteja ativa antes do YOLO iniciar)
  funciona adequadamente, mas poderia ser substituído por `threading.Event` em iterações
  futuras para maior robustez em sistemas com carga de inicialização variável.
- A Galeria carrega todas as imagens de uma vez ao abrir; para volumes muito grandes de
  exames (dezenas), considerar paginação futuramente.

---

*Registro encerrado em 03/08/2026 às 14:37*  
*VisualDetect v1.1 — SENAI / NUDEP — 2026*
