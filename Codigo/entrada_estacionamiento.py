
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
import datetime
import pymysql

os.environ['PIGPIO_ADDR'] = 'localhost'
os.environ['PIGPIO_PORT'] = '8888'


GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)

# Configurar el pin factory de pigpio
pi_gpio_factory = PiGPIOFactory()


# Configurar el pin del servo
SERVO_PIN = 19

# Inicializar el objeto Servo con el pin factory de pigpio
servo = Servo(SERVO_PIN, pin_factory=pi_gpio_factory)

# Definir los pines GPIO
pin_sensor = 29 # Pin para el boton tactil
# Configurar los pines
GPIO.setup(pin_sensor, GPIO.IN)



try:
    conexion = pymysql.connect(
        host='192.168.100.23',
        user='rb',
        password='RB#User123',
        database='base_estacionamiento'
    )
    print("Conexion exitosa")
    while True:
        estado = GPIO.input(pin_sensor)
        if estado == GPIO.LOW:
            print("Boton tactil no presionado")
            servo.min()
        else:
            print("Boton tactil presionado")
            reader = SimpleMFRC522()
            id,__ = reader.read()
            print(f"Tarjeta reconocida con exito con id: {id}")
            id2 = str(id)

            sql_query_tarjetas = "SELECT id FROM tarjeta WHERE codigo = %s ;"
            cur = conexion.cursor()
            cur.execute(sql_query_tarjetas, (id2,))
            for (id) in cur:
                id_tarjeta = (id)
            print(id_tarjeta)
            hora_actualesita = datetime.datetime.now().time()
            hora_actual = hora_actualesita.strftime("%Y-%m-%d %H:%M:%S")
            id_usuario = ""

            sql = "SELECT id FROM users WHERE id_tarjeta = %s ;"
            cur = conexion.cursor()
            cur.execute(sql, (id_tarjeta,))
            print("Consulta ejecutada", hora_actual)
            for (id) in cur:
                id_usuario = id
            print(id_usuario)
            sql2 = "INSERT INTO registros (id, id_usuario, id_tarjeta, fecha_entrada, fecha_salida) VALUES (%s, %s, %s, NOW(), %s)"
            val2 = ("", id_usuario, id_tarjeta, "")

            cur.execute(sql2, val2)
            conexion.commit()

            servo.max()
            time.sleep(2)
            sql_estatus_tarjeta = "UPDATE tarjeta SET estatus = %s  WHERE id = %s"
            cur.execute(sql_estatus_tarjeta,("Adentro",id_tarjeta))
            print(hora_actual)
            servo.min()

            # Esperar antes de leer nuevamente
            time.sleep(0.1)


except KeyboardInterrupt:
    print("Programa interrumpido por el usuario")

finally:
    # Limpiar la configuración de la GPIO al finalizar
    GPIO.cleanup()
