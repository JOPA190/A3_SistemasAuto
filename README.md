# 🔐 Sistema Automatizado de Controle de Acesso Biométrico e Monitoramento IoT (Projeto A3)

Projeto desenvolvido para a Avaliação A3 da unidade curricular de **Sistemas Automatizados**. O sistema integra hardware embarcado (**Arduino Uno**), visão computacional com Inteligência Artificial (**Python + OpenCV + DeepFace**) e supervisão remota via **API do Telegram** para controle de acesso físico e detecção de intrusos em tempo real.

---

## 👥 Integrantes do Grupo (Ordem Alfabética)

* **João Carlos Oliveira Passos** – RA: 82510149
* **Bryan Lira Junqueira** – RA:  825110147
* **Luiz Gustavo Dias Machado** – RA: 825223688
* **Felipe Cabral de Aquino** – RA: 82510945
* **Gabriel Martins Gomes de Oliveira** – RA: 825128943
* **Guilherme Fernandes Lima** – RA: 82516937

---

## ⚙️ Arquitetura e Funcionamento do Sistema

O projeto opera em uma arquitetura integrada de 4 etapas (Sensoriamento, Processamento, Atuação e Supervisão):

1. **Detecção de Presença (Hardware):** O sensor PIR (`HC-SR501`) monitora continuamente a área de acesso. Ao detectar movimento, o Arduino atualiza o Display LCD I2C (`"Movimento! Analisando Rosto"`) e envia o gatilho `"MOVIMENTO"` via comunicação Serial (`9600 bps`) para o computador.
2. **Captura e Validação Biométrica (Software/IA):** O script `ponte_serial.py` intercepta o sinal, aciona a webcam realizando um ciclo de estabilização luminosa de 5 frames e compara a imagem capturada com a base cadastrada (`autorizado.jpg`) utilizando a rede neural do **DeepFace** (`enforce_detection=True`).
3. **Atuação Física (Hardware):**
   * **Acesso Autorizado (`"LIBERADO"`):** O Arduino exibe `"Acesso Liberado / Bem-vindo!"` no LCD e atraca o **Módulo Relé** por 5 segundos para destravar a fechadura/carga.
   * **Acesso Negado (`"INTRUSO"`):** O Arduino exibe `"ALERTA: INTRUSO!!!"` no LCD e aciona o **Buzzer** com um alarme sonoro intermitente.
4. **Supervisão e Monitoramento Remoto (IoT):** Em caso de tentativa de invasão ou rosto não identificado, o script Python envia instantaneamente uma notificação para o **Telegram** contendo a **fotografia capturada do intruso** e o **horário exato da ocorrência**.

---

## 🔌 Mapeamento de Hardware e Pinagem

| Componente | Pino no Componente | Pino no Arduino Uno | Função no Sistema |
| :--- | :--- | :--- | :--- |
| **Sensor PIR (HC-SR501)** | `VCC` / `GND` / `OUT` | `5V` / `GND` / `Pino D2` | Sensoriamento de presença humana |
| **Módulo Relé 5V** | `VCC` / `GND` / `IN` | `5V` / `GND` / `Pino D3` | Atuador de destravamento da porta |
| **Buzzer Ativo 5V** | `(+)` / `(-)` | `Pino D4` / `GND` | Atuador de alarme sonoro de intrusão |
| **Display LCD 16x2 I2C (0x27)** | `VCC` / `GND` / `SDA` / `SCL` | `5V` / `GND` / `A4` / `A5` | Supervisão visual local de status |

---

## 🛠️ Tecnologias e Bibliotecas Utilizadas

* **Firmware Embarcado (C++ / Arduino IDE):**
  * `Wire.h` (Comunicação via barramento I2C)
  * `LiquidCrystal_I2C.h` (Controle do display LCD 16x2 no endereço `0x27`)
* **Back-end e Visão Computacional (Python 3.11):**
  * `pyserial` (Comunicação Serial RS-232/USB entre Arduino e PC)
  * `opencv-python` (Controle de hardware da webcam e captura de frames)
  * `deepface` / `tf-keras` (Reconhecimento e verificação biométrica facial)
  * `requests` (Integração HTTP POST com a API de Bot do Telegram)
  * `datetime` (Registro de timestamp nos alertas de segurança)

---

## 🚀 Como Executar o Projeto

### 1. Configuração do Arduino
1. Abra o arquivo `Arduino.c++` na **Arduino IDE**.
2. Instale a biblioteca **LiquidCrystal I2C** (por *Frank de Brabander*) no Gerenciador de Bibliotecas.
3. Selecione a placa **Arduino Uno** e a respectiva porta COM, e faça o upload do código.
4. *(Importante)* Feche o Monitor Serial da Arduino IDE após o upload para liberar a porta COM para o Python.

### 2. Configuração do Back-end em Python
1. Instale as dependências no terminal:
   ```bash
   pip install pyserial opencv-python deepface tf-keras requests
   ```
2. Adicione uma foto frontal nítida da pessoa autorizada na mesma pasta do script com o nome exato de **`autorizado.jpg`**.
3. No arquivo `ponte_serial.py`, configure a variável `PORTA` (ex: `'COM7'`) e insira o seu `TOKEN_TELEGRAM` e `CHAT_ID_TELEGRAM`.
4. Execute o sistema:
   ```bash
   python ponte_serial.py
   ```

### 3. Simulação do Circuito (Wokwi)
O repositório inclui o arquivo `diagram.json` contendo o mapeamento elétrico completo. Para simular:
1. Acesse o simulador [Wokwi](https://wokwi.com/).
2. Crie um projeto para **Arduino Uno**, cole o conteúdo de `Arduino.c++` na aba principal e substitua o conteúdo da aba `diagram.json` pelo arquivo deste repositório.

---

## 📂 Estrutura do Repositório

```text
📦 A3-Controle-Acesso-IoT
 ┣ 📜 controle_acesso.ino   # Firmware C++ para o Arduino Uno
 ┣ 📜 ponte_serial.py       # Script Python (Visão Computacional + Serial + Telegram)
 ┣ 📜 diagram.json          # Esquema elétrico interativo para o simulador Wokwi
 ┗ 📜 README.md             # Documentação geral do projeto
```
