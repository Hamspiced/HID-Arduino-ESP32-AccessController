# Headless build and flash for the Nano and ESP32 door-controller sketches.
#   make bootstrap   install arduino-cli (if needed), cores, and libraries
#   make compile     build both sketches
#   make flash       upload the Nano, the ESP32 app, and the LittleFS image

CONFIG := arduino-cli.yaml
PYTHON ?= python3

NANO_CPU ?= atmega328old
NANO_FQBN := arduino:avr:nano:cpu=$(NANO_CPU)
ESP_FQBN := esp32:esp32:esp32:UploadSpeed=921600,FlashSize=4M,PartitionScheme=default
ESP_BAUD ?= 921600

NANO_SKETCH := Arduino nano Code/HIDR10-RP15-Door-Simulator
ESP_SKETCH := ESP32_Code
ESP_DATA := ESP32_Code/data
BUILD_NANO := build/nano
BUILD_ESP := build/esp32
SCRIPTS := scripts

ARDUINO_CLI_ON_PATH := $(shell command -v arduino-cli 2>/dev/null)
ifeq ($(ARDUINO_CLI_ON_PATH),)
  ARDUINO_CLI := $(CURDIR)/.tools/arduino-cli
else
  ARDUINO_CLI := $(ARDUINO_CLI_ON_PATH)
endif

ifeq ($(SKIP_FS),1)
FLASH_FS_AFTER := true
else
FLASH_FS_AFTER := $(PYTHON) $(SCRIPTS)/flash_littlefs.py --config $(CONFIG) --cli "$(ARDUINO_CLI)" --fqbn "$(ESP_FQBN)" --build-dir $(BUILD_ESP) --data "$(ESP_DATA)" --baud $(ESP_BAUD) --port "$$port"
endif

.DEFAULT_GOAL := compile

.PHONY: bootstrap compile compile-nano compile-esp32 list \
	flash flash-nano flash-esp32 flash-fs

# Download the official CLI into .tools/ only when it is not already on PATH.
$(CURDIR)/.tools/arduino-cli:
	mkdir -p .tools
	curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR="$(CURDIR)/.tools" sh
	test -x "$@"

bootstrap: $(if $(ARDUINO_CLI_ON_PATH),,$(CURDIR)/.tools/arduino-cli)
	"$(ARDUINO_CLI)" --config-file $(CONFIG) core update-index
	"$(ARDUINO_CLI)" --config-file $(CONFIG) core install arduino:avr
	"$(ARDUINO_CLI)" --config-file $(CONFIG) core install esp32:esp32
	"$(ARDUINO_CLI)" --config-file $(CONFIG) lib install "Adafruit SSD1306" "Adafruit GFX Library"
	"$(ARDUINO_CLI)" --config-file $(CONFIG) lib install --git-url https://github.com/monkeyboard/Wiegand-Protocol-Library-for-Arduino
	mkdir -p .arduino
	touch .arduino/.bootstrapped

.arduino/.bootstrapped: arduino-cli.yaml
	$(MAKE) bootstrap

compile: compile-nano compile-esp32

compile-nano: .arduino/.bootstrapped
	"$(ARDUINO_CLI)" --config-file $(CONFIG) compile --fqbn "$(NANO_FQBN)" --build-path $(BUILD_NANO) "$(NANO_SKETCH)"

compile-esp32: .arduino/.bootstrapped
	"$(ARDUINO_CLI)" --config-file $(CONFIG) compile --fqbn "$(ESP_FQBN)" --build-path $(BUILD_ESP) "$(ESP_SKETCH)"

list: .arduino/.bootstrapped
	"$(ARDUINO_CLI)" --config-file $(CONFIG) board list

flash: flash-nano flash-esp32

flash-nano: compile-nano
	port=$$($(PYTHON) $(SCRIPTS)/resolve_ports.py --config $(CONFIG) --cli "$(ARDUINO_CLI)" --need nano --print); \
	test -n "$$port" || exit 1; \
	"$(ARDUINO_CLI)" --config-file $(CONFIG) upload -p "$$port" --fqbn "$(NANO_FQBN)" --input-dir $(BUILD_NANO)

flash-esp32: compile-esp32
	port=$$($(PYTHON) $(SCRIPTS)/resolve_ports.py --config $(CONFIG) --cli "$(ARDUINO_CLI)" --need esp --print); \
	test -n "$$port" || exit 1; \
	"$(ARDUINO_CLI)" --config-file $(CONFIG) upload -p "$$port" --fqbn "$(ESP_FQBN)" --input-dir $(BUILD_ESP); \
	$(FLASH_FS_AFTER)

flash-fs: compile-esp32
	port=$$($(PYTHON) $(SCRIPTS)/resolve_ports.py --config $(CONFIG) --cli "$(ARDUINO_CLI)" --need esp --print); \
	test -n "$$port" || exit 1; \
	$(PYTHON) $(SCRIPTS)/flash_littlefs.py --config $(CONFIG) --cli "$(ARDUINO_CLI)" --fqbn "$(ESP_FQBN)" --build-dir $(BUILD_ESP) --data "$(ESP_DATA)" --baud $(ESP_BAUD) --port "$$port"
