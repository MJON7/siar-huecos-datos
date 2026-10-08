'''Analiza cada combinación estación/frecuencia/mes y compara el conteo de registros de la API
con el conteo de registros en la base de datos Oracle. Devuelve un CSV de resultados con errores
y huecos detectados, incluidas investigaciones adicionales por fecha/hora.
'''

import csv
import calendar
import requests
from datetime import datetime
from tqdm import tqdm

from src.Mod_Funciones.clienteAPISIAR import genera_url_datos_climaticos
from src.Mod_Funciones.clienteAPISIAR import tiempo_cronometro
from src.Mod_Funciones.clienteBDSIAR import generarcsv_sql_API_csv, conectar_bd_oracle, obtener_tabla

NOMBRE_ARCHIVO_RESULTADOS = "Registros_Faltantes.csv"

inicio = str(datetime.now())

#  Dada un fecha inicial y una fecha final calcular cuantos registros teoricos tiene que haber (para una frecuencia)
def contar_numero_registros(estacion, frecuencia, **filtros):
    '''
        Dada una estacion, una frecuencia y unos filtros compatibles con la peticion a la API
        (p.ej "fecha_inico", "fecha_fin", "parametro", "funcion", "posicion) comprobar cuantos registros tiene la API 
        
        Al hacer solicitud a la API, la respuesta JSON contiene variables "count", "success" y "datos"
        La variable "count" incluye el número de registros de ese tipo que tiene la BBDD

        Esta función devuelve el valor de "count" como integer
        En caso de error de comunicación devuelve valor "None"
    '''    
     
    api_url = genera_url_datos_climaticos(estacion, frecuencia, **filtros)
    res = requests.get(api_url) # conectamos con esa url método GET y guardamos el contenido en la variable res
    
    if res.ok:
        res = res.json()    # lo que nos interesa de la respuesta es el número de registros, 
                            # que se encuentra en la variable "count" del JSON
        return(int(res["count"]))
    else:
        print("Error al comunicar con la API")
        return(None)

def calcula_num_registros_teoricos(fecha_inicio, fecha_fin, frecuencia, num_parametros = 1): 
    '''
        Dados los parámetros indicados devuelve como integer el número de registros
        teóricos que tiene la API
    '''

    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d') # https://www.digitalocean.com/community/tutorials/python-string-to-datetime-strptime 
    fecha_fin= datetime.strptime(fecha_fin, '%Y-%m-%d %H:%M:%S')
    
    diferencia = fecha_fin - fecha_inicio

    num_dias = round(diferencia.total_seconds()/(3600*24)) #https://www.geeksforgeeks.org/python-difference-between-two-dates-in-minutes-using-datetime-timedelta-method/
    num_meses = round(num_dias/30) # Se redondean para evitar el error ya que la hora es hasta las 23:59
       
    if frecuencia == "T":
        total_registros = 48 * num_dias * num_parametros
    if frecuencia == "D":
        total_registros = num_dias * num_parametros
    if frecuencia == "M":
        total_registros = num_meses * num_parametros 
    
    return int(total_registros)

# Incializar variables
listado_estaciones = list(range(501, 524)) # Aquí se introduce el rango de estaciones que se comprobará
listado_estaciones.append(201) # Se añade la estación al la lista
listado_frecuencias = ["T", "D", "M"] # Aquí se introduce el rango de frecuencias que se comprobará
listado_anios = list(range(2005, 2026)) # Aquí se introduce el rango anual que se comprobará
listado_meses = list(range(1, 13)) # Aquí se introduce el rango mensual que se comprobará de cada anio

# Determino cuántos meses se procesarán en total para actualizar la barra de progreso
total = (
    len(listado_frecuencias)
    * len(listado_estaciones)
    * len(listado_anios)
    * len(listado_meses)
)

connection, bd = conectar_bd_oracle()

# Para cada frecuencia...
with open(NOMBRE_ARCHIVO_RESULTADOS, 'w', newline='') as archivo_resultados:
    # El archivo lo escribiremos como csv
    # El formato del csv será europeo, es decir, con coma como separador decimal y punto y coma como delimitador entre columnas
    resultado = csv.writer(archivo_resultados, quoting=csv.QUOTE_NONE, escapechar='\\', delimiter=";")
    with tqdm(total=total, desc="Procesando datos") as pbar:
        for frecuencia in listado_frecuencias:
            #...y para cada estación
            for estacion in listado_estaciones:
                # Analizar para cada año...
                for anio in listado_anios:
                    # ...y mes a mes, si el número de registros es ok o no 
                    for mes in listado_meses:
                        # Genero los valores de la primera y última fecha del mes  para consultar la API
                        if(len(str(mes)) == 1): # si el mes es del 1 al 9 hay que añadirle un 0 antes (por definición de la API)
                            primera_fecha = str(anio) + "-0" + str(mes) + "-01"
                            primera_fecha_bd = "01-0" + str(mes) + "-" + str(anio)
                        else:
                            primera_fecha = str(anio) + "-" + str(mes) + "-01"
                            primera_fecha_bd = "01-" + str(mes) + "-" + str(anio)
                        
                        # Para generar la última fecha necesito saber el número de días que tiene el mes
                        num_dias_mes = calendar.monthrange(anio, mes)[1] # https://www.fatosmorina.com/how-to-get-the-number-of-days-in-a-month-in-python/#google_vignette
                        
                        if(len(str(mes)) == 1): # Si el mes es del 1 al 9 hay que añadirle un 0 antes (por definición de la API)
                            ultima_fecha = str(anio) + "-0" + str(mes) + "-" + str(num_dias_mes) + " 23:59:00"
                            ultima_fecha_db = str(num_dias_mes) + "-0" + str(mes) + "-" + str(anio)
                        else:
                            ultima_fecha = str(anio) + "-" + str(mes) + "-" + str(num_dias_mes) + " 23:59:00"
                            ultima_fecha_db = str(num_dias_mes) + "-" + str(mes) + "-" + str(anio)
                        
                        # Con esa información y la estación y la frecuencia llamo a las funciones que me dan info:
                        num_registros_teoricos = calcula_num_registros_teoricos(primera_fecha, ultima_fecha, frecuencia)
                        filtros = {"fecha_inicio": primera_fecha,
                                    "fecha_fin": ultima_fecha,
                                    "parametro": "T",
                                    "funcion": "Med"
                                    }
                        
                        num_registros_API = contar_numero_registros(estacion, frecuencia, **filtros)
                        
                        #Dependiendo de la frecuencia se mandará una cosulta SQL a una tabla u otra
                        # (la tabla se obtiene del archivo .env con obtener_tabla)
                        instruccion = f"""SELECT COUNT(*) FROM {obtener_tabla(frecuencia)} WHERE 
                            (COD_ESTACION = :estacion AND FECHA 
                            BETWEEN :inicio AND :fin)
                        """
                        
                        bd.execute(instruccion, {"estacion": str(estacion),
                                                 "inicio": primera_fecha_bd,
                                                 "fin": ultima_fecha_db})
                        numreg = bd.fetchone()[0]

                        # Escribo en el archivo la información en el orden de la cabecera
                        if (num_registros_teoricos == num_registros_API):
                            # Están todos los registros
                            pass
                        elif (num_registros_API == 0) and (numreg == 0):
                            # No hay registros
                            if frecuencia == "D" or frecuencia == "M":
                                generarcsv_sql_API_csv(frecuencia, num_dias_mes, mes, anio, estacion, resultado, primera_fecha, ultima_fecha, bd)
                                #print(ultima_fecha_db)
                        elif (not(num_registros_API == 0)) and (numreg == 0):
                            # No hay registros en base de datos, pero si en la API. No debería pasar
                            resultado.writerow([estacion, frecuencia, str(anio) + "/" + str(mes), "ERROR. Sin registros en la base de datos."])
                        elif num_registros_API > numreg:
                            # Hay mas registros que provienen de la API que de la base de datos
                            resultado.writerow([estacion, frecuencia, str(anio) + "/" + str(mes), "ERROR. Hay más registros en la API que en la base de datos."])
                        elif (num_registros_API == 0) and (numreg == num_registros_teoricos):
                            # No hay registros en la API y en la base de datos están todos
                            generarcsv_sql_API_csv(frecuencia, num_dias_mes, mes, anio, estacion, resultado, primera_fecha, ultima_fecha, bd)
                        elif (num_registros_API < numreg) and (numreg != num_registros_teoricos):
                            # Hay más registros en la base de datos que en la API
                            generarcsv_sql_API_csv(frecuencia, num_dias_mes, mes, anio, estacion, resultado, primera_fecha, ultima_fecha, bd)
                        else:
                            # Faltan algunos registros de la API
                            generarcsv_sql_API_csv(frecuencia, num_dias_mes, mes, anio, estacion, resultado, primera_fecha, ultima_fecha, bd)
                        pbar.update(1) # Actualizamos la barra de progreso


# Cerrar la conexión y el cursor
bd.close()
connection.close()

final = str(datetime.now())

tiempo = tiempo_cronometro(inicio, final)
print(f"El programa ha durado {tiempo}")