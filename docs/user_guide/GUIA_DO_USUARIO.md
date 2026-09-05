# VisualDetect — Guia do Usuário

**Equipamento de Triagem do Reflexo Ocular**
SENAI / NUDEP — 2026

---

> ⚠️ **Aviso importante:** O VisualDetect é uma ferramenta de **triagem**.
> O resultado deve **sempre** ser avaliado por um médico oftalmologista.
> Este equipamento **não substitui diagnóstico médico**.

---

## Início Rápido — 3 Passos

> Para quem já conhece o equipamento:

```
1. Ligue o equipamento e aguarde a tela inicial aparecer (~30–60 segundos)
2. Pressione ENTER para iniciar → configure o exame com ↑ ↓ → pressione ENTER
3. Posicione o paciente → selecione INICIAR → pressione ENTER → aguarde o exame
```

---

## O que é o VisualDetect?

O **VisualDetect** é um equipamento de triagem desenvolvido para auxiliar na detecção precoce do
**Retinoblastoma** — um tipo de tumor ocular que afeta principalmente crianças.

O equipamento fotografa o olho do paciente e analisa automaticamente o reflexo pupilar,
identificando padrões que podem indicar a presença do tumor.

---

## O que você vai precisar

| Item | Descrição |
|---|---|
| Equipamento VisualDetect | Caixa com Raspberry Pi, tela e câmera acoplada |
| Fonte de alimentação | Cabo USB-C fornecido com o equipamento |
| Controle físico | Teclado com 5 botões (← → ↑ ↓ ENTER) — já conectado |

---

## Os 5 Botões de Controle

O equipamento é controlado por **5 botões físicos**. Aprenda uma vez e use sempre:

| Botão | Símbolo | O que faz |
|---|---|---|
| **Esquerda** | `←` | Voltar à tela anterior / cancelar / selecionar opção da esquerda |
| **Direita** | `→` | Avançar / selecionar opção da direita |
| **Cima** | `↑` | Aumentar um número / mover para cima em uma lista |
| **Baixo** | `↓` | Diminuir um número / mover para baixo em uma lista |
| **Confirmar** | `ENTER` | Confirmar a seleção atual / avançar para a próxima tela |

> **Dica:** Quando estiver em dúvida, pressione `ENTER` para confirmar
> ou `←` para voltar ao passo anterior.

---

## Passo a Passo — Realizando um Exame

### Passo 1 — Ligar o equipamento

1. Conecte o cabo de alimentação.
2. Aguarde entre **30 e 60 segundos** — o sistema está carregando a inteligência artificial.
3. Quando a tela de boas-vindas aparecer, o equipamento está pronto.

> Não é necessário apertar nenhum botão para ligar.
> A barra de progresso na tela indica que o sistema está inicializando.

---

### Passo 2 — Tela de Boas-Vindas

Você verá a tela inicial com o logotipo **VisualDetect** e duas opções:
- **INICIAR** — começa um novo exame
- **GALERIA** — acessa exames anteriores

**→ Pressione `ENTER` para iniciar um novo exame.**

---

### Passo 3 — Configurar o Exame

Você vai configurar dois parâmetros, um de cada vez:

#### Número de capturas

Define quantas fotos o equipamento vai tirar.

- `↑` para **aumentar** o número
- `↓` para **diminuir** o número
- `ENTER` para confirmar e ir ao próximo

> **Recomendado:** entre **8 e 15 fotos** por exame.

#### Tempo total do exame

Define quantos segundos dura o exame.

- `↑` para **aumentar** o tempo
- `↓` para **diminuir** o tempo
- `ENTER` para confirmar

> **Exemplo:** 10 fotos em 10 segundos = 1 foto por segundo.

**Para voltar ao passo anterior a qualquer momento:** pressione `←`

---

### Passo 4 — Posicionar o Paciente

Esta tela mostra um **resumo das configurações** e a **imagem ao vivo da câmera**.

1. Use o feed da câmera para posicionar o olho do paciente no centro da imagem.
2. Verifique se há iluminação adequada.
3. Quando estiver pronto:
   - `→` para selecionar **INICIAR**
   - `ENTER` para confirmar e iniciar o exame

> Se precisar ajustar as configurações, pressione `←` para **VOLTAR**.

---

### Passo 5 — Aguardar o Exame

O equipamento está fotografando. **Nesta tela:**

- ❌ **Não mova o paciente** — cada movimento pode prejudicar a captura
- ❌ **Não pressione os botões** — estão bloqueados durante o exame
- ✅ Aguarde — o equipamento avança automaticamente

A barra de progresso e o contador mostram quantas fotos já foram tiradas e quanto falta.

---

### Passo 6 — Análise Automática

Após as fotos, o sistema analisa automaticamente as imagens com IA.
Isso dura alguns segundos. **Aguarde.**

---

### Passo 7 — Exame Concluído

A tela mostra que o exame foi concluído e as imagens foram salvas.

Você tem duas opções:
- **NOVO EXAME** (`←` + `ENTER`) — inicia outro exame imediatamente
- **GALERIA** (`→` + `ENTER`) — vê os resultados do exame atual

---

## Entendendo os Resultados

As fotos analisadas ficam salvas no equipamento com marcações coloridas:

| Resultado na imagem | O que significa |
|---|---|
| **REFLEXO-NORMAL** | Reflexo pupilar dentro do padrão esperado |
| **REFLEXO-ANORMAL** | Padrão diferente do normal — encaminhar para avaliação médica |
| *(sem marcação)* | O sistema não identificou o olho na foto — refaça o exame |

> ⚠️ **Qualquer resultado deve ser avaliado por um médico.**
> Um resultado NORMAL não garante ausência de problema.
> Um resultado ANORMAL não confirma diagnóstico de Retinoblastoma.

---

## Usando a Galeria

A Galeria permite visualizar exames anteriores organizados por data:

| Botão | Ação |
|---|---|
| `↑` / `↓` | Navegar entre exames / imagens |
| `ENTER` | Abrir o exame ou a imagem selecionada |
| `←` | Voltar ao nível anterior |

---

## O que fazer em caso de problema

### A tela está preta / o equipamento não responde

1. Aguarde **2 minutos** — o sistema pode estar carregando.
2. Se persistir, desconecte o cabo de alimentação, aguarde 15 segundos e reconecte.

### A câmera não aparece na tela de posicionamento

1. Verifique se a câmera está bem conectada ao equipamento.
2. Desligue e religue o equipamento.
3. Se o problema continuar, acione o suporte técnico.

### O exame terminou, mas as fotos parecem borradas

- Certifique-se de que o paciente estava imóvel durante o exame.
- Verifique se a lente da câmera está limpa.
- Repita o exame.

### O controle físico (botões) não responde

1. Verifique se o cabo do controlador está conectado ao equipamento.
2. Tente pressionar os botões com mais firmeza.
3. Se não funcionar, acione o suporte técnico.

### Qualquer outro problema

Anote a mensagem que apareceu na tela e acione o suporte técnico:

**Yuri Mendes / Andrei Krug — SENAI NUDEP**

---

## Cuidados com o Equipamento

- **Não desconecte** o cabo de alimentação durante um exame em andamento
- **Não force** os botões físicos do controlador
- **Limpe a lente da câmera** regularmente com pano macio e seco (sem líquidos)
- Guarde o equipamento em local **seco, arejado e longe de luz solar direta**
- **Não exponha a impactos** — é um equipamento eletrônico sensível

---

## Onde ficam as fotos salvas?

As imagens são salvas automaticamente no próprio equipamento após cada exame:

| Pasta | Conteúdo |
|---|---|
| `capturas_voluntarios_analisar/` | Fotos originais do exame |
| `capturas_analisadas_voluntarios/` | Fotos com marcações da IA |

> Para acessar as fotos, conecte um monitor e teclado ao equipamento
> ou solicite ao suporte técnico a transferência dos arquivos.

---

*VisualDetect — SENAI / NUDEP — Projeto Técnico 2026*
*Curso Técnico em Desenvolvimento de Sistemas*
