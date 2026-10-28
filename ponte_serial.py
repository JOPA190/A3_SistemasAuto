"""
Sistema de Controle de Acesso Biométrico e Monitoramento IoT

Módulo: Back-end de Visão Computacional, Ponte Serial e Notificação IoT
Descrição: Escuta a porta serial do Arduino Uno, realiza a captura de vídeo
via OpenCV quando o sensor PIR é acionado, valida a biometria facial com
DeepFace e envia alertas remotos com foto e horário via API do Telegram.
"""

import serial
import time
import cv2
from deepface import DeepFace
import requests
from datetime import datetime

# ============================================================================
# CONFIGURAÇÕES GERAIS E CREDENCIAIS
# ============================================================================
PORTA = 'COM7'       # Porta Serial onde o Arduino Uno está conectado
BAUD_RATE = 9600     # Taxa de transmissão (deve ser igual ao Serial.begin)

# Credenciais do Bot do Telegram (Substitua pelos seus dados locais)
TOKEN_TELEGRAM = "SEU_TOKEN_AQUI"
CHAT_ID_TELEGRAM = "SEU_CHAT_ID_AQUI"
# ============================================================================

def enviar_foto_telegram(caminho_imagem, mensagem_base):
    """
    Envia uma notificação remota para o Telegram contendo a fotografia 
    capturada pela webcam e o carimbo exato de data e hora do evento.
    """
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    mensagem_com_hora = f"{mensagem_base}\n🕒 Horário: {agora}"
    
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendPhoto"
    
    try:
        with open(caminho_imagem, 'rb') as foto:
            payload = {'chat_id': CHAT_ID_TELEGRAM, 'caption': mensagem_com_hora}
            files = {'photo': foto}
            requests.post(url, data=payload, files=files, timeout=10)
            
        print("[SISTEMA] 📸 Alerta com foto e horário enviado para o Telegram!")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar foto para o Telegram: {e}")

print("[SISTEMA] A iniciar o sistema de segurança IoT...")

try:
    # Inicializa a comunicação serial com o microcontrolador
    arduino = serial.Serial(PORTA, BAUD_RATE, timeout=1)
    time.sleep(2) # Aguarda o reset automático da placa Arduino após conexão
    print(f"[SISTEMA] Ligado ao Arduino na porta {PORTA}. A aguardar o sensor PIR...")
    
    while True:
        # Verifica se há bytes recebidos no buffer da porta serial
        if arduino.in_waiting > 0:
            mensagem_placa = arduino.readline().decode('utf-8').strip()
            
            # Gatilho disparado pelo sensor PIR no Arduino
            if mensagem_placa == "MOVIMENTO":
                print("\n[ALERTA] Movimento detetado! A ligar a câmara...")
                
                # Inicializa a webcam padrão (índice 0)
                video_capture = cv2.VideoCapture(0)
                
                # Ciclo de aquecimento (descarta 5 frames em 2.5s para ajuste de foco e luz)
                print("[IA] A estabilizar a câmara e a focar...")
                for _ in range(5):
                    time.sleep(0.5)
                    video_capture.read()
                
                # Captura o frame definitivo para análise
                ret, frame = video_capture.read()
                
                if ret:
                    print("[IA] Fotografia capturada! A processar biometria...")
                    cv2.imwrite("captura_temporaria.jpg", frame)
                    
                    try:
                        # Compara a captura atual com a imagem de referência (autorizado.jpg)
                        # enforce_detection=True exige que um rosto humano nítido esteja visível
                        resultado = DeepFace.verify(
                            img1_path="captura_temporaria.jpg", 
                            img2_path="autorizado.jpg", 
                            enforce_detection=True 
                        )
                        
                        if resultado["verified"]:
                            print(">> Rosto CONFIRMADO! A enviar comando: LIBERADO")
                            arduino.write(b"LIBERADO\n") 
                        else:
                            print(">> Rosto DESCONHECIDO! A enviar comando: INTRUSO")
                            arduino.write(b"INTRUSO\n")
                            enviar_foto_telegram(
                                "captura_temporaria.jpg", 
                                "🚨 ALERTA: Intruso detetado no Sistema de Segurança A3!"
                            )
                            
                    except Exception:
                        # Acionado caso não haja rosto visível na câmera ou o ambiente esteja escuro
                        print(">> Erro na verificação (sem rosto visível). A enviar: INTRUSO")
                        arduino.write(b"INTRUSO\n")
                        enviar_foto_telegram(
                            "captura_temporaria.jpg", 
                            "⚠️ ALERTA: Movimento detetado, mas rosto não identificado!"
                        )
                else:
                    print("[ERRO] Não foi possível aceder à câmara web.")
                
                # Libera o recurso de hardware da webcam
                video_capture.release()

except serial.SerialException:
    print(f"[ERRO] Não foi possível ligar à porta {PORTA}. Verifique a conexão USB e feche o Monitor Serial.")
except KeyboardInterrupt:
    print("\n[SISTEMA] Encerrado manualmente pelo utilizador.")
finally:
    if 'arduino' in locals() and arduino.is_open:
        arduino.close()