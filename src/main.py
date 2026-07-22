import machine
import time

# ==========================================
# Configuração de Hardware
# ==========================================
# LDR no GPIO 34 com atenuação para leitura em toda a faixa (0-3.3V)
pino_ldr = machine.ADC(machine.Pin(34))
pino_ldr.atten(machine.ADC.ATTN_11DB) 

# Botão no GPIO 32 com Pull-Up interno
pino_botao = machine.Pin(32, machine.Pin.IN, machine.Pin.PULL_UP)

# ==========================================
# Variáveis de Estado e Constantes
# ==========================================
total_pecas = 0
estado_bloqueado = False
alerta_emitido = False

tempo_inicio_bloqueio = 0
ultimo_tempo_botao = 0

# Limiares 
LIMIAR_ADC = 2000          # Limite para detectar a queda de luz no divisor de tensão do módulo
TEMPO_PARADA_MS = 5000     # 5 segundos para caracterizar micro-parada
DEBOUNCE_MS = 250          # Tempo de debounce do botão

# ==========================================
# Inicialização
# ==========================================
# Mensagem obrigatória na inicialização do sistema
print("Contador de Producao Inicializado")

# ==========================================
# Loop Principal (Não-Bloqueante)
# ==========================================
while True:
    tempo_atual = time.ticks_ms()
    
    # 1. Rotina de Reset de Turno (Botão com Debounce)
    if pino_botao.value() == 0:
        if time.ticks_diff(tempo_atual, ultimo_tempo_botao) > DEBOUNCE_MS:
            total_pecas = 0
            estado_bloqueado = False
            alerta_emitido = False
            print("Turno resetado com sucesso. Contadores zerados.")
            ultimo_tempo_botao = tempo_atual

    # 2. Leitura do Sensor Óptico
    valor_adc = pino_ldr.read()
    
    # ATUALIZAÇÃO: Se a luz é obstruída (50 lux), a resistência sobe e a tensão no pino AO sobe.
    luz_obstruida = valor_adc > LIMIAR_ADC
    
    # Transição de Descida: A peça começou a interromper o feixe
    if luz_obstruida and not estado_bloqueado:
        estado_bloqueado = True
        tempo_inicio_bloqueio = tempo_atual
        alerta_emitido = False

    # Transição de Subida: A peça terminou de passar pelo sensor
    elif not luz_obstruida and estado_bloqueado:
        estado_bloqueado = False
        total_pecas += 1
        print(f"Peca detectada! Total: {total_pecas}")

    # 3. Detecção de Micro-paradas
    if estado_bloqueado and not alerta_emitido:
        if time.ticks_diff(tempo_atual, tempo_inicio_bloqueio) > TEMPO_PARADA_MS:
            print("Alerta: Micro-parada detectada!")
            alerta_emitido = True

    # Breve pausa para não sobrecarregar a CPU
    time.sleep_ms(20)
