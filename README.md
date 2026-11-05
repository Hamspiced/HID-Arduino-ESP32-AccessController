# HID-Arduino-AccessController
This is a project repository for creating a full fledged door access controller using an HID Reader, Arduino, and i2c screen.  

The Arduino portion of this project will allow you to use the reader as a simple badge scanner, act as a door controller, identify authorized access control cards, add cards, and delete cards.

The ESP32 Portion of this project will do all of the same as well as connect to your wifi or host an AP that can be connected do.  Through the Web Server you can add an Admin card, trigger the door signal, add cards, remove cards, as well as see a log of all scanned cards.

![R15 Door Simulator](https://github.com/Hamspiced/HID-Arduino-AccessController/raw/main/Images/R15%20Door%20Simulator2.jpeg)


## Parts

 [Arduino Nano](https://a.co/d/4Q9VMcR) - $16.49 per 3 or $5.49 ea
 or
 [Esp32 Dev board](https://a.co/d/32qhvlW) - $29 for 5 or 5.50$ each
 
 [USB-C Pigtail](https://a.co/d/i3n7h48) - $7.99 per 10 or $0.80 ea
 
 [Arduino Breakout Board](https://a.co/d/hGXZX4y) - $8.79 per 3 or $2.93 ea
 
 [5v Buck Converter](https://a.co/d/7Qql78y) - $11.59 per 5 or $2.32 ea
 
 [i2c 2 Color OLED](https://a.co/d/0r9uNRJ) - $13.98 per 5 or $2.80 ea
 
 HID R10 or R15 Multiclass Reader - Ebay or Marketplace Price Varies between 20-90$ Any reader should work that uses the Wiegand protocol

Total Cost without Reader: $58.84/$14.34

Optional (if you want to add a Relay and Door Striker/Mag Lock

 [DC 5v Relay Module 1 Channel](https://a.co/d/gpslT7C) - 12.99 per $10 or $1.29 ea
 
 [USB-C PD Trigger Board](https://a.co/d/3NxkBei) $9.98 for 4 or $2.50 ea
 
 [12v Door Strike](https://a.co/d/8t9gDx0) $64.19 each
 
 [12v Pin Deadbolt (used in my Test Bench)](https://www.aliexpress.us/item/3256804840295067.html) $10.00 each


## 3d Printed Cases

 I have the cases uploaded to Thingiverse but in case it goes down ill attach them to the repository.  Ive made 2 cases for the two different form factors of the Rp15 and 
 R10 Multiclass Se Readers 
 
 [RP15 Case STL - Top](https://github.com/Hamspiced/HID-Arduino-AccessController/blob/main/Cases/R15_Bottom.stl)
 
 [RP15 Case STL - Bottom](https://github.com/Hamspiced/HID-Arduino-AccessController/blob/main/Cases/R15__Top.stl)
 
 [R10 Case STL - Top](https://github.com/Hamspiced/HID-Arduino-AccessController/blob/main/Cases/R10_Case_Top.stl)
 
 [R10 Case STL - Bottom](https://github.com/Hamspiced/HID-Arduino-AccessController/blob/main/Cases/R10_Case_bottom.stl)
 
 [R10 Case with MagLock STL - Top](https://github.com/Hamspiced/HID-Arduino-AccessController/blob/main/Cases/R10_MaglockCase_Top.stl)
 
 [R10 Case With Maglock STL - Bottom](https://github.com/Hamspiced/HID-Arduino-AccessController/blob/main/Cases/R10_MaglockCase_bottom.stl)

## 📌 ARDUINO Pinout Connections

### 🔌 HID Reader to Arduino Uno

| HID Wire Color | Arduino Uno Pin |
|----------------|------------------|
| Black          | GND              |
| Green          | D2               |
| White          | D3               |
| Brown          | D5               |
| Orange         | D6               |
| Yellow         | A3               |

### 📟 OLED to Arduino

| OLED Pin | Arduino Uno Pin |
|----------|------------------|
| VCC      | 5V               |
| GND      | GND              |
| SCL      | A5               |
| SDA      | A4               |

### ⚡ Power Input to Step-Down Converter

| Power Input Wire | Step-Down Pin |
|------------------|----------------|
| Black            | - IN           |
| Red              | + IN           |

### 🔋 Step-Down Converter to Arduino

| Step-Down Pin | Arduino Uno Pin |
|---------------|------------------|
| - OUT         | GND              |
| + OUT         | VIN              |

 Note: Match the Pins to the pin on that actual microcontroller and not to the printed labels on the breakout board.

## Assembly
 Next assemble the OLED into the case, you may need a dab of hot glue to secureit. 
 Attach the Readerto the case next its easiest to keep the base plate on and thread the screws down from the reader into the case and use nuts to secure the case to the reader and trim off excess of the screw.
 attach the breakout board to the bottom case
 attach MCU to the breakout board.  
 Stepdown module can go in its slot and it should clip into place.  
 Feed the wires for the pig tail USB C into the case from outside and press fit into place, then solder the connection to the stepdown converter In + and -
 You can use Heatset inserts or just screws to attach to the bottom of the case.

Note: When programming you have to connect USB C directly to the arduino, The USB-C Pigtail is power only it wont pass data through so you cant update your Arduino with this connection.  Likewise you cannot power the reader directly by the Arduino power, it isnt poweful enough for that.

## Assembly of Relay + Door Strike.
Run Wire from Arduino Pin 7 or ESP32 Pin 27 to Relay IN 
Run 12v+ from USB-C PD to Door Strike
Run 12v- from USB-C PD to Relay Com.
Run Wire from NO (Normall Open) on Relay to Doorstrike.
Run 5v+ From Step Down to DC+ on relay
Run 5v- from Step Down to DC- on relay



# Headless flash

`make flash` compiles and uploads the Nano and the ESP32 with [arduino-cli](https://arduino.github.io/arduino-cli/), then writes the ESP32 LittleFS image from `ESP32_Code/data` (the web UI, plus `cards.txt` and `admin.txt`). The Arduino IDE is not required.

```bash
make bootstrap   # download arduino-cli if it is not on PATH, then install cores and libraries
make list        # show serial ports
make compile     # build both sketches, no upload
make flash       # Nano, then ESP32 app, then LittleFS
```

The Nano target defaults to the ATmega328P old bootloader (`NANO_CPU=atmega328old`), which is what most clone boards need. An official Nano is:

```bash
make flash-nano NANO_CPU=atmega328
```

Ports come from `arduino-cli board list`. A CP2102 (`10C4:EA60`) or Espressif native USB id (`303A`) is the ESP32. An FTDI adapter (`0403:6001`) or official Arduino id (`2341`) is the Nano. CH340 adapters (`1A86:7523`) are used on both boards, so if both ports look the same, set them yourself:

```bash
make flash NANO_PORT=/dev/ttyUSB0 ESP_PORT=/dev/ttyUSB1
```

`make flash-esp32` uploads the ESP32 sketch and the filesystem. `make flash-esp32 SKIP_FS=1` (or `make flash SKIP_FS=1`) uploads firmware only and leaves the card list already stored on the device. `make flash-fs` rewrites LittleFS from `ESP32_Code/data`, which replaces `index.html`, `cards.txt`, and `admin.txt`.

The IDE steps below still work.

# Flashing Arduino via Arduino IDE

Download and install Arduino IDE.
You can copy the code file itself, or copy and paste the code into IDE.  Some MCU's from china require you to select old bootloader, or power up while pressing the reset button. 

# Use
On Startup the Reader defaults to Read Mode.  To switch modes you will need to pre-program 4 cards or add your card UID to the code  by default it is:


### 🏷️ RFID Mode UIDs and Proxmark3 Commands

| Mode         | UID         | LF Command (T5577)             | HF Command (Magic 1K Card)                           |
|--------------|-------------|--------------------------------|------------------------------------------------------|
| Read Mode    | `0x1E6DC032` | `lf em 410xwrite 1E6DC032`     | `hf mf csetuid -u 1E6DC032`                          |
| Door Mode    | `0x1E6D9861` | `lf em 410xwrite 1E6D9861`     | `hf mf csetuid -u 1E6D9861`                          |
| Add Mode     | `0x1E6DFCA0` | `lf em 410xwrite 1E6DFCA0`     | `hf mf csetuid -u 1E6DFCA0`                          |
| Remove Mode  | `0x1E6DE636` | `lf em 410xwrite 1E6DE636`     | `hf mf csetuid -u 1E6DE636`                          |

Door Mode will send a Signal on Pin6 to activate a Door Relay when authorized cards are scanned.
When Add Mode is selected, when a card is scanned it is added to the controller
when Remove mode is selected if that card is scanned it is removed from the controller

TODO: Scanning the remove mode card 3 times will reset all added cards (not mode cards)



# Configuring the Admin UID (Arduino Nano)

The Arduino Nano build uses an Admin card to cycle modes (READ → DOOR → ADD → DEL). To set your own Admin UID:

1) Get your card's UID
- Put the Nano in READ MODE and scan the card. The OLED shows the HEX UID as “Card: 0x…”. Convert that HEX to decimal, or temporarily enable Serial to print the decimal (see step 2).

2) Optional: enable Serial to view the decimal UID
- In `Arduino nano Code/HIDR10-RP15-Door-Simulator/HIDR10-RP15-Door-Simulator.ino`, set `#define ENABLE_SERIAL 1`. Upload, open Serial Monitor at 115200, scan the card, note the `RAW` decimal, then set `ENABLE_SERIAL` back to 0 if desired.

3) Set the Admin UID
- In the same file, edit the line:
  `#define ADMIN_UID_DEFAULT 253411519UL`
  Replace `253411519UL` with your card's decimal UID and keep the `UL` suffix.

4) Upload the sketch
- Upload to your Nano. On boot, the Admin UID will be used to detect admin scans and cycle modes.

Notes
- The Admin UID is read from EEPROM if present; when EEPROM is blank, the compiled `ADMIN_UID_DEFAULT` is used. If you later change the default and re-upload, the new default will take effect without any extra steps.

# ESP32 Installation

I use Arduino IDE for the ESP32.  I had to download the ESP32Little Fs plugin for Arduino IDE 2.x.   More information on it can be found from [earlephilhower's Github](https://github.com/earlephilhower/arduino-littlefs-upload) the TL;DR is: 

Copy the VSIX file to ~/.arduinoIDE/plugins/ on Mac and Linux or C:\Users\<username>\.arduinoIDE\plugins\ on Windows (you may need to make this directory yourself beforehand).

Once the plugin is in it's folder.  You can load the INO file into your sketch.  In the sketch folder, in the root create a directory called "data" and place the html file in there.  Then, Upload your code to your ESP32 (selecting the proper board and port).  When upload is complete: 

On Windows: press [Ctrl] + [Shift] + [P], then "Upload LittleFS to Pico/ESP8266/ESP32".

On macOS: press [⌘] + [Shift] + [P] to open the Command Palette in the Arduino IDE, then "Upload LittleFS to Pico/ESP8266/ESP32".

It will upload the data folder with the web page interface.


  ## ESP32 Usage

The ESP32 adds a Web Interface to the RFID Reader.  It will allow you to access a webpage (192.168.4.1 when in Access Point Mode) that will allow you to add Admin Cards, Trigger the door sensor, and display a card log.  

  ##REST Api

  There are Endpoints for the REST API already added to the code.  The Endpoint webhooks are within the code.  I dont use Home Assistant but if you are savvy you should be able to use this with home assistant.
    



## Pinouts for ESP32 devices
   
   ### 📌 Xiao ESP32C3 Pin Mapping

   | Function      | Physical Pin | Arduino Pin |
   |---------------|--------------|-------------|
   | Wiegand D0    | 2            | D2          |
   | Wiegand D1    | 3            | D3          |
   | Beeper        | 6            | D6          |
   | Door Strike   | 7            | D7          |
   | I2C SDA       | 4            | D4          |
   | I2C SCL       | 5            | D5          |

   ### 📌  ESP32 Pin Mapping

   | Function      | GPIO         | Label          |
   |---------------|--------------|----------------|
   | Wiegand D0    | 16           | Wiegand D0 Pin |
   | Wiegand D1    | 17           | Wiegand D1 Pin |
   | Beeper        | 26           | Beeper Pin     |
   | Door Strike   | 27           | Signal Pin     |
   | I2C SDA       | 21           | SSD1306 OLED   |
   | I2C SCL       | 22           | SSD1306 OLED   |


 # Use

 When booted up the esp32 will broadcast a Wifi Signal named: Door-Simulator.  Encryption Key is "12345678".  In the code you can also specify your own wifi network for it to connect to.  By default the default AP will host the webservice on: 192.168.4.1



# Home Assistant Integration Guide

## 1. Install a Text Editor Add-on

- Install a **Text Editor Add-on** or **Studio Code Server Add-on** from the Home Assistant Add-on Store.

## 2. Edit Configuration

- Open your `configuration.yaml` file with your preferred editor.
- Paste the contents of **RFIDHomeAssistant.yaml** at the **end** of your `configuration.yaml`.
- **Important:** Change `"YourDeviceIPaddress"` to the static IP assigned to your door reader.

## 3. Check and Restart

- Go to **Developer Tools** → **YAML** → **Check Configuration**.
- If the configuration is valid, press **Restart**. (You may need to confirm a few times.)

## 4. Verify Entities

After restart, go to:

    Settings > Devices & Services > Entities

Search for:

- `sensor.rfid_door_mode`
- `sensor.rfid_last_card`

These entities will show the current mode and the last card scanned.

---

## 5. Trigger Door

- Go to **Developer Tools** → **Services**.
- Search for `rest_command.trigger_rfid_door` and click **Call Service** to test.

---

## 6. Change Mode

- Use `rest_command.set_rfid_mode` with a data payload to set the desired mode.

---

## Add the New Entities to Your Dashboard

1. Go to your dashboard.
2. Click the three dots (⋮) in the upper right and choose **Take Control**.
3. Click **Add Card** in the lower right.
4. Choose **By Entity**.
5. Select the RFID entities and hit **Continue**.

---

## Add a Mode Button

You can also add a button to display and control the reader mode:

```yaml
type: button
entity: sensor.rfid_door_mode
name: RFID Mode
show_state: true
tap_action:
  action: call-service
  service: rest_command.cycle_rfid_mode
```   

## 🙏 Acknowledgments

Huge thanks to [Peekaboo](https://github.com/Peekaboo-ICU) for their invaluable support in helping bring this project to life.  
From debugging my bad code to offering key insights and improvements, their contributions were instrumental in getting this over the finish line.  

Explore more of their work at [Peekaboo.icu](https://peekaboo.icu)


 
## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to use, modify, and share this code for **non-commercial purposes**, provided proper attribution is given.  
**Commercial use is not permitted** without prior written consent. Please [contact the author](mailto:your.email@example.com) to inquire about commercial licensing.
