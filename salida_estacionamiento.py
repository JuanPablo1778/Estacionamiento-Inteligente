

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
pin_sensor = 31  # Pin para el boton tactil
# Configurar los pines
GPIO.setup(pin_sensor, GPIO.IN)
contador = 1
tiempo = ""
pagar = 0
saldo_real = 1

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
                print("boton tactil precionado")
                servo.min()
                reader = SimpleMFRC522()
                id, name = reader.read()
                id2 = int(id)
                id, name= reader.read()
                sql_query_tarjetas = "SELECT id FROM tarjeta WHERE codigo = %s ;"
                cur = conexion.cursor()
                cur.execute(sql_query_tarjetas, (id2,))

                for (id) in cur:
                    id_tarjeta_bd = (id)
                id_tarjeta_primero = id_tarjeta_bd[0]
                id_tarjeta = int(id_tarjeta_primero)
                print(f"Tarjeta detectada con {id_tarjeta} como id")
                print("Tarjeta reconocida con exito")

                sql_query_estatarjeta = "SELECT estatus FROM tarjeta WHERE codigo = %s ;"
                cur = conexion.cursor()
                cur.execute(sql_query_estatarjeta, (id2,))
                for (estatus) in cur:
                    estatus_tarjeta = (estatus)
                    estatus_tarjeta_primero = estatus_tarjeta[0]
                    estatus_tarjeta_completo = str(estatus_tarjeta_primero)
                print(estatus_tarjeta_primero)
                time.sleep(2)
                if estatus_tarjeta_primero == "Adentro":
                    sql1 = f"SELECT id FROM users;"
                    cur = conexion.cursor()
                    cur.execute(sql1)

                    hora_actualesita = datetime.datetime.now().time()
                    hora_actual = hora_actualesita.strftime("%Y-%m-%d %H:%M:%S")

                    sql2 = "UPDATE registros SET fecha_salida = NOW()  WHERE id_tarjeta = %s AND fecha_salida is NULL"
                    cur.execute(sql2,(id_tarjeta))
                    print(hora_actual)
                    conexion.commit()
                    print("esa es ha lora actual")
                    sql3 = f"SELECT fecha_salida,  fecha_entrada FROM registros;"
                    cur = conexion.cursor()
                    cur.execute(sql3)
                    for (fecha_salida, fecha_entrada) in cur:
                        print("ESTA ES LA HORA INGESADA")
                        print(fecha_salida)
                        tiempo = fecha_salida - fecha_entrada
                        tiempo_hora = tiempo.seconds // 3600
                        tiempo_hora = tiempo_hora + 1
                        pagar = tiempo_hora * 15

                    print("te haz quedado ", tiempo_hora, "horas y vas a pagar ", pagar, " pesos")
                    print(tiempo)

                    sql_saldo = f"SELECT saldo FROM users WHERE id_tarjeta = %s;"
                    cur = conexion.cursor()
                    cur.execute(sql_saldo,(id_tarjeta,))

                    for (saldo) in cur:
                        saldo_real = (saldo)
                    print (saldo_real)
                    pagar_primero = pagar
                    saldo_real_primero = saldo_real[0]
                    saldo_real_int = int (saldo_real_primero)
                    pagar_int = int (pagar_primero)
                    print (saldo_real_int)
                    if saldo_real_int >= pagar_int:
                        saldo_real_int = saldo_real_int - pagar_int
                        sql_meter_saldo = "UPDATE users SET saldo = %s  WHERE id_tarjeta = %s"

                        cur.execute(sql_meter_saldo,(saldo_real_int,id_tarjeta))
                        conexion.commit()
                        servo.max()
                        time.sleep(2)
                        servo.min() 

                    else:
                        print("Saldo insuficiente, recargue dinero o pague en cajero por favor")
                        time.sleep(2)

    # Esperar antes de leer nuevamente
    time.sleep(0.1)
    conexion.commit()
    conexion.close()

except KeyboardInterrupt:
    print("Programa interrumpido por el usuario")


finally:

    GPIO.cleanup()
