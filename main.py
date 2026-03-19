import board
import digitalio
import time

# Set pin number
LED_PIN = board.D17

# Initialize DigitalIO
led = digitalio.DigitalInOut(LED_PIN)
led.direction = digitalio.Direction.OUTPUT
# Blinking function

def blink(led_obj, number_blinks, period, duty_cycle):
        # duty_cycle is a percentage (0-100)
        time_high = period * (duty_cycle / 100)
        time_low = period - time_high
        for i in range(number_blinks):
        led_obj.value = True
        time.sleep(time_high)
        led_obj.value = False
        time.sleep(time_low)

# Blink LED 20 times
blink(led, 20, 0.5, 75)

# Cleanup
led.deinit() # Releases the pin
print("Program executed")