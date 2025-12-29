#
# Thermostat - Automatic Demo - FINAL
#

from time import sleep, time
from datetime import datetime
from statemachine import StateMachine, State
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import serial
from gpiozero import PWMLED
from threading import Thread
from math import floor

DEBUG = True

# serial setup for UART output to server simulator
ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# LEDs
redLight = PWMLED(18)
blueLight = PWMLED(23)

# LCD management
class ManagedDisplay():
    def __init__(self):
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        self.lcd_columns = 16
        self.lcd_rows = 2

        self.lcd = characterlcd.Character_LCD_Mono(
            self.lcd_rs, self.lcd_en, self.lcd_d4, self.lcd_d5,
            self.lcd_d6, self.lcd_d7, self.lcd_columns, self.lcd_rows
        )
        self.lcd.clear()

    def cleanupDisplay(self):
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message

screen = ManagedDisplay()

# state Machine
class TemperatureMachine(StateMachine):
    off = State('OFF', initial=True)
    heat = State('HEAT')
    cool = State('COOL')

    setPoint = 72

    cycle = off.to(heat) | heat.to(cool) | cool.to(off)

    def on_enter_heat(self):
        self.updateLights()
        if DEBUG: print("* Entering HEAT")

    def on_exit_heat(self):
        redLight.off()

    def on_enter_cool(self):
        self.updateLights()
        if DEBUG: print("* Entering COOL")

    def on_exit_cool(self):
        blueLight.off()

    def on_enter_off(self):
        redLight.off()
        blueLight.off()
        if DEBUG: print("* Entering OFF")

    def processTempStateButton(self):
        if DEBUG: print("Cycling mode")
        self.cycle()

    def processTempIncButton(self):
        if DEBUG: print("Increasing setpoint")
        self.setPoint += 1
        self.updateLights()

    def processTempDecButton(self):
        if DEBUG: print("Decreasing setpoint")
        self.setPoint -= 1
        self.updateLights()

    def updateLights(self):
        temp = floor(self.getFahrenheit())
        redLight.off()
        blueLight.off()

        if self.current_state == self.heat:
            if temp < self.setPoint:
                redLight.pulse()      # Fading
            else:
                redLight.on()         # Solid
        elif self.current_state == self.cool:
            if temp > self.setPoint:
                blueLight.pulse()     # Fading
            else:
                blueLight.on()        # Solid
        # OFF: both already off

    def getFahrenheit(self):
        return 70.0  # fixed demo temperature

    def setupSerialOutput(self):
        return f"{self.current_state.id.lower()},{self.getFahrenheit():.1f},{self.setPoint}\n"

    endDisplay = False

    def manageMyDisplay(self):
        counter = 1
        altCounter = 1
        while not self.endDisplay:
            current_time = datetime.now()
            lcd_line_1 = current_time.strftime("%m/%d/%y %H:%M:%S") + "\n"

            if altCounter < 6:
                lcd_line_2 = f"Temp: {self.getFahrenheit():.1f} F"
                altCounter += 1
            else:
                lcd_line_2 = f"{self.current_state.id}: {self.setPoint} F"
                altCounter += 1
                if altCounter >= 11:
                    self.updateLights()
                    altCounter = 1

            screen.updateScreen(lcd_line_1 + lcd_line_2)

            if counter % 30 == 0:
                ser.write(self.setupSerialOutput().encode())
                counter = 1
            else:
                counter += 1
            sleep(1)

        screen.cleanupDisplay()

# AUTOMATIC DEMO MODE
DEMO_MODE = True
demo_timer = 0
demo_step = 0

def run_demo():
    global demo_timer, demo_step
    while True:
        if DEMO_MODE:
            now = int(time())
            if now - demo_timer >= 15:  # action every 15 seconds
                demo_timer = now
                if demo_step == 0:
                    tsm.processTempStateButton()  # OFF to HEAT
                    print("=== Demo: Switching to HEAT ===")
                elif demo_step == 1:
                    tsm.processTempIncButton()
                    tsm.processTempIncButton()
                    print("=== Demo: Setpoint +2 ===")
                elif demo_step == 2:
                    tsm.processTempStateButton()  # HEAT to COOL
                    print("=== Demo: Switching to COOL ===")
                elif demo_step == 3:
                    tsm.processTempDecButton()
                    tsm.processTempDecButton()
                    print("=== Demo: Setpoint -2 ===")
                elif demo_step == 4:
                    tsm.processTempStateButton()  # COOL to OFF
                    print("=== Demo: Switching to OFF ===")
                demo_step = (demo_step + 1) % 5
        sleep(1)

# start everything
tsm = TemperatureMachine()
display_thread = Thread(target=tsm.manageMyDisplay)
display_thread.start()

demo_thread = Thread(target=run_demo)
demo_thread.daemon = True
demo_thread.start()

# keep main thread alive
try:
    while True:
        sleep(30)
except KeyboardInterrupt:
    print("\nCleaning up. Exiting...")
    tsm.endDisplay = True
    sleep(1)