# Caderno de Campo - VisualDetect

**Data:** 22 de setembro de 2026  
**Responsáveis:** Yuri Mendes  
**Instituição:** SENAI / NUDEP - Curso Técnico em Desenvolvimento de Sistemas  
**Sessão:** Documentação Técnica & Guia do Usuário

---

## Registro de Alterações - Documentação v1.1

### Contexto e Motivação

Após a implementação bem-sucedida do suporte a displays sensíveis ao toque (`TOUCH_MODE`) e as evoluções na interface gráfica do **VisualDetect**, tornou-se imprescindível atualizar a documentação do projeto. O objetivo desta sessão foi garantir que tanto o manual técnico (voltado a desenvolvedores e mantenedores) quanto o guia do usuário final refletissem com precisão o estado atual do software e hardware.

Havia defasagens na documentação em relação:
- À nova paleta de cores.
- Aos atalhos globais de teclado (F11 e ESC).
- Às lógicas de navegação alteradas (ex: Galeria nível 3, retorno de Novo Exame para Tela 1).
- Ao comportamento do feed da câmera (agora parado durante a análise YOLO para economizar recursos).
- Ao index padrão da câmera, que mudou para `0`.
- À correta operação em telas touch screen vs. operação via HID.

---

### Alterações Realizadas

#### 1. Atualização do `MANUAL_TECNICO.md`

O Manual Técnico foi promovido para a versão **1.1**, recebendo extensas revisões para alinhar-se com a base de código atual:

*   **Paleta de Cores Atualizada:** Foram documentados 8 novos tokens inseridos no `ui.py` (`green_dark`, `purple_light`, `btn_off`, `btn_off_border`, `bg_field`, `black`, `transparent`).
*   **Gestão de Câmera:** Documentado que `CameraManager.start()` agora utiliza `index=0` como padrão. Foi destacada a parada automática da câmera na tela T4b (análise) para reduzir o consumo de CPU.
*   **Feedback de Interface:** A documentação da tela T4 agora reflete a existência da barra de tempo, contador regressivo e feed ao vivo. A tela T4b documenta o novo spinner visual. A tela T5 documenta a exibição de `last_analyzed_folder`.
*   **Fluxo de Navegação:** Registrado que a ação "Novo Exame" na tela T5 retorna à T1, não mais à T2. Adicionados detalhes sobre a navegação na Galeria nível 3 (botões e atalhos).
*   **Modo Touchscreen (Seção 15):** Uma nova seção dedicada foi criada detalhando o impacto de `TOUCH_MODE = True` tela a tela, facilitando o entendimento de como a interface se adapta dinamicamente e os impactos no uso do controlador HID.
*   **Ambiente e Dependências:** Atualizada a contagem de linhas do `ui.py` para 1697. Registrado que o `requirements_rpi.txt` agora possui versões fixas de dependências para garantir estabilidade no Raspberry Pi.
*   **Atalhos Globais:** Adicionada documentação para as teclas F11 (Fullscreen) e ESC.

#### 2. Revisão do `GUIA_USUARIO_FINAL.md`

O Guia do Usuário Final foi completamente revisado, visando clareza e precisão para operadores não técnicos:

*   **Modelos de Interação:** Reestruturada a seção de introdução para explicar claramente que o equipamento pode ser operado via toque (Touchscreen) ou através do controle físico (HID) de 5 botões. Todos os passos práticos agora descrevem a ação primária como um "toque".
*   **Transparência durante a Captura (T4):** O passo 5 foi enriquecido para tranquilizar o usuário sobre os elementos visuais na tela (contador e barra de progresso) e reforçar que a câmera continua exibindo o paciente ao vivo.
*   **Análise em Background (T4b):** Adicionada explicação no passo 6 de que a tela apaga a imagem da câmera propositalmente durante o processamento para não alarmar o operador.
*   **Galeria e Navegação:** Detalhada a navegação na galeria, especialmente o uso dos novos botões **◀ ANTERIOR** e **PRÓXIMO ▶** para visualizar as imagens analisadas de um exame.
*   **FAQ Atualizado:** Novas perguntas e respostas abordam o comportamento da câmera durante a análise e a volta ao Menu Principal após um exame. O glossário também recebeu termos como "TOUCH_MODE" e "Feed ao vivo".

---

### Testes e Validação

1.  **Revisão Cruzada:** Os documentos gerados foram lidos para garantir que as alterações no `ui.py` (especialmente linhas como `_bar_time`, `_lbl_next` e controle do cv2) estão descritas no manual técnico.
2.  **Verificação de Formatação:** A formatação Markdown (tabelas, alertas do GitHub e diagramas Mermaid) foi validada.

---

### Procedimento de Commit

Os seguintes arquivos estão sendo enviados neste commit:

*   `docs/dev/MANUAL_TECNICO.md` (Atualizado)
*   `docs/user_guide/GUIA_USUARIO_FINAL.md` (Atualizado)
*   `docs/dev/CADERNO_CAMPO_22-09-2026.md` (Novo - este arquivo)

---

### Próximos Passos

*   [ ] Realizar testes de usabilidade com a documentação atualizada para garantir que o fluxo de touch screen está intuitivo para um usuário final de primeira viagem.
*   [ ] Verificar se é necessário exportar uma versão em PDF do Guia do Usuário Final para anexar fisicamente ao equipamento ou embalagem.
