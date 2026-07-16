# VisualDetect — Guia do Usuário

**Equipamento de Triagem do Reflexo Ocular**  
SENAI / NUDEP — Curso Técnico em Desenvolvimento de Sistemas

---

## O que é o VisualDetect?

O **VisualDetect** é um equipamento de triagem desenvolvido para auxiliar na detecção precoce do
**Retinoblastoma** — um tipo de tumor ocular que afeta principalmente crianças.

O equipamento fotografa o olho do paciente e analisa automaticamente o reflexo pupilar,
identificando padrões que podem indicar a presença do tumor.

> ⚠️ **Importante:** O VisualDetect é uma ferramenta de **triagem**. O resultado deve ser
> sempre avaliado por um médico oftalmologista. Não substitui diagnóstico médico.

---

## O que você vai precisar

| Item | Descrição |
|------|-----------|
| Equipamento VisualDetect | Raspberry Pi com tela e câmera acoplada |
| Cabo de energia | Fonte USB-C do equipamento |
| Teclado de controle | Teclado físico com 5 botões (← → ↑ ↓ ENTER) |

---

## Como ligar o equipamento

1. Conecte o cabo de energia ao equipamento.
2. Aguarde a inicialização (pode levar cerca de **30 a 60 segundos**).
3. A tela acenderá automaticamente e o sistema iniciará.
4. Não é necessário apertar nenhum botão para ligar.

---

## Controles — Teclado físico

O equipamento é controlado por **5 botões físicos**:

| Botão | Símbolo | Função |
|-------|---------|--------|
| Esquerda | `←` | Voltar / Cancelar |
| Direita  | `→` | Selecionar próximo |
| Cima     | `↑` | Aumentar valor |
| Baixo    | `↓` | Diminuir valor |
| Confirmar | `ENTER` | Confirmar / Avançar |

---

## Fluxo completo de um exame

### Tela 1 — Carregando
Ao ligar o equipamento, uma barra de progresso indica que o sistema está carregando.
**Aguarde** — o sistema avança automaticamente quando estiver pronto.

---

### Tela 2 — Informações SENAI / NUDEP
Exibe as informações institucionais do projeto.

**→ Pressione `ENTER` para continuar.**

---

### Tela 3 — Tela Inicial (Splash)
Tela de boas-vindas com o logotipo do VisualDetect.

**→ Pressione `ENTER` para iniciar a configuração do exame.**

---

### Tela 4 — Configuração do Exame

Você configura **dois parâmetros** do exame, um de cada vez:

#### Passo 1 — Número de capturas
Define quantas fotos o equipamento vai tirar durante o exame.

- Pressione `↑` para **aumentar** o número de fotos.
- Pressione `↓` para **diminuir**.
- Pressione `ENTER` para confirmar e ir ao próximo passo.

> **Recomendado:** entre 8 e 15 fotos.

#### Passo 2 — Tempo total do exame
Define quantos segundos dura o exame no total.

- Pressione `↑` para **aumentar** o tempo.
- Pressione `↓` para **diminuir**.
- Pressione `ENTER` para confirmar.

> **Exemplo:** 10 fotos em 10 segundos = 1 foto por segundo.

**Para voltar ao passo anterior:** pressione `←`.

---

### Tela 5 — Revisão + Câmera ao vivo

Exibe um resumo das configurações e o **feed ao vivo da câmera**.

Use essa tela para **posicionar o paciente** corretamente na frente da câmera.

| Botão | Ação |
|-------|------|
| `→` | Selecionar **INICIAR** |
| `←` | Selecionar **VOLTAR** |
| `ENTER` | Confirmar a seleção |

**→ Posicione o paciente, selecione INICIAR e pressione `ENTER`.**

---

### Tela 6 — Capturando

O equipamento está fotografando. **Não mova o paciente durante esta tela.**

- A barra de progresso mostra quantas fotos já foram tiradas.
- O contador de tempo mostra quanto falta para o exame terminar.
- Os botões ficam **bloqueados** — o exame não pode ser interrompido.

Aguarde o equipamento concluir automaticamente.

---

### Tela 7 — Exame Concluído

Indica que o exame terminou e as fotos foram salvas e analisadas.

**→ Pressione `ENTER` para realizar um novo exame.**

---

## Onde ficam as fotos salvas?

Após cada exame, as imagens são salvas automaticamente no próprio equipamento, em duas pastas:

| Pasta | Conteúdo |
|-------|----------|
| `capturas_voluntarios_analisar/` | Fotos originais do exame |
| `capturas_analisadas_voluntarios/` | Fotos com marcações do sistema de IA |

O nome de cada arquivo inclui a data e hora do exame (ex: `20260716_151139_capture_1.jpg`).

> Para acessar as fotos, conecte um monitor e teclado ao equipamento
> ou transfira via rede (consulte o técnico responsável).

---

## Resultados da análise

O sistema detecta automaticamente dois padrões:

| Resultado | O que significa |
|-----------|----------------|
| **REFLEXO-NORMAL** | Reflexo pupilar dentro do padrão esperado |
| **REFLEXO-ANORMAL** | Padrão de reflexo diferente do normal — requer avaliação médica |
| **Nenhuma detecção** | O sistema não identificou o olho na foto — refaça o exame |

> ⚠️ Qualquer resultado **deve ser avaliado por um médico**. O sistema é uma ferramenta de auxílio.

---

## O que fazer em caso de erro

### A tela ficou preta / o equipamento não responde

1. Aguarde 1 minuto (o sistema pode estar carregando).
2. Se persistir, desligue o cabo de energia, aguarde 10 segundos e ligue novamente.

### A câmera não aparece (mensagem "Câmera não disponível")

1. Verifique se a câmera está bem conectada ao equipamento.
2. Desligue e religue o equipamento.
3. Se o problema continuar, acione o suporte técnico.

### O exame terminou mas poucas fotos foram tiradas

- Verifique se a câmera está conectada e apontada corretamente para o paciente.
- Repita o exame com o paciente posicionado centralmente na câmera.

### Qualquer outro erro

Anote a mensagem que apareceu na tela e acione o suporte técnico:  
**Yuri Mendes / Andrei Krug — SENAI NUDEP**

---

## Cuidados com o equipamento

- **Não desconecte** o cabo de energia durante um exame em andamento.
- **Não force** os botões físicos.
- Mantenha a **lente da câmera limpa** — use pano macio e seco.
- Guarde o equipamento em local **seco e arejado**.
- Não exponha à luz solar direta por longos períodos.

---

## Dúvidas?

Entre em contato com a equipe técnica responsável pelo equipamento.

---

*VisualDetect v1.0 — SENAI / NUDEP — 2026*  
*Projeto acadêmico — Curso Técnico em Desenvolvimento de Sistemas*
