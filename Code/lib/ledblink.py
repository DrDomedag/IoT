from machine import Pin
import utime as time


def blink_onboard():
    onboard_led = Pin("LED", Pin.OUT)

    while True:
        onboard_led.on()
        time.sleep(1)
        onboard_led.off()
        time.sleep(1)

def blink_external():
    external_LED = Pin(16, Pin.OUT)

    while True:
        external_LED.on()
        time.sleep(0.3)
        external_LED.off()
        time.sleep(0.8)