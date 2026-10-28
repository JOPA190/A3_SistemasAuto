/**
 * Sistema de Controle de Acesso Biométrico e Monitoramento IoT
 * 
 * Módulo: Firmware de Controle Embarcado (Arduino Uno)
 * Descrição: Realiza a leitura do sensor de presença (PIR), gerencia a 
 * interface local via Display LCD I2C e aciona os atuadores (Relé e Buzzer)
 * mediante validação biométrica recebida via comunicação Serial.
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Inicializa o Display LCD no endereço I2C 0x27 com 16 colunas e 2 linhas
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Mapeamento de Pinos Digitais (Hardware)
const int pinoPIR = 2;    // Entrada digital: Sensor de Movimento HC-SR501
const int pinoRele = 3;   // Saída digital: Módulo Relé (Trava Elétrica / Carga)
const int pinoBuzzer = 4; // Saída digital: Buzzer Ativo (Alarme Sonoro)

// Variável de controle de estado (evita disparos repetidos contínuos)
bool pessoaDetectada = false;

void setup() {
  // Atraso de estabilização elétrica na inicialização da placa
  delay(100); 

  // Inicia a comunicação serial a 9600 bps (mesmo baud rate do script Python)
  Serial.begin(9600);
  
  // Configuração dos modos de operação dos pinos
  pinMode(pinoPIR, INPUT);
  pinMode(pinoRele, OUTPUT);
  pinMode(pinoBuzzer, OUTPUT);
  
  // Garante que os atuadores iniciem desligados
  digitalWrite(pinoRele, LOW);
  digitalWrite(pinoBuzzer, LOW);

  // Inicialização do Display LCD I2C e ativação da luz de fundo (Backlight)
  lcd.begin(16, 2); 
  lcd.backlight(); 
  
  // Exibe o estado inicial de supervisão
  mostrarMensagem("Sistema Armado", "Aguardando...");
}

void loop() {
  // =========================================================================
  // ETAPA 1: SENSORIAMENTO E NOTIFICAÇÃO AO BACK-END (ARDUINO -> PYTHON)
  // =========================================================================
  int leituraPIR = digitalRead(pinoPIR);
  
  // Se detectar movimento pela primeira vez no ciclo atual
  if (leituraPIR == HIGH && !pessoaDetectada) {
    Serial.println("MOVIMENTO"); // Envia gatilho pela porta Serial
    pessoaDetectada = true; 
    
    mostrarMensagem("Movimento!", "Analisando Rosto");
    delay(2000); // Tempo para estabilização da captura no PC
  } 
  // Reseta a flag quando o sensor parar de detectar presença
  else if (leituraPIR == LOW && pessoaDetectada) {
    pessoaDetectada = false;
  }

  // =========================================================================
  // ETAPA 2: RECEBIMENTO DA VALIDAÇÃO E ATUAÇÃO (PYTHON -> ARDUINO)
  // =========================================================================
  if (Serial.available() > 0) {
    // Lê o comando enviado pelo script Python até a quebra de linha
    String comandoPC = Serial.readStringUntil('\n');
    comandoPC.trim(); // Remove espaços ou caracteres invisíveis (\r)

    // Caso 1: Biometria facial reconhecida com sucesso
    if (comandoPC == "LIBERADO") {
      mostrarMensagem("Acesso Liberado", "Bem-vindo!");
      
      digitalWrite(pinoRele, HIGH); // Aciona o relé (destrava a porta)
      delay(5000);                  // Mantém liberado por 5 segundos
      digitalWrite(pinoRele, LOW);  // Trava a porta novamente
      
      mostrarMensagem("Sistema Armado", "Aguardando...");
    } 
    // Caso 2: Rosto desconhecido ou não identificado (Intruso)
    else if (comandoPC == "INTRUSO") {
      mostrarMensagem("ALERTA:", "INTRUSO!!!");
      
      tocarAlarme(); // Aciona o alerta sonoro intermitente
      
      mostrarMensagem("Sistema Armado", "Aguardando...");
    }
  }
}

/**
 * Atualiza as duas linhas do Display LCD 16x2 de forma padronizada
 */
void mostrarMensagem(String linha1, String linha2) {
  lcd.clear();
  lcd.setCursor(0, 0); 
  lcd.print(linha1);
  lcd.setCursor(0, 1); 
  lcd.print(linha2);
}

/**
 * Emite 5 bipes sonoros no Buzzer em caso de tentativa de invasão
 */
void tocarAlarme() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(pinoBuzzer, HIGH);
    delay(300);
    digitalWrite(pinoBuzzer, LOW);
    delay(300);
  }
}