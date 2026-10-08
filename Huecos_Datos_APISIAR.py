'''Detecta huecos en los datos de la API del SIAR sin cotejar la base de datos.
CSV que marca cuándo falta datos de la API respecto al volumen teórico esperado mes a mes.
'''

import csv
import calendar
import requests
from datetime import datetime
from tqdm import tqdm

from src.Mod_Funciones.clienteAPISIAR import genera_url_datos_climaticos
from src.Mod_Funciones.clienteAPISIAR import tiempo_cronometro

inicio = str(datetime.now())

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

#  Dada un fecha inicial y una fecha final calcular cuantos registros teoricos tiene que haber (para una frecuencia)
def calcula_num_registros_teoricos(fecha_inicio, fecha_fin, frecuencia, num_parametros = 1): 
    '''
        Dados los parámetros indicados devuelve como integer el número de registros
        teóricos que tiene la API
    '''

    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d') # https://www.digitalocean.com/community/tutorials/python-string-to-datetime-strptime 
    fecha_fin= datetime.strptime(fecha_fin, '%Y-%m-%d %H:%M:%S')
    
    diferencia = fecha_fin - fecha_inicio

    num_dias = round(diferencia.total_seconds()/(3600*24)) #https://www.geeksforgeeks.org/python-difference-between-two-dates-in-minutes-using-datetime-timedelta-method/
    num_meses = round(num_dias/30) # se redondean para evitar el error ya que la hora es hasta las 23:59
       
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

nombre_archivo_resultados = 'resultado_analisis_huecoDatos_APIV01.csv'

total = (
    len(listado_frecuencias)
    * len(listado_estaciones)
    * len(listado_anios)
    * len(listado_meses)
)

# Abrir un archivo donde escribiremos los resultados
with open(nombre_archivo_resultados, 'w', newline='') as archivo_resultados:
    # el archivo lo escribiremos como csv
    resultado = csv.writer(archivo_resultados)
    # Escribimos la primera línea o cabecera, con el orden en el que se escribirán los resultados
    resultado.writerow(['Estacion', "frecuencia", 'Mes/anio', 'Observaciones', 'num_registros_faltantes'])
    with tqdm(total=total, desc="Procesando datos") as pbar:
        # Para cada frecuencia...
        for frecuencia in listado_frecuencias:
            #...y para cada estación.
            for estacion in listado_estaciones:
                # Analizar para cada año...
                for anio in listado_anios:
                    # ...y mes a mes, si el número de registros es ok o no 
                    for mes in listado_meses:
                        # Genero los valores de la primera y última fecha del mes  para consultar la API
                        if(len(str(mes)) == 1): # si el mes es del 1 al 9 hay que añadirle un 0 antes (por definición de la API)
                            primera_fecha = str(anio) + "-0" + str(mes) + "-01"
                        else:
                            primera_fecha = str(anio) + "-" + str(mes) + "-01"
                        
                        # para generar la última fecha necesito saber el número de días que tiene el mes
                        num_dias_mes = calendar.monthrange(anio, mes)[1] # https://www.fatosmorina.com/how-to-get-the-number-of-days-in-a-month-in-python/#google_vignette
                        
                        if(len(str(mes)) == 1): # si el mes es del 1 al 9 hay que añadirle un 0 antes (por definición de la API)
                            ultima_fecha = str(anio) + "-0" + str(mes) + "-" + str(num_dias_mes) + " 23:59:00"
                        else:
                            ultima_fecha = str(anio) + "-" + str(mes) + "-" + str(num_dias_mes) + " 23:59:00"
                        
                        # Con esa información y la estación y la frecuencia llamo a las funciones que me dan info:
                        num_registros_teoricos = calcula_num_registros_teoricos(primera_fecha, ultima_fecha, frecuencia)
                        
                        filtros = {"fecha_inicio": primera_fecha, 
                                    "fecha_fin": ultima_fecha, 
                                    "parametro": "T", 
                                    "funcion": "Med"}
                        
                        num_registros_API = contar_numero_registros(estacion, frecuencia, **filtros)
                        
                        # Escribo en el archivo la información en el orden de la cabecera
                        if(num_registros_teoricos == num_registros_API): # si el número de registros teóricos es igual al número de registros que tiene la API, se considera que es ok y no faltan datos
                            resultado.writerow([str(estacion), frecuencia, str(mes) + "/" + str(anio),
                                                "OK",
                                                0])
                        else:
                            resultado.writerow([str(estacion), frecuencia, str(mes) + "/" + str(anio),
                                                "Faltan " + str(int(num_registros_teoricos) - num_registros_API) + " registros",
                                                int(num_registros_teoricos) - num_registros_API]) #si no es ok guardar un registro que indique codigo_estacion, mes/año, faltan x número de registros
                            
                            if(num_registros_teoricos - num_registros_API < 0): # esto no debería ocurrir, pero por si acaso sucede...
                                #mostramos mensaje error en pantalla y salimos del proceso
                                print("Error no controlado para estacion-frecuencia-mes/año", str(estacion), "-", frecuencia, "-", str(mes) + "/" + str(anio),
                                    " el numero registros teóricos es inferior al número de registros almacenados en la BBDD")
                                break   
                        pbar.update(1) # Actualizamos la barra de progreso

final = str(datetime.now())

tiempo = tiempo_cronometro(inicio, final)
print(f"El programa ha durado {tiempo}")