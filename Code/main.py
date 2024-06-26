#import lib.ledblink
#import lib.mqtt_comms as mqtt_comms
import lib.keys as keys
import utime as time
import lib.adafruit as adafruit
from machine import Pin, ADC
import dht
import lib.adafruit as adafruit

# For rotary
from lib.rotary_irq_rp2 import RotaryIRQ

import lib.wifi as wifiConnection         # Contains functions to connect/disconnect from WiFi 

verbose = True

# Try WiFi Connection
try:
    ip = wifiConnection.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

client = adafruit.connect()

temp_humid_sensor = dht.DHT11(Pin(6))     # DHT11 Constructor 

knock_pin = Pin(16, Pin.IN) # Define knock pin

#vibratePin = Pin(1, Pin.IN) # Define vibration sensor pin

light_detector = ADC(Pin(28))

#ir_detector = Pin(13, Pin.IN)

#ir_transmitter = Pin(12, Pin.OUT)
#ir_transmitter.on()


temp_humid_report_cooldown = 10000
temp_humid_last_report = 0

#ir_report_cooldown = 1000
#ir_last_report = 0

light_report_cooldown = 10000
light_last_report = 0

knock_report_cooldown = 10000
knock_last_report = 0

# Rotary stuff
rotary = RotaryIRQ(pin_num_clk=18,
              pin_num_dt=19,
              min_val=0,
              max_val=20,
              reverse=False,
              range_mode=RotaryIRQ.RANGE_WRAP)

old_rotary_val = rotary.value()

rotary_cooldown = 1000
rotary_last_report = 0


def rotary_update():
    
    global old_rotary_val
    global rotary_last_report

    new_rotary_val = rotary.value()
    
    if rotary_last_report + rotary_cooldown < time.ticks_ms():
        diff = new_rotary_val - old_rotary_val
        wrapped_difference_up = (new_rotary_val + 21 - old_rotary_val) % 21
        wrapped_difference_down = (old_rotary_val + 21 - new_rotary_val) % 21

        if abs(diff) <= abs(wrapped_difference_up) and abs(diff) <= abs(wrapped_difference_down):
            # No wrapping involved
            if diff > 0:
                adafruit.send_number(client, "Left", keys.AIO_ROTARY_FEED, verbose)
            else:
                adafruit.send_number(client, "Right", keys.AIO_ROTARY_FEED, verbose)
        else:
            # Wrapping involved
            if wrapped_difference_up < wrapped_difference_down:
                adafruit.send_number(client, "Left", keys.AIO_ROTARY_FEED, verbose)
            else:
                adafruit.send_number(client, "Right", keys.AIO_ROTARY_FEED, verbose)
            
        old_rotary_val = new_rotary_val
        if verbose:
            print(f"Rotated to value: {old_rotary_val}")
        rotary_last_report = time.ticks_ms()
    
    

rotary.add_listener(rotary_update)

time.sleep(1)

try:
    while True:
        
        '''
        # IR stuff
        if ir_last_report + ir_report_cooldown < time.ticks_ms():
            ir_last_report = time.ticks_ms()
            ir_in = ir_detector.value()
            if ir_in == 0:
                adafruit.send_number(client, "Creature detected", keys.AIO_IR_FEED, verbose)
            if verbose:
                if ir_in == 1:
                    print("No IR light detected - a creature must be here!")
                else:
                    print("IR light detected. We are safe, for now...")
        '''
        
        
        # Light stuff
        if light_last_report + light_report_cooldown < time.ticks_ms():
            light_last_report = time.ticks_ms()
            light = light_detector.read_u16()
            if verbose:
                print(f"Light voltage: {light}")
            light = round(light / 65535 * 100, 2)
            if verbose:
                print("It is {}% bright.".format(light))
            adafruit.send_number(client, light, keys.AIO_LIGHT_FEED, verbose)
        
        
        
        
        # Temperature and humidity stuff
        if temp_humid_last_report + temp_humid_report_cooldown < time.ticks_ms():
            temp_humid_last_report = time.ticks_ms()
            try:
                temp_humid_sensor.measure()
                temperature = temp_humid_sensor.temperature()
                humidity = temp_humid_sensor.humidity()
                if verbose:
                    print("Temperature is {} degrees Celsius and Humidity is {}%".format(temperature, humidity))
                adafruit.send_number(client, humidity, keys.AIO_HUMIDITY_FEED, verbose)
                adafruit.send_number(client, temperature, keys.AIO_TEMPERATURE_FEED, verbose)
            except Exception as error:
                print("Exception occurred during temperature/humidity measurement: ", error)
        
        
        
        

        # Knock stuff
        if knock_last_report + knock_report_cooldown < time.ticks_ms():
            knock = knock_pin.value()
            if knock == 1:
                adafruit.send_number(client, 1, keys.AIO_KNOCK_FEED, verbose)
                knock_last_report = time.ticks_ms()
                if verbose:
                    print("Knock, knock!")
        '''else:
            #adafruit.send_number(client, 0, keys.AIO_KNOCK_FEED, verbose)
            if verbose:
                print("No knock.")
        '''

        '''
        # Vibration stuff
        if vibratePin.value() == 1:
            if verbose:
                adafruit.send_number(client, 1, keys.AIO_VIBRATE_FEED, verbose)
                print("Good vibrations..!")
        else:
            if verbose:
                adafruit.send_number(client, 0, keys.AIO_VIBRATE_FEED, verbose)
                print("No vibration...")
        '''
        

finally:                  # If an exception is thrown ...
        client.disconnect()   # ... disconnect the client and clean up.
        client = None
        wifiConnection.disconnect()
        print("Disconnected from Adafruit IO.")

#lib.ledblink.blink_onboard()
#lib.ledblink.blink_external()
