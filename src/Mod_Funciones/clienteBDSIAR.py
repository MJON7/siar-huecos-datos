# Este espacio de trabajo contiene funciones más específicas para consultas y modificaciones a la base de datos

__author__ = "SIAR-GOBIERNO DE LA RIOJA"
__copyright__ = ""
__credits__ =["Alejandro Daniel Bucur Bucur"]
__license__ = "MIT"
__version__ = "0.1"
__email__ = "siar.cida@larioja.org"
__status__ = "Desarrollo"

# CONSTANTES
DEBUG = False # Debug = True devuelve valores respuesta API en caso de error
            # Debug = False devuelve None cuando no comunica bien con la API

import os
import re
import socket
import oracledb
import requests # Para hacer las peticiones a la API
from datetime import datetime, timedelta # Para manejar fechas y horas
from dotenv import load_dotenv

load_dotenv()

from .clienteAPISIAR import genera_url_datos_climaticos

# Los nombres de las tablas se leen del archivo .env para no exponer el esquema de la base de datos.
# Cada frecuencia ("T" horaria, "D" diaria, "M" mensual) tiene su propia tabla.
_VARIABLES_TABLA = {"T": "TABLA_HORARIA", "D": "TABLA_DIARIA", "M": "TABLA_MENSUAL"}
# Formato válido: NOMBRE_TABLA o ESQUEMA.NOMBRE_TABLA
_PATRON_TABLA = re.compile(r"^[A-Za-z_][A-Za-z0-9_$#]*(\.[A-Za-z_][A-Za-z0-9_$#]*)?$")


def obtener_tabla(frecuencia):
    """Devuelve el nombre de la tabla correspondiente a la frecuencia ("T", "D" o "M").

    Oracle no permite pasar el nombre de una tabla como variable enlazada (:variable),
    así que se valida su formato antes de insertarlo en la consulta para evitar inyección SQL.
    """
    variable = _VARIABLES_TABLA.get(frecuencia)
    if variable is None:
        raise ValueError(f"Frecuencia no reconocida: {frecuencia}")
    tabla = os.getenv(variable)
    if not tabla or not _PATRON_TABLA.match(tabla):
        raise ValueError(f"La variable {variable} no está definida en el archivo .env o no es un nombre de tabla válido")
    return tabla


def conectar_bd_oracle():
    """Inicializa el cliente Oracle y devuelve la conexión y el cursor."""
    oracledb.init_oracle_client(os.getenv("ORACLE_CLIENT"))
    servidor = socket.gethostname()

    try:
        # Para alternar entre una DB y la otra se sustituye la comilla
        if servidor == os.getenv("SERVIDOR_DESARROLLO"):
            dsn = os.getenv("DSN_PROD_R")
            # dsn = os.getenv("DSN_DESA_L")
        elif servidor == os.getenv("SERVIDOR_PRODUCCION"):
            dsn = os.getenv("DSN_PROD_L")
            # dsn = os.getenv("DSN_DESA_R")
        else:
            raise ValueError(f"Servidor no reconocido: {servidor}")

        connection = oracledb.connect(
            user=None,
            password=None,
            dsn=dsn,
            config_dir=os.getenv("ORACLE_CONFIG"),
            wallet_location=os.getenv("ORACLE_WALLET"),
        )
    except Exception:
        print("ERROR. Se produjo un error con la conexión al servidor o la validación de credenciales")
        raise

    return connection, connection.cursor()


def comparacion(bd, frecuencia, num_dias_mes, primera_fecha_bd, ultima_fecha_db, mes, anio, estacion, num_registros_teoricos, resultado, numreg):
    if numreg == num_registros_teoricos:
        resultado.writerow([f"---"]) # De esta manera divido los registros para verlos con mayor claridad.
    else:
        if frecuencia == "T":
            bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('T')} WHERE (COD_ESTACION = :estacion AND FECHA BETWEEN :inicio AND :fin)",
                       {"estacion": str(estacion), "inicio": primera_fecha_bd, "fin": f"15/{mes}/{anio}"})
            numreg = bd.fetchone()[0]
            if numreg == 720:
                for dia in range(16, num_dias_mes + 1):
                    if len(str(dia)) == 1:
                        dia == f"0{dia}"
                    else:
                        pass
                    bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('T')} WHERE (COD_ESTACION = :estacion AND FECHA = :fecha)",
                    {"estacion": str(estacion), "fecha": f"{dia}/{mes}/{anio}"})
                    existreg = bd.fetchone()[0]
                    
                    if existreg < 48:
                        resultado.writerow([f"Falta uno o mas registros en la base de datos en la fecha {dia}/{mes}/{anio}"])
                    else:
                        pass

                    if dia == num_dias_mes:
                        resultado.writerow([f"---"])
                    else:
                        pass
                
            else:
                bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('T')} WHERE (COD_ESTACION = :estacion AND FECHA BETWEEN :inicio AND :fin)",
                           {"estacion": str(estacion), "inicio": f"16/{mes}/{anio}", "fin": ultima_fecha_db})
                numreg = bd.fetchone()[0]
                if numreg == num_registros_teoricos - 720:
                    for dia in range(1, 16):
                        if len(str(dia)) == 1:
                            dia == f"0{dia}"
                        else:
                            pass
                        bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('T')} WHERE (COD_ESTACION = :estacion AND FECHA = :fecha)",
                    {"estacion": str(estacion), "fecha": f"{dia}/{mes}/{anio}"})
                        existreg = bd.fetchone()[0]
                        
                        if existreg < 48:
                            resultado.writerow([f"Falta {48 - existreg} registros en la base de datos en la fecha {dia}/{mes}/{anio}"])
                        else:
                            pass

                        if dia == 15:
                            resultado.writerow([f"---"])
                        else:
                            pass

                else:
                    for dia in range(1, num_dias_mes + 1):
                        if len(str(dia)) == 1:
                            dia == f"0{dia}"
                        else:
                            pass    
                        bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('T')} WHERE (COD_ESTACION = :estacion AND FECHA = :fecha)",
                    {"estacion": str(estacion), "fecha": f"{dia}/{mes}/{anio}"})
                        existreg = bd.fetchone()[0]
                        
                        if existreg < 48:
                            resultado.writerow([f"Falta {48 - existreg} registros en la base de datos en la fecha {dia}/{mes}/{anio}"])
                        else:
                            pass

                        if dia == num_dias_mes:
                            resultado.writerow([f"---"])
                        else:
                            pass

        elif frecuencia == "D":
            for rdia in range(1, num_dias_mes + 1):
                if len(str(rdia)) == 1:
                    dia = f"0{str(rdia)}"
                else:
                    dia = str(rdia)
                bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('D')} WHERE (COD_ESTACION = :estacion AND FECHA = :fecha)",
                           {"estacion": str(estacion), "fecha": f"{dia}/{mes}/{anio}"})
                numreg = bd.fetchone()[0]
                if numreg == 0:
                    resultado.writerow([f"Falta el registro en la base de datos en la fecha {dia}/{mes}/{anio}"])
                else:
                    pass

                
            resultado.writerow([f"---"])

        else:
            bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('M')} WHERE (COD_ESTACION = :estacion AND FECHA BETWEEN :inicio AND :fin)",
                       {"estacion": str(estacion), "inicio": f"01/{mes}/{anio}", "fin": f"{num_dias_mes}/{mes}/{anio}"})
            numreg = bd.fetchone()[0]
            if numreg == 0:
                resultado.writerow([f"Falta el registro en la base de datos de la fecha {dia}/{mes}/{anio}"])
            else:
                pass


def generarcsv_sql_API_csv(frecuencia, num_dias_mes,
        mes, anio, estacion, fichero,
        fecha_inicio, fecha_fin, bd,
        ):

    if frecuencia == "T":
        for dia in range(1, num_dias_mes + 1):
            if len(str(dia)) == 1:
                dia = f"0{dia}"
            if len(str(mes)) == 1:
                mes = f"0{mes}"
            filtros = {"fecha_inicio": f"{anio}-{mes}-{dia}", 
                        "fecha_fin": f"{anio}-{mes}-{dia}%2023:59:00", 
                        "parametro": "T", 
                        "funcion": "Med"}
            
            api_huecos_url = genera_url_datos_climaticos(estacion,
                                                    frecuencia,
                                                    **filtros
                                                    )

            resultado = requests.get(api_huecos_url)

            if resultado.ok:
                resultado = resultado.json() # Lo que nos interesa de la respuesta está en el json, contiene variable "count", "success" y "datos"
                if(resultado["success"]):
                    numero_registros = int(resultado["count"])
                    if numero_registros == 0:
                        for i in range(48):
                            # El formato de fecha que necesito para la consulta y la que quiero para el csv es diferente,
                            # por esa razón creo dos variable diferentes para hora
                            hora = datetime.strptime("23:30:00", "%H:%M:%S") - timedelta(minutes=30*i)
                            hora_bd = datetime.strftime(hora, "%H:%M")
                            hora = datetime.strftime(hora, "%H:%M:%S")
                            linea = [estacion, frecuencia, f"{anio}-{mes}-{dia} {hora}", "N"]
                            fecha_bd = datetime.strptime(f"{anio}-{mes}-{dia}", "%Y-%m-%d")
                            fecha_bd = datetime.strftime(fecha_bd, "%d/%m/%Y")
                            try:
                                bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('T')} WHERE COD_ESTACION = :estacion AND FECHA = :fecha AND HORA = :hora",
                                           {"estacion": str(estacion), "fecha": fecha_bd, "hora": hora_bd})
                                numreg = bd.fetchone()[0]
                                if numreg == 0:
                                    fichero.writerow((estacion, frecuencia, f"{anio}-{mes}-{dia} {hora}", "KO"))
                                else:
                                    fichero.writerow(linea)
                                
                            except:
                                print(fecha_bd)
                                print(hora)
                        
                    elif numero_registros < 30000:
                        
                        lista = []

                        resultadod = resultado["datos"]
                        # En caso de que solo haya un registro, el resultado es un diccionario,
                        # si hay más de uno, el resultado es una lista de diccionarios.
                        if isinstance(resultadod, dict):
                            resultadod = [resultadod]
                        
                        for i in resultadod:
                            fecha = str(i["fecha"])
                            res = fecha.split(" ")
                            lista.append(res[1])
                        
                        fecha_bd = str(resultadod[0]["fecha"])
                        res = fecha.split(" ")
                        fecha_bd = res[0]
                        fecha_bd = datetime.strptime(f"{anio}-{mes}-{dia}", "%Y-%m-%d")
                        fecha_bd = datetime.strftime(fecha_bd, "%d/%m/%Y")

                        horas_esperadas = []
                        t = datetime.strptime("23:30:00", "%H:%M:%S")

                        for i in range(48):
                            horas_esperadas.append(t.strftime("%H:%M:%S"))
                            t -= timedelta(minutes=30)

                        faltantes = [h for h in horas_esperadas if h not in lista]

                        for reg in faltantes:
                            hora = datetime.strptime(reg, "%H:%M:%S").strftime("%H:%M")
                            linea = [estacion, frecuencia, res[0] + " " + reg, "N"]
                            bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('T')} WHERE COD_ESTACION = :estacion AND FECHA = :fecha AND HORA = :hora",
                                       {"estacion": str(estacion), "fecha": str(fecha_bd), "hora": hora})
                            numreg = bd.fetchone()[0]
                            if numreg == 0:
                                fichero.writerow((estacion, frecuencia, f"{anio}-{mes}-{dia} {reg}", "KO"))
                            else:
                                fichero.writerow(linea)
                            
                    else:
                        print("Se supera el número máximo de registros, numero_registros = ",
                              numero_registros)
                        
                else:
                    print("Error al recibir los datos. str(res) = " + str(resultado))
                    if(DEBUG):
                        print(resultado)
                    else:
                        print(None)
            else:
                print("Error al comunicar con la API")
                if(DEBUG):
                    print(resultado)
                else:
                    print(None)

    elif frecuencia == "D":
        filtros = {"fecha_inicio": f"{fecha_inicio}", 
                    "fecha_fin": f"{fecha_fin}", 
                    "parametro": "T", 
                    "funcion": "Med"}
        
        api_huecos_url = genera_url_datos_climaticos(estacion,
                                                frecuencia, 
                                                **filtros
                                                )

        resultado = requests.get(api_huecos_url)

        if resultado.ok:
            resultado = resultado.json() # lo que nos interesa de la respuesta está en el json, contiene variable "count", "success" y "datos"
            if(resultado["success"]):
                numero_registros = int(resultado["count"])                    
                if numero_registros == 0:
                    for i in range(1, num_dias_mes + 1):
                        linea = [estacion, frecuencia, str(anio) + "-" + str(mes) 
                                 +  "-" + str(i) + " 00:00:00", "N"]
                        fecha_hora = datetime.strptime(str(anio) + "-" + str(mes) +  "-" + str(i), "%Y-%m-%d")
                        fecha = datetime.strftime(fecha_hora, "%Y-%m-%d")
                        fecha_hora = datetime.strftime(fecha_hora, "%d/%m/%Y")
                        bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('D')} WHERE COD_ESTACION = :estacion AND DAT01 = :fecha",
                                   {"estacion": str(estacion), "fecha": fecha_hora})
                        numreg = bd.fetchone()[0]
                        if numreg == 1:
                            fichero.writerow(fecha)
                        else:
                            fichero.writerow((estacion, frecuencia, fecha, "KO"))
                        
                elif numero_registros < 30000:
                    lista = []
                    lista_dias = []
                    resultado_datos = resultado["datos"]
                    
                    if isinstance(resultado_datos, dict):
                        resultado_datos = [resultado_datos]
                    
                    for i in resultado_datos:
                        fecha = str(i["fecha"])
                        res = fecha.split(" ")
                        resf = res[0]
                        resh = res[1]
                        lista.append(res)
                        resf = datetime.strptime(resf, "%Y-%m-%d")
                        lista.append(resf)
                        ref = resf.day
                        lista_dias.append(ref)
                        
                    for i in range(1, num_dias_mes + 1):
                        if i in lista_dias:
                            pass
                        else:
                            fecha = str(anio) + "-" + str(mes) + "-" + str(i)
                            fecha_hora = datetime.strptime(str(fecha), "%Y-%m-%d")
                            fecha = datetime.strftime(fecha_hora, "%Y-%m-%d")
                            fecha_hora = datetime.strftime(fecha_hora, "%d/%m/%Y")
                            linea = [estacion, frecuencia,
                                fecha, "N"
                                ]
                            bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('D')} WHERE COD_ESTACION = :estacion AND DAT01 = :fecha",
                                   {"estacion": str(estacion), "fecha": fecha_hora})
                            numreg = bd.fetchone()[0]
                            if numreg == 0:
                                fichero.writerow((estacion, frecuencia, fecha, "KO"))
                            else:
                                fichero.writerow(linea)
                            
                else:
                    print("Se supera el número máximo de registros, numero_registros = ", numero_registros)
                    
            else:
                print("Error al recibir los datos. str(res) = " + str(resultado))
                if(DEBUG):
                    print(resultado)
                else:
                    print(None)
        else:
            print("Error al comunicar con la API")
            if(DEBUG):
                print(resultado)
            else:
                print(None)
        
    else:
        filtros = {"fecha_inicio": f"{fecha_inicio}", 
                    "fecha_fin": f"{fecha_fin}", 
                    "parametro": "T", 
                    "funcion": "Med"}
        
        api_huecos_url = genera_url_datos_climaticos(estacion,
                                                frecuencia,
                                                **filtros
                                                )

        resultado = requests.get(api_huecos_url)

        if resultado.ok:
            resultado = resultado.json() # lo que nos interesa de la respuesta está en el json, contiene variable "count", "success" y "datos"
            if(resultado["success"]):
                numero_registros = int(resultado["count"])                    
                fecha_fin = fecha_fin.split(" ")
                fecha_fin_bd = datetime.strptime(str(fecha_fin[0]), "%Y-%m-%d")
                fecha_fin_bd = datetime.strftime(fecha_fin_bd, "%d-%m-%Y")
                if numero_registros == 0:
                    linea = [estacion, frecuencia, str(fecha_fin[0]), "N"]
                    bd.execute(f"SELECT COUNT(*) FROM {obtener_tabla('M')} WHERE COD_ESTACION = :estacion AND DAT01 = :fecha",
                               {"estacion": str(estacion), "fecha": fecha_fin_bd})
                    numreg = bd.fetchone()[0]
                    #print(fecha_fin_bd)
                    if numreg == 0:
                        fichero.writerow((estacion, frecuencia, fecha_fin[0], "KO"))
                    else:
                        fichero.writerow(linea) 
                else:
                    pass       
            else:
                print("Error al recibir los datos. str(res) = " + str(resultado))
                if(DEBUG):
                    print(resultado)
                else:
                    print(None)
        else:
            print("Error al comunicar con la API")
            if(DEBUG):
                print(resultado)
            else:
                print(None)