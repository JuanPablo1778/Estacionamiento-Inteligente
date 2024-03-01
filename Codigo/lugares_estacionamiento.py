# -- coding: utf-8 --
from gpiozero import LED
import smbus
import os
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import RPi.GPIO as GPIO
import time
from time import sleep
import os
from mfrc522 import SimpleMFRC522


os.environ['PIGPIO_ADDR'] = 'localhost'
os.environ['PIGPIO_PORT'] = '8888'


GPIO.setwarnings(False)

#declarar sensores us
TRIG_PIN = 11
ECHO_PIN = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

#numero2
TRIG_PIN2 = 16
ECHO_PIN2 = 12

GPIO.setup(TRIG_PIN2, GPIO.OUT)
GPIO.setup(ECHO_PIN2, GPIO.IN)


#numero3
TRIG_PIN3 = 18
ECHO_PIN3 = 32

GPIO.setup(TRIG_PIN3, GPIO.OUT)
GPIO.setup(ECHO_PIN3, GPIO.IN)


# Configurar el pin GPIO para los led
LED1 = LED (20)
LED2 = LED (21)
LED3 = LED (26)


# Configurar el pin factory de pigpio
pi_gpio_factory = PiGPIOFactory()


def obtener_distancia():
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    inicio, fin = time.time(), time.time()

    while GPIO.input(ECHO_PIN) == 0:
        inicio = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        fin = time.time()

    return (fin - inicio) * 34300 / 2



def obtener_distancia2():
    GPIO.output(TRIG_PIN2, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN2, False)

    inicio2, fin2 = time.time(), time.time()

    while GPIO.input(ECHO_PIN2) == 0:
        inicio2 = time.time()

    while GPIO.input(ECHO_PIN2) == 1:
        fin2 = time.time()

    return (fin2 - inicio2) * 34300 / 2

def obtener_distancia3():
    GPIO.output(TRIG_PIN3, True)

    time.sleep(0.00001)
    GPIO.output(TRIG_PIN3, False)

    inicio3, fin3 = time.time(), time.time()

    while GPIO.input(ECHO_PIN3) == 0:
        inicio3 = time.time()

    while GPIO.input(ECHO_PIN3) == 1:
        fin3 = time.time()

    return (fin3 - inicio3) * 34300 / 2






try:

    while True:
        distancia = obtener_distancia()
        distancia2 = obtener_distancia2()
        distancia3 = obtener_distancia3()
#        print(distancia)
#        print(distancia2)
#        print(distancia3)
        if distancia < 6:
            LED3.on()
        else:
            LED3.off()
        if distancia2 < 6:
            LED2.on()
        else:
            LED2.off()
        if distancia3 < 6:
            LED1.on()
        else:
            LED1.off()
        # Esperar antes de leer nuevamente
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programa interrumpido por el usuario")

finally:
    # Limpiar la configuración de la GPIO al finalizar
    GPIO.cleanup()
