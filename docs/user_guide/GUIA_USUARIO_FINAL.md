# Guia do Usuário — VisualDetect

> **Equipamento de Triagem do Reflexo Ocular**
> SENAI / NUDEP — 2026

---

> [!CAUTION]
> **Aviso Médico Importante**
> O VisualDetect é uma ferramenta de **triagem**. Os resultados devem **sempre** ser avaliados por um médico oftalmologista. Este equipamento **não substitui diagnóstico médico**.

---

## Índice

1. [O que é o VisualDetect?](#1-o-que-é-o-visualdetect)
2. [O que você vai precisar](#2-o-que-você-vai-precisar)
3. [Como operar o equipamento](#3-como-operar-o-equipamento)
4. [Início Rápido — 3 Passos](#4-início-rápido--3-passos)
5. [Passo a Passo Completo](#5-passo-a-passo-completo)
   - [Passo 1 — Ligar o equipamento](#passo-1--ligar-o-equipamento)
   - [Passo 2 — Tela inicial](#passo-2--tela-inicial)
   - [Passo 3 — Configurar o exame](#passo-3--configurar-o-exame)
   - [Passo 4 — Revisar e posicionar o paciente](#passo-4--revisar-e-posicionar-o-paciente)
   - [Passo 5 — Realizar o exame](#passo-5--realizar-o-exame)
   - [Passo 6 — Aguardar a análise](#passo-6--aguardar-a-análise)
   - [Passo 7 — Exame concluído](#passo-7--exame-concluído)
6. [Como Acessar a Galeria de Exames](#6-como-acessar-a-galeria-de-exames)
7. [Dicas para um Bom Exame](#7-dicas-para-um-bom-exame)
8. [Perguntas Frequentes](#8-perguntas-frequentes)
9. [O que fazer em caso de problema](#9-o-que-fazer-em-caso-de-problema)
10. [Glossário](#10-glossário)

---

## 1. O que é o VisualDetect?

O **VisualDetect** é um equipamento de triagem desenvolvido para auxiliar na detecção precoce do **Retinoblastoma** — um tipo de tumor ocular que afeta principalmente crianças pequenas.

O equipamento fotografa o olho do paciente durante um exame rápido e, em seguida, analisa automaticamente cada imagem usando inteligência artificial, identificando padrões que podem indicar a presença do tumor.

### Como funciona em resumo

```
1. Você configura o exame (quantidade de fotos e tempo)
2. Posiciona o paciente na frente da câmera
3. Pressiona INICIAR — o equipamento fotografa sozinho
4. O equipamento analisa as imagens automaticamente
5. Os resultados ficam salvos na Galeria para consulta
```

---

## 2. O que você vai precisar

| Item | Descrição |
|------|-----------|
| **Equipamento VisualDetect** | Caixa com Raspberry Pi, tela touchscreen e câmera acoplada |
| **Fonte de alimentação** | Cabo USB-C fornecido com o equipamento |
| **Controle** | Tela touchscreen (toque nos botões) ou teclado com 5 botões físicos — dependendo da configuração do equipamento |
| **Ambiente** | Local com iluminação ambiente adequada (nem muito escuro, nem muito claro) |

---

## 3. Como operar o equipamento

O equipamento pode funcionar em dois modos, dependendo de como foi configurado:

### Modo Touchscreen (padrão atual)

Toque diretamente nos botões exibidos na tela. Todos os botões são clicáveis e respondem ao toque.

### Modo HID — 5 Botões Físicos

Se o equipamento tiver um controle com 5 botões físicos:

| Botão | Símbolo | O que faz |
|-------|---------|-----------|
| **Esquerda** | `←` | Voltar à tela anterior · cancelar · selecionar opção da esquerda |
| **Direita** | `→` | Avançar · selecionar opção da direita |
| **Cima** | `↑` | Aumentar um número · mover para cima em uma lista |
| **Baixo** | `↓` | Diminuir um número · mover para baixo em uma lista |
| **Confirmar** | `ENTER` | Confirmar a seleção atual · avançar para a próxima tela |

> **Dica:** Em dúvida, toque em `←` (ou pressione o botão Esquerda) para voltar, ou toque em `ENTER` para confirmar.

---

## 4. Início Rápido — 3 Passos

> Para quem já conhece o equipamento:

```
1. Ligue e aguarde a tela inicial (~30–60 segundos)
2. Toque em INICIAR → ajuste capturas e tempo → CONFIRMAR → INICIAR
3. Posicione o paciente → aguarde o exame terminar automaticamente
```

---

## 5. Passo a Passo Completo

### Passo 1 — Ligar o equipamento

Conecte o cabo de alimentação ao equipamento. A tela acende e exibe a mensagem **"Carregando modelo..."** com uma barra animada.

> ⏳ Aguarde de **30 a 60 segundos** enquanto o sistema inicializa. Não toque na tela neste momento.

Quando aparecer **"Pronto!"** na tela, o equipamento avança automaticamente.

---

### Passo 2 — Tela inicial

Após o carregamento, você verá a tela de créditos com os nomes dos autores.

![T0 - Créditos](../interface/T0%20-%20Desenvolvedores.jpeg)

Toque em **CONTINUAR** (ou pressione `ENTER` no controle físico) para ir ao **menu principal**.

![T1 - Menu Principal](../interface/T1%20-%20Tela%20inicial.jpeg)

No menu principal, você tem duas opções:

| Opção | O que faz | Como selecionar |
|-------|-----------|-----------------|
| **INICIAR** | Começar um novo exame | Toque no botão verde **INICIAR** |
| **GALERIA** | Ver exames anteriores | Toque no botão roxo **GALERIA** |

Para um novo exame, toque em **INICIAR**.

---

### Passo 3 — Configurar o exame

O equipamento vai pedir duas informações antes de iniciar:

#### 3a. Número de capturas

![T2 - Número de capturas](../interface/T2%20-%20Sela%C3%A7%C3%A3o%20de%20numero%20de%20imagens.jpeg)

Use os botões `−` e `+` (ou `↑` / `↓` no controle físico) para ajustar o **número de fotos** que serão tiradas durante o exame.

| Número | Quando usar |
|--------|-------------|
| **5–10** | Exames rápidos, triagem inicial |
| **15–20** | Maior cobertura, melhor para análise detalhada |
| **30–50** | Análise extensa (exame mais longo) |

Toque em **PRÓXIMO** (ou pressione `ENTER`) para confirmar e avançar.

#### 3b. Tempo total do exame

![T2.1 - Tempo total](../interface/T2.1%20-%20Sele%C3%A7%C3%A3o%20de%20tempo%20total.jpeg)

Use os botões `−` e `+` (ou `↑` / `↓`) para ajustar o **tempo total em segundos** do exame.

| Tempo | Quando usar |
|-------|-------------|
| **5–15 s** | Pacientes que cooperam bem |
| **20–40 s** | Tempo padrão recomendado |
| **60–120 s** | Pacientes que precisam de mais tempo |

> O equipamento calculará automaticamente o intervalo entre as fotos.
> Exemplo: 10 fotos em 20 segundos = 1 foto a cada 2 segundos.

Toque em **CONFIRMAR** (ou pressione `ENTER`) para confirmar.

---

### Passo 4 — Revisar e posicionar o paciente

![T3 - Revisão pré-exame](../interface/T3%20-%20Tela%20de%20inform%C3%A7%C3%B5es%20pr%C3%A9-exame.jpeg)

Esta tela mostra o resumo da configuração e a **imagem ao vivo da câmera**.

Use a imagem ao vivo para verificar se o paciente está bem posicionado:

- ✅ Olho centralizado na câmera
- ✅ Distância adequada (câmera a ~30–50 cm do olho)
- ✅ Iluminação uniforme — evite reflexos fortes
- ✅ Paciente olhando diretamente para a câmera

| Ação | Toque | Controle físico |
|------|-------|-----------------|
| Voltar para ajustar configuração | Botão **← VOLTAR** | `←` → `ENTER` |
| Iniciar o exame | Botão **INICIAR →** | `→` → `ENTER` |

---

### Passo 5 — Realizar o exame

![T4 - Capturando 0%](../interface/T4%20-%20Tela%20duerante%20o%20exame%20(0%25).jpeg)

Após pressionar INICIAR, o exame começa automaticamente.

- A barra de progresso mostra quantas fotos já foram tiradas
- O contador de tempo mostra quanto do exame já passou
- O label "Próxima captura em: X.X s" indica quando a próxima foto será tirada
- A câmera continua mostrando o feed ao vivo durante todo o exame
- **Não toque na tela** durante o exame — todos os controles estão bloqueados
- Oriente o paciente a **manter o olho aberto e olhar para a câmera**

![T4 - Capturando ~50%](../interface/T4%20-%20Tela%20durante%20o%20exame%20(~50%25).jpeg)

![T4 - Capturando ~100%](../interface/T4%20-%20Tela%20durante%20o%20exame%20(~100%25).jpeg)

Quando a barra chega a 100%, a captura está concluída e o equipamento avança automaticamente para a análise.

---

### Passo 6 — Aguardar a análise

![T4b - Analisando 0%](../interface/T5%20-%20Tela%20de%20analise%20das%20capturas(0%25).jpeg)

Após a captura, o equipamento analisa cada imagem automaticamente usando inteligência artificial.

- **Não toque na tela** durante a análise
- O tempo de análise depende do número de fotos (geralmente 15–60 segundos)
- A barra de progresso e o nome do arquivo atual mostram o andamento
- A câmera é **desligada** neste momento para que o processador foque na análise

![T4b - Analisando 100%](../interface/T5%20-%20Tela%20de%20analise%20das%20capturas(100%25).jpeg)

---

### Passo 7 — Exame concluído

![T5 - Exame concluído](../interface/T6%20-%20Tela%20de%20exame%20concluido.jpeg)

O exame está concluído! As imagens analisadas ficam **salvas automaticamente** na Galeria com a data e hora do exame. O nome da pasta do exame é exibido na tela para confirmação.

Você tem duas opções:

| Opção | O que faz | Como selecionar |
|-------|-----------|-----------------|
| **NOVO EXAME** | Voltar ao menu principal para fazer um novo exame | Toque no botão **NOVO EXAME** |
| **VER GALERIA** | Abrir a galeria para ver os resultados | Toque no botão **VER GALERIA** |

---

## 6. Como Acessar a Galeria de Exames

A galeria guarda todos os exames realizados, organizados por data e hora.

### Acessar pelo menu principal

Na **tela inicial (T1)**, toque em **GALERIA**.

### Navegando pela galeria

**Nível 1 — Lista de exames:**

![Galeria - Lista de exames](../interface/T7%20-%20Tela%20galeria%20sele%C3%A7%C3%A3o%20de%20exame.jpeg)

Toque em um exame para abri-lo (o mais recente aparece primeiro). No modo com controle físico, use `↑` e `↓` para navegar e `ENTER` para abrir.

**Nível 2 — Fotos do exame:**

![Galeria - Fotos do exame](../interface/T8%20-%20tela%20galeria%20sele%C3%A7%C3%A3o%20de%20captura.jpeg)

Toque em uma foto analisada para visualizá-la com mais detalhes. Cada linha mostra o resultado da IA (ex.: "NORMAL 93.2%").

**Nível 3 — Visualização da imagem:**

Ao abrir uma imagem, você verá a foto com marcações coloridas (bounding boxes) desenhadas pela inteligência artificial.

- Toque em **◀ ANTERIOR** ou **PRÓXIMO ▶** para navegar entre as imagens do exame
- Toque em **← VOLTAR** no topo para voltar à lista

**Para voltar:** Toque no botão **← VOLTAR** no topo da tela em qualquer nível.

### Entendendo os resultados

Ao abrir uma imagem na galeria, você verá a foto com marcações coloridas (bounding boxes) desenhadas pela inteligência artificial, indicando o que foi detectado em cada região do olho. A confiança (%) indica o quanto o sistema está certo da detecção.

> ⚠️ **Lembre-se:** Os resultados da IA são indicativos. Sempre consulte um médico oftalmologista para interpretação e diagnóstico.

---

## 7. Dicas para um Bom Exame

### Posicionamento do paciente

- Peça ao paciente para sentar confortavelmente em frente ao equipamento
- O olho deve estar centralizado na câmera, a **30–50 cm** de distância
- Use o feed ao vivo da câmera (tela T3) para verificar o posicionamento antes de iniciar
- Peça para olhar **diretamente para a câmera** durante todo o exame
- Para crianças pequenas, um familiar pode ajudar a manter o posicionamento

### Iluminação

- Prefira ambientes com iluminação **suave e uniforme**
- Evite luz solar direta sobre o paciente ou a câmera
- Evite reflexos fortes na tela ou na câmera

### Durante o exame

- Peça ao paciente para **não piscar com frequência** durante o exame
- Se o paciente precisar piscar, está tudo bem — o equipamento tira múltiplas fotos
- Em caso de movimento excessivo, aguarde o término e refaça o exame

### Configurações recomendadas para diferentes perfis

| Perfil | Nº de capturas | Tempo total |
|--------|---------------|-------------|
| Criança cooperativa (>5 anos) | 10 | 20 s |
| Criança pequena (<5 anos) | 15 | 30 s |
| Adulto | 10 | 15 s |
| Paciente com dificuldade de fixação | 20 | 60 s |

---

## 8. Perguntas Frequentes

**P: Quanto tempo leva um exame completo?**
R: O tempo total inclui a captura + a análise. Uma configuração típica (10 fotos em 20 s) leva aproximadamente 1–2 minutos no total.

**P: Posso interromper o exame no meio?**
R: Durante a captura (T4) e a análise (T4b), os controles estão bloqueados por segurança. Aguarde o término ou desligue e religue o equipamento se necessário.

**P: Os dados ficam salvos se o equipamento desligar?**
R: Sim. Todos os exames concluídos são salvos automaticamente no armazenamento interno e ficam disponíveis na Galeria mesmo após reinicializações.

**P: Posso examinar os dois olhos?**
R: Sim. Realize um exame para cada olho separadamente. Cada exame fica registrado na galeria com data e hora próprias.

**P: O equipamento substitui uma consulta oftalmológica?**
R: **Não.** O VisualDetect é uma ferramenta de triagem para identificar suspeitas. O diagnóstico final deve sempre ser feito por um médico oftalmologista.

**P: O que significa quando a análise não detecta nada?**
R: Uma lista de detecções vazia pode indicar ausência de anomalias ou que a imagem não tinha qualidade suficiente. Sempre considere o contexto clínico e consulte um especialista.

**P: A câmera apaga durante a análise — isso é normal?**
R: Sim. O feed da câmera é desligado automaticamente durante a análise das imagens (tela T4b) para que o processador possa se dedicar completamente à análise. Ela volta a funcionar quando você acessar a tela de revisão (T3) em um novo exame.

**P: Após "NOVO EXAME", fui para o menu principal — isso é correto?**
R: Sim. A partir da versão 1.1, "NOVO EXAME" retorna ao menu principal (T1) para que você possa escolher entre iniciar um novo exame ou acessar a galeria.

---

## 9. O que fazer em caso de problema

### Tela preta ou equipamento não liga

1. Verifique se o cabo de alimentação está conectado corretamente
2. Aguarde 60 segundos — o sistema pode estar inicializando
3. Desligue e religue o equipamento

### Câmera não aparece na tela de revisão (T3)

1. Verifique se a câmera USB está conectada ao equipamento
2. Desligue e religue o equipamento
3. Se o problema persistir, contate o suporte técnico

### A análise parece muito lenta

- A análise de imagens é um processo que exige processamento — é normal levar alguns segundos por imagem
- Não desligue o equipamento durante a análise

### O equipamento travou (tela parada, botões não respondem)

1. Aguarde 2 minutos — o sistema pode estar processando
2. Se não houver resposta, desligue e religue o equipamento
3. Os exames já concluídos antes do problema estarão disponíveis na galeria normalmente

### Contato para suporte técnico

Em caso de problemas não resolvidos pelos passos acima, entre em contato com a equipe técnica do SENAI / NUDEP responsável pelo equipamento.

---

## 10. Glossário

| Termo | Significado |
|-------|-------------|
| **Triagem** | Exame inicial para identificar casos que precisam de investigação mais aprofundada |
| **Retinoblastoma** | Tumor maligno da retina, mais comum em crianças |
| **YOLO** | Algoritmo de inteligência artificial usado para detectar padrões nas imagens |
| **Bounding box** | Caixa colorida desenhada sobre a imagem indicando o que a IA detectou |
| **Confiança** | Porcentagem que indica o quão certo o sistema está de uma detecção |
| **Galeria** | Biblioteca com todos os exames realizados, organizados por data e hora |
| **HID** | Protocolo que permite ao controle físico se comunicar com o equipamento como um teclado |
| **Raspberry Pi** | Computador de placa única usado como cérebro do equipamento |
| **TOUCH_MODE** | Configuração interna que ativa a navegação por toque na tela |
| **Feed ao vivo** | Imagem em tempo real da câmera exibida nas telas T3 e T4 |

---

*VisualDetect — SENAI / NUDEP · Setembro 2026*
*Para dúvidas técnicas, consulte o [Manual Técnico](../dev/MANUAL_TECNICO.md).*
