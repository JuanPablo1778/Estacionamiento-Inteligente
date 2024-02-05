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

os.environ['PIGPIO_ADDR'] = 'localhost'
os.environ['PIGPIO_PORT'] = '8888'


GPIO.setwarnings(False)

#declarar sensores us
TRIG_PIN = 13
ECHO_PIN = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

#numero2
TRIG_PIN2 = 15
ECHO_PIN2 = 16

GPIO.setup(TRIG_PIN2, GPIO.OUT)
GPIO.setup(ECHO_PIN2, GPIO.IN)


#numero3
TRIG_PIN3 = 18
ECHO_PIN3 = 22

GPIO.setup(TRIG_PIN3, GPIO.OUT)
GPIO.setup(ECHO_PIN3, GPIO.IN)


# Configurar el pin GPIO para los led
LED1 = LED (13)
LED2 = LED (19)
LED3 = LED (26)

# Direccion I2C del sensor MLX90614
direccion_i2c_mlx90614 = 0x5A

# Registro de temperatura del objeto
registro_temperatura_objeto = 0x07

# Configuracion del bus I2C

bus_i2c = smbus.SMBus(1)  # Usa 0 en lugar de 1 si estas utilizando Raspberry Pi 1


# Configurar el pin factory de pigpio
pi_gpio_factory = PiGPIOFactory()


# Configurar el pin del servo
SERVO_PIN = 17

# Inicializar el objeto Servo con el pin factory de pigpio
servo = Servo(SERVO_PIN, pin_factory=pi_gpio_factory)


# Definir los pines GPIO
pin_sensor = 31  # Pin para el boton tactil
# Configurar los pines
GPIO.setup(pin_sensor, GPIO.IN)

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

        # Leer el estado del botón
        estado = GPIO.input(pin_sensor)

        if estado == GPIO.LOW:
            print("Boton tactil no presionado")
            servo.min()
        else:
            print("Boton tactil presionado")
            servo.max()

            # Leer la temperatura del objeto desde el sensor MLX90614
            temperatura_objeto = bus_i2c.read_word_data(direccion_i2c_mlx90614, registro_temperatura_objeto)
            temperatura_objeto = (temperatura_objeto * 0.02) - 273.15
            # Establecer un umbral de temperatura para determinar la presencia de un objeto
            umbral_temperatura = 19.0

            while temperatura_objeto < umbral_temperatura:
                # Leer la temperatura del objeto desde el sensor MLX90614
                temperatura_objeto = bus_i2c.read_word_data(direccion_i2c_mlx90614, registro_temperatura_objeto)
                temperatura_objeto = (temperatura_objeto * 0.02) - 273.15
                # Establecer un umbral de temperatura para determinar la presencia de un objeto
                umbral_temperatura = 19.0
                print("No hay un objeto presente")
                servo.max()
                time.sleep(0.3)
            print("Hay un objeto presente")
            time.sleep(0.1)
            servo.min()

        # Esperar antes de leer nuevamente
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programa interrumpido por el usuario")

finally:
    # Limpiar la configuración de la GPIO al finalizar
    GPIO.cleanup()