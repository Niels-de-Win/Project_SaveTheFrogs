from gpiozero import PWMOutputDevice
from time import sleep

# Use GPIO 17 (This is NOT a hardware PWM pin)
soft_pwm = PWMOutputDevice(17)
while True:
    soft_pwm.value = 0.2 # 20% Duty Cycle
    sleep(1)
    soft_pwm.value = 0.8 # 80% Duty Cycle
    sleep(1)