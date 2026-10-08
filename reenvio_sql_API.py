import csv # Para trabajar con archivos CSV
import os # Para trabajar con archivos y rutas
import oracledb # Para conectar con la base de datos Oracle
import socket # Para obtener el nombre del servidor y así conectar con la base de datos correcta
from datetime import datetime # Para trabajar con fechas y horas

from src.Mod_Funciones.clienteBDSIAR import conectar_bd_oracle, obtener_tabla

NUM_REGISTROS_MAXIMOS = 500 # Número máximo de registros a modificar para no sobrecargar el servidor
ARCHIVO_REGISTROS_FALTANTES = "./Registros_Faltantes.csv" 
""" Asegúrate de que la ruta al archivo CSV, 
    el cual contiene los registros faltantes obtenidos
    con el script Obtencion_SQL_API_CSV.py, sea correcta
"""

connection, bd = conectar_bd_oracle()

# Creo las variables necesarias para el proceso de modificación del archivo CSV.
contador = 0 # Contador para limitar los registros
lista_filas = [] # Lista para almacenar las filas modificadas. Luego se asignará a la variable "registros" para escribir en el archivo CSV

# Abrir el archivo CSV en modo lectura para modificar las filas que cumplan la condición "N" en la columna 3
with open(ARCHIVO_REGISTROS_FALTANTES, "r", encoding="utf-8") as f:
    registros = csv.reader(f, delimiter=";") # El delimitador es ";" porque el archivo CSV tiene el formato europeo
    for fila_registro in registros:
        if contador <= NUM_REGISTROS_MAXIMOS and len(fila_registro) == 4: # Para no sobrecargar el servidor pongo un máximos de 500 registros a modificar
            if fila_registro[3] == "N": # Solo se modificarán los registros que tengan un "N" en la columna 4, el cual indica que debe ser exportado
                if fila_registro[1] == "T": # Dependiendo de la frecuencia del registro, la consulta SQL para modificar el registro en la base de datos será diferente
                    fecha_hora = fila_registro[2].split(" ") # La fecha llega en formato "YYYY-MM-DD HH:MM:SS". Hay que separarlas para realizar la consulta SQL
                    fecha = datetime.strptime(str(fecha_hora[0]), "%Y-%m-%d") # El formato de la fecha de la base de datos es diferente, así que hay que cambiarlo
                    fecha = datetime.strftime(fecha, "%d/%m/%Y")
                    hora = datetime.strptime(str(fecha_hora[1]), "%H:%M:%S") # El formato de la hora de la base de datos es diferente, así que hay que cambiarlo
                    hora = datetime.strftime(hora, "%H:%M")
                    parametros = {"estacion": str(fila_registro[0]), "fecha": str(fecha), "hora": str(hora)} # Valores enlazados (evitan inyección SQL)
                    bd.execute(f"""UPDATE {obtener_tabla('T')} SET EXPORTADO = 'N' 
                               WHERE COD_ESTACION = :estacion AND FECHA = :fecha AND HORA = :hora""", parametros) # Actualizo el registro
                    connection.commit() # Confirmo los cambios en la base de datos
                    bd.execute(f"""SELECT EXPORTADO FROM {obtener_tabla('T')} 
                               WHERE COD_ESTACION = :estacion AND FECHA = :fecha AND HORA = :hora""", parametros)
                    comprobacion = bd.fetchone()[0] # Esto sirve para comprobar que realmente se ha modificado la columna del registro
                elif fila_registro[1] == "D":
                    fecha = datetime.strptime(str(fila_registro[2]), "%Y%m%d")
                    fecha = datetime.strftime(fecha, "%d%m%Y")
                    parametros = {"estacion": str(fila_registro[0]), "fecha": fecha}
                    bd.execute(f"UPDATE {obtener_tabla('D')} SET EXPORTADO = 'N' WHERE COD_ESTACION = :estacion AND FECHA = :fecha", parametros)
                    connection.commit()
                    bd.execute(f"SELECT EXPORTADO FROM {obtener_tabla('D')} WHERE COD_ESTACION = :estacion AND FECHA = :fecha", parametros)
                    comprobacion = bd.fetchone()[0]
                elif fila_registro[1] == "M":
                    fecha = datetime.strptime(str(fila_registro[2]), "%Y%m%d")
                    fecha = datetime.strftime(fecha, "%d%m%Y")
                    parametros = {"estacion": str(fila_registro[0]), "fecha": fecha}
                    bd.execute(f"UPDATE {obtener_tabla('M')} SET EXPORTADO = 'N' WHERE COD_ESTACION = :estacion AND FECHA = :fecha", parametros)
                    connection.commit()
                    bd.execute(f"SELECT EXPORTADO FROM {obtener_tabla('M')} WHERE COD_ESTACION = :estacion AND FECHA = :fecha", parametros)
                    comprobacion = bd.fetchone()[0]
                else:
                    lista_filas.append(fila_registro) # Esto no debería suceder, pero se introduce por si se modifica el script que genera el archivo csv
                
                if comprobacion == "N": # Si la comprobación es correcta, se modifica el valor de la columna 4 del registro a "OK" para indicar que ya ha sido exportado
                    fila_registro[3] = "OK"
                    lista_filas.append(fila_registro)
                    contador += 1 # Incremento el contador para limitar los registros a modificar
            else:
                lista_filas.append(fila_registro)
        else:
            lista_filas.append(fila_registro)

# Abrir el archivo CSV en modo escritura para escribir las filas modificadas
with open(ARCHIVO_REGISTROS_FALTANTES, "w", newline="", encoding="utf-8") as f:
    registros = csv.writer(f, delimiter=";")
    registros.writerows(lista_filas) # Escribo las filas modificadas en el archivo CSV. El delimitador es ";" porque el archivo CSV tiene el formato europeo

# Cerrar la conexión y el cursor
bd.close()
connection.close()