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
3. [Os 5 Botões de Controle](#3-os-5-botões-de-controle)
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
| **Equipamento VisualDetect** | Caixa com Raspberry Pi, tela e câmera acoplada |
| **Fonte de alimentação** | Cabo USB-C fornecido com o equipamento |
| **Controle físico** | Teclado com 5 botões (← → ↑ ↓ ENTER) — já conectado ao equipamento |
| **Ambiente** | Local com iluminação ambiente adequada (nem muito escuro, nem muito claro) |

---

## 3. Os 5 Botões de Controle

O equipamento é operado exclusivamente por **5 botões físicos**. Aprenda uma vez e use sempre:

| Botão | Símbolo | O que faz |
|-------|---------|-----------|
| **Esquerda** | `←` | Voltar à tela anterior · cancelar · selecionar opção da esquerda |
| **Direita** | `→` | Avançar · selecionar opção da direita |
| **Cima** | `↑` | Aumentar um número · mover para cima em uma lista · selecionar opção de cima |
| **Baixo** | `↓` | Diminuir um número · mover para baixo em uma lista · selecionar opção de baixo |
| **Confirmar** | `ENTER` | Confirmar a seleção atual · avançar para a próxima tela |

> **Dica:** Quando estiver em dúvida, pressione `←` para voltar ou `ENTER` para confirmar.

---

## 4. Início Rápido — 3 Passos

> Para quem já conhece o equipamento:

```
1. Ligue e aguarde a tela inicial (~30–60 segundos)
2. ENTER → configure com ↑ ↓ → ENTER → ENTER → INICIAR → ENTER
3. Posicione o paciente → aguarde o exame terminar automaticamente
```

---

## 5. Passo a Passo Completo

### Passo 1 — Ligar o equipamento

Conecte o cabo de alimentação ao equipamento. A tela acende e exibe a mensagem **"Carregando modelo..."** com uma barra animada.

> ⏳ Aguarde de **30 a 60 segundos** enquanto o sistema inicializa. Não pressione nenhum botão neste momento.

Quando aparecer **"Pronto!"** na tela, o equipamento avança automaticamente.

---

### Passo 2 — Tela inicial

Após o carregamento, você verá a tela de créditos com os nomes dos autores.

![T0 - Créditos](../interface/T0%20-%20Desenvolvedores.jpeg)

Pressione `ENTER` para continuar para o **menu principal**.

![T1 - Menu Principal](../interface/T1%20-%20Tela%20inicial.jpeg)

No menu principal, você tem duas opções:

| Opção | O que faz | Como selecionar |
|-------|-----------|-----------------|
| **INICIAR** | Começar um novo exame | `↑` para destacar em verde → `ENTER` |
| **GALERIA** | Ver exames anteriores | `↓` para destacar em roxo → `ENTER` |

Para um novo exame, pressione `ENTER` com **INICIAR** destacado (verde).

---

### Passo 3 — Configurar o exame

O equipamento vai pedir duas informações antes de iniciar:

#### 3a. Número de capturas

![T2 - Número de capturas](../interface/T2%20-%20Sela%C3%A7%C3%A3o%20de%20numero%20de%20imagens.jpeg)

Use `↑` e `↓` para ajustar o **número de fotos** que serão tiradas durante o exame.

| Número | Quando usar |
|--------|-------------|
| **5–10** | Exames rápidos, triagem inicial |
| **15–20** | Maior cobertura, melhor para análise detalhada |
| **30–50** | Análise extensa (exame mais longo) |

Pressione `ENTER` para confirmar e avançar.

#### 3b. Tempo total do exame

![T2.1 - Tempo total](../interface/T2.1%20-%20Sele%C3%A7%C3%A3o%20de%20tempo%20total.jpeg)

Use `↑` e `↓` para ajustar o **tempo total em segundos** do exame.

| Tempo | Quando usar |
|-------|-------------|
| **5–15 s** | Pacientes que cooperam bem |
| **20–40 s** | Tempo padrão recomendado |
| **60–120 s** | Pacientes que precisam de mais tempo |

> O equipamento calculará automaticamente o intervalo entre as fotos.
> Exemplo: 10 fotos em 20 segundos = 1 foto a cada 2 segundos.

Pressione `ENTER` para confirmar.

---

### Passo 4 — Revisar e posicionar o paciente

![T3 - Revisão pré-exame](../interface/T3%20-%20Tela%20de%20inform%C3%A7%C3%B5es%20pr%C3%A9-exame.jpeg)

Esta tela mostra o resumo da configuração e a **imagem ao vivo da câmera**.

Use a imagem ao vivo para verificar se o paciente está bem posicionado:

- ✅ Olho centralizado na câmera
- ✅ Distância adequada (câmera a ~30–50 cm do olho)
- ✅ Iluminação uniforme — evite reflexos fortes
- ✅ Paciente olhando diretamente para a câmera

| Botão | Ação |
|-------|------|
| `←` → seleciona **VOLTAR** → `ENTER` | Volta para ajustar a configuração |
| `→` → seleciona **INICIAR** → `ENTER` | Inicia o exame |

---

### Passo 5 — Realizar o exame

![T4 - Capturando 0%](../interface/T4%20-%20Tela%20duerante%20o%20exame%20(0%25).jpeg)

Após pressionar INICIAR, o exame começa automaticamente.

- A barra de progresso mostra quantas fotos já foram tiradas
- **Não pressione nenhum botão** durante o exame — todos estão bloqueados
- Oriente o paciente a **manter o olho aberto e olhar para a câmera**

![T4 - Capturando ~50%](../interface/T4%20-%20Tela%20durante%20o%20exame%20(~50%25).jpeg)

![T4 - Capturando ~100%](../interface/T4%20-%20Tela%20durante%20o%20exame%20(~100%25).jpeg)

Quando a barra chega a 100%, a captura está concluída e o equipamento avança automaticamente para a análise.

---

### Passo 6 — Aguardar a análise

![T4b - Analisando 0%](../interface/T5%20-%20Tela%20de%20analise%20das%20capturas(0%25).jpeg)

Após a captura, o equipamento analisa cada imagem automaticamente usando inteligência artificial.

- **Não pressione nenhum botão** durante a análise
- O tempo de análise depende do número de fotos (geralmente 15–60 segundos)
- A barra de progresso mostra quantas imagens já foram processadas

![T4b - Analisando 100%](../interface/T5%20-%20Tela%20de%20analise%20das%20capturas(100%25).jpeg)

---

### Passo 7 — Exame concluído

![T5 - Exame concluído](../interface/T6%20-%20Tela%20de%20exame%20concluido.jpeg)

O exame está concluído! As imagens analisadas ficam **salvas automaticamente** na Galeria com a data e hora do exame.

Você tem duas opções:

| Opção | O que faz | Como selecionar |
|-------|-----------|-----------------|
| **NOVO EXAME** | Voltar para a configuração e fazer um novo exame | `←` → `ENTER` |
| **VER GALERIA** | Abrir a galeria para ver os resultados | `→` → `ENTER` |

---

## 6. Como Acessar a Galeria de Exames

A galeria guarda todos os exames realizados, organizados por data e hora.

### Acessar pelo menu principal

Na **tela inicial (T1)**, pressione `↓` para destacar **GALERIA** e depois `ENTER`.

### Navegando pela galeria

**Nível 1 — Lista de exames:**

![Galeria - Lista de exames](../interface/T7%20-%20Tela%20galeria%20sele%C3%A7%C3%A3o%20de%20exame.jpeg)

Use `↑` e `↓` para navegar entre os exames (o mais recente aparece primeiro). Pressione `ENTER` para abrir um exame.

**Nível 2 — Fotos do exame:**

![Galeria - Fotos do exame](../interface/T8%20-%20tela%20galeria%20sele%C3%A7%C3%A3o%20de%20captura.jpeg)

Use `↑` e `↓` para navegar entre as fotos analisadas. Pressione `ENTER` para ver uma foto com mais detalhes e os resultados da análise.

**Para voltar:** Pressione `←` em qualquer nível para retornar ao nível anterior.

### Entendendo os resultados

Ao abrir uma imagem na galeria, você verá a foto com marcações coloridas (bounding boxes) desenhadas pela inteligência artificial, indicando o que foi detectado em cada região do olho.

> ⚠️ **Lembre-se:** Os resultados da IA são indicativos. Sempre consulte um médico oftalmologista para interpretação e diagnóstico.

---

## 7. Dicas para um Bom Exame

### Posicionamento do paciente

- Peça ao paciente para sentar confortavelmente em frente ao equipamento
- O olho deve estar centralizado na câmera, a **30–50 cm** de distância
- Peça para olhar **diretamente para a câmera** durante todo o exame
- Para crianças pequenas, um familiar pode ajudar a manter o posicionamento

### Iluminação

- Prefira ambientes com iluminação **suave e uniforme**
- Evite luz solar direta sobre o paciente ou a câmera
- Evite reflexos fortes na tela ou na câmera

### Durante o exame

- Peça ao paciente para **não piscar com frequência** durante o exame
- Se o paciente precisar piscar, está tudo bem — o equipamento tira múltiplas fotos
- Em caso de movimento excessivo, cancele e refaça o exame

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
R: Durante a captura (T4) e a análise (T4b), os botões estão bloqueados por segurança. Aguarde o término ou desligue e religue o equipamento se necessário.

**P: Os dados ficam salvos se o equipamento desligar?**
R: Sim. Todos os exames concluídos são salvos automaticamente no armazenamento interno e ficam disponíveis na Galeria mesmo após reinicializações.

**P: Posso examinar os dois olhos?**
R: Sim. Realize um exame para cada olho separadamente. Cada exame fica registrado na galeria com data e hora próprias.

**P: O equipamento substitui uma consulta oftalmológica?**
R: **Não.** O VisualDetect é uma ferramenta de triagem para identificar suspeitas. O diagnóstico final deve sempre ser feito por um médico oftalmologista.

**P: O que significa quando a análise não detecta nada?**
R: Uma lista de detecções vazia pode indicar ausência de anomalias ou que a imagem não tinha qualidade suficiente. Sempre considere o contexto clínico e consulte um especialista.

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

---

*VisualDetect — SENAI / NUDEP · Setembro 2026*
*Para dúvidas técnicas, consulte o [Manual Técnico](../dev/MANUAL_TECNICO.md).*
