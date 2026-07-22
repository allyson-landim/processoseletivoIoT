# Relatório Final do Candidato - Contador de Produção Não-Intrusivo

**Nome completo:** Allyson Andre Almeida de Castro Paes Landim  
**GitHub:** https://github.com/allyson-landim/processoseletivoIoT

---

## Visão Geral da Solução
O objetivo deste projeto é fornecer uma solução de baixo custo para contabilização de itens em linhas de montagem manuais ou semiautomáticas que operam sem a presença de Controladores Lógicos Programáveis (CLPs). 

O sistema embarcado monitora de forma não-intrusiva a passagem de produtos utilizando um sensor óptico. A interação acontece inteiramente através dos eventos físicos na esteira e de um botão manual, fornecendo logs em tempo real sobre a contagem de peças, detecção de micro-paradas operacionais e execução de resets manuais de turno.

---

## Arquitetura do Sistema Embarcado
A arquitetura de software baseia-se em um único *loop* principal implementado no arquivo `main.py` utilizando MicroPython.
* **Controle Não-Bloqueante:** Em vez de interrupções puras, o fluxo utiliza a diferença de tempo (`time.ticks_diff()`) para garantir que o microcontrolador execute suas checagens em altíssima velocidade sem ser travado por rotinas de espera.
* **Máquina de Estados de Sensores:** 
  * O sensor óptico opera gerenciando transições de estado: ele lê a queda na luminosidade (borda de descida) e só efetiva a contagem da peça no retorno à luminosidade ambiente (borda de subida), atestando que o objeto atravessou completamente a barreira de luz.
  * O temporizador de micro-paradas atua de forma concorrente, disparando o alerta caso o estado do sensor se mantenha no bloqueio por mais de 5 segundos.

---

## Componentes Utilizados na Simulação
A simulação no ambiente Wokwi foi estruturada no `diagram.json` contendo:
* **Microcontrolador ESP32 DevKit C v4:** Orquestrador principal da lógica e encarregado da telemetria e emissão de alertas via comunicação UART (Interface Serial).
* **Sensor Óptico (LDR - `ldr1`):** Responsável por ler a variação de luminosidade em *lux* (convertido para uma tensão analógica no GPIO 34).
* **Botão Físico (`btn1`):** Configurado no GPIO 32 operando em modo Pull-Up interno para o reset manual e assíncrono do turno.

---

## Decisões Técnicas Relevantes
* **Mapeamento Analógico do LDR:** Considerando o comportamento do divisor de tensão no módulo padrão do simulador, a lógica adotada inverteu a premissa digital convencional: considerou-se a obstrução (baixa de *lux*) como um aumento no nível de tensão recebido pelo ADC, aplicando um limiar de disparo (`LIMIAR_ADC`) confiável para filtrar ruídos.
* **Detecção de Borda (Release) no Reset:** Para atender aos testes de automação, a ação de zerar os contadores e gerar logs foi alocada exclusivamente na borda de subida (quando o operador *solta* o botão), garantindo que a execução contínua no loop não causasse falsos gatilhos de impressão.

---

## Resultados Obtidos
A simulação via Wokwi CI obteve aprovação plena em todos os cenários exigidos.
* **Contagem:** O hardware virtual atendeu estritamente à dinâmica de variação de luz (`lux: 800` -> `50` -> `800`), identificando as passagens sem leituras falsas.
* **Micro-paradas:** A manutenção do bloqueio de *lux* estourou o *timeout* planejado do projeto, imprimindo o log de alerta no tempo adequado.
* **Sincronia CI:** Não houve perda de pacotes ou interrupções parciais pelo emprego efetivo da rotina de código 100% não-bloqueante, entregando as strings exatas no terminal de comunicação.

---

## Comentários Adicionais (Opcional)
O maior desafio deste desenvolvimento foi alinhar o modelo mental de debounce mecânico com as características fechadas da esteira de integração contínua (CI). A transição inicial da variável de estado do botão provocou travamentos no `Timeout` da automação por disparos prematuros de log, o que reforçou o aprendizado em otimizar rotinas que atuem estritamente em bordas (Falling/Rising Edges) dentro de simulações com hardware virtual restrito.