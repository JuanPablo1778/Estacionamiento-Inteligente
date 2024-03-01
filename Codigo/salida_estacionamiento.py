# -- coding: utf-8 --
from datetime import datetime
import pymysql
import datetime
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
import pymysql

os.environ['PIGPIO_ADDR'] = 'localhost'
os.environ['PIGPIO_PORT'] = '8888'


GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)

# Configurar el pin factory de pigpio
pi_gpio_factory = PiGPIOFactory()


# Configurar el pin del servo
SERVO_PIN = 16

# Inicializar el objeto Servo con el pin factory de pigpio
servo = Servo(SERVO_PIN, pin_factory=pi_gpio_factory)

# Definir los pines GPIO
pin_sensor = 22 # Pin para el boton tactil
# Configurar los pines
GPIO.setup(pin_sensor, GPIO.IN)
contador = 1
tiempo = ""
pagar = 0
try:
    conexion = pymysql.connect(
        host='192.168.100.23',
        user='rb',
        password='RB#User123',
        database='base_estacionamiento'

    )
    while True:
        estado = GPIO.input(pin_sensor)
        if estado == GPIO.LOW:
             print("Boton tactil no presionado")
             servo.min()
        else:

            if contador == 2:
                 servo.max()
            else:
                servo.min()
                reader = SimpleMFRC522()
                id, name = reader.read()
                id2 = int(id)
                id, name= reader.read()
                sql_query_tarjetas = "SELECT id FROM tarjeta WHERE codigo = %s ;"
                cur = conexion.cursor()
                cur.execute(sql_query_tarjetas, (id2,))
                for (id) in cur:
                    id_tarjeta = (id)

                print(f"Tarjeta detectada con {id} como id")
                print("Tarjeta reconocida con exito")

                sql1 = f"SELECT id FROM users;"
                cur = conexion.cursor()
                cur.execute(sql1)

                hora_actualesita = datetime.datetime.now().time()
                hora_actual = hora_actualesita.strftime("%Y-%m-%d %H:%M:%S")

                sql2 = "UPDATE registros SET fecha_salida = NOW()  WHERE id_tarjeta = %s"
                cur.execute(sql2,(id_tarjeta))
                print(hora_actual)

                sql3 = f"SELECT fecha_salida,  fecha_entrada FROM registros;"
                cur = conexion.cursor()
                cur.execute(sql3)
                for (fecha_salida, fecha_entrada) in cur:

                    tiempo = fecha_salida - fecha_entrada
#                    pagar = tiempo * 15
                    print("te haz quedado ", tiempo, "horas y vas a pagar ", pagar, " pesos")
                print(tiempo)

                sql4 = f"SELECT saldo FROM registros WHERE id_tarjeta = %s;"
                cur = conexion.cursor()
                cur.execute(sql4,(id_tarjeta,))

                if saldo < pagar:
                    saldo = saldo - pagar
                    sql2 = "UPDATE users SET saldo = %s  WHERE id_tarjeta = %s"

                    mycursor.execute(sql4,(saldo,id_tarjeta))
                print("Saldo insuficiente, recargue dinero o pague en cajero por favor")
                servo.max()
                time.sleep(2)
                servo.min()

        # Esperar antes de leer nuevamente
        time.sleep(0.1)
        db.commit()
        db.close()

except KeyboardInterrupt:
    print("Programa interrumpido por el usuario")

finally:
    # Limpiar la configuración de la GPIO al finalizar
    GPIO.cleanup()
