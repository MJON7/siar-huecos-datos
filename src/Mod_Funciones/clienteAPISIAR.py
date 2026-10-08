# ESPACIO DE TRABAJO
#-*-coding:utf-8-*- # CODIFICACION

"""

    Incluye todas las funciones necesarias para consultar todos los servicios de 
    la API del SIAR, ver: https://www.larioja.org/larioja-client/cm/agricultura/images?idMmedia=1499039
    
"""

__author__ = "SIAR-GOBIERNO DE LA RIOJA"
__copyright__ = ""
__credits__ =["Joaquín Huete", "Vanessa Tobar", "Alejandro Daniel Bucur Bucur"]
__license__ = "MIT"
__version__ = "0.1"
__email__ = "siar.cida@larioja.org"
__status__ = "Desarrollo"

# CONSTANTES
API_URL_ROOT = "https://ias1.larioja.org/apiSiar/servicios/v2/"
DEBUG = False # Debug = True devuelve valores respuesta API en caso de error
            # Debug = False devuelve None cuando no comunica bien con la API

# Cargar bibliotecas y módulos

import math 
import requests # peticiones html
from datetime import datetime, timedelta


# FUNCIONES AUXILIARES !!! a archivo cas_funciones_auxiliares.py
def extrae_num_maximo_registros() -> int:
    """ Obtiene el núm. máx. de registros que la API SIAR devuelve en una única peticion"""
    api_url = API_URL_ROOT + "numero-maximo-registros"
    res = requests.get(api_url)
    
    if res.ok:
        res = res.json()
        return int(res["numero-maximo-registros"])
    else:
        if DEBUG:
            print("Se devuelve salida de la API sin procesar")
            return res
        else:
            print("Error al comunicar con la API")
            return None


def extrae_funciones_agregacion(extrae_abreviatura: bool = False) -> list:
    """ 
    genera lista de diccionarios con la respuesta del servicio ./funciones-agregacion
    si extrae_abreviatura = True, simplifica respuesta y devuelve lista de str con
    abreviaturas posibles de esta variable al extraer datos climaticos
    """
    api_url = API_URL_ROOT + "funciones-agregacion"
    
    res = requests.get(api_url)
    
    if res.ok:
        res = res.json()
        res = res["funciones"]
        if extrae_abreviatura:
            abreviatura = []
            for i in range(0, len(res)):
                abreviatura.append(res[i]["abreviatura"])
            return abreviatura
        else:
            return res
    else:
        print("Error al comunicar con la API http.status != 200")
        if DEBUG:
            print("Se devuelve salida de la API sin procesar")
            return res
        else:
            return None


def existe_funcion(abreviatura: str) -> bool:
    """ Permite consultar si una abreviatura de función existe"""
    abreviaturas_posibles = extrae_funciones_agregacion(True)
    for i in abreviaturas_posibles:
        if i == abreviatura:
            return True
    return False


def extrae_parametros(extrae_abreviatura: bool = False) -> list:
    """ 
    genera lista de diccionarios con la respuesta del servicio ./parametros
    si extrae_abreviatura = True, simplifica respuesta y devuelve lista de str con
    abreviaturas posibles para esta variable al extraer datos climaticos
    """
    api_url = API_URL_ROOT + "parametros"
    
    res = requests.get(api_url)
    
    if res.ok:
        res = res.json()
        res = res["parametros"]
        if extrae_abreviatura:
            abreviatura = []
            for i in range(0, len(res)):
                abreviatura.append(res[i]["abreviatura"])
            return abreviatura
        else:
            return res
    else:
        print("Error al comunicar con la API http.status != 200")
        if DEBUG:
            print("Se devuelve salida de la API sin procesar")
            return res
        else:
            return None


def existe_parametro(abreviatura: str) -> bool:
    """ Permite consultar si una abreviatura de parametro existe"""
    abreviaturas_posibles = extrae_parametros(True)
    for i in abreviaturas_posibles:
        if i == abreviatura: return True
    return False


def extrae_frecuencias(extrae_abreviatura: bool = False) -> list:
    """ 
    genera lista de diccionarios con la respuesta del servicio ./frecuencias
    si extrae_abreviatura = True, simplifica respuesta y devuelve lista de str con
    abreviaturas posibles para esta variable al extraer datos climaticos
    """

    api_url = API_URL_ROOT + "frecuencias"
    
    res = requests.get(api_url)
    
    if res.ok:
        res = res.json()
        res = res["frecuencias"]
        if extrae_abreviatura:
            abreviatura = []
            for i in range(0, len(res)):
                abreviatura.append(res[i]["abreviatura"])
            return abreviatura
        else:
            return res 

    else:
        print("Error al comunicar con la API http.status != 200")
        if(DEBUG):
            print("Se devuelve salida de la API sin procesar")
            return res
        else:
            return None


def existe_frecuencia(abreviatura: str) -> bool:
    """ Permite consultar si una abreviatura de frecuencia existe"""
    abreviaturas_posibles = extrae_frecuencias(True)
    for i in abreviaturas_posibles:
        if(i == abreviatura): return True
    return False


def extrae_posiciones(extrae_abreviatura: bool = False) -> list:
    """ 
    genera lista de diccionarios con la respuesta del servicio ./posiciones
    si extrae_abreviatura = True, simplifica respuesta y devuelve lista de str con
    abreviaturas posibles para esta variable al extraer datos climaticos
    """

    api_url = API_URL_ROOT + "posiciones"
    
    res = requests.get(api_url)
    
    if res.ok:
        res = res.json()
        res = res["posiciones"]
        if extrae_abreviatura:
            abreviatura = []
            for i in range(0, len(res)):
                abreviatura.append(res[i]["abreviatura"])
            return abreviatura
        else:
            return res

    else:
        print("Error al comunicar con la API http.status != 200")
        if DEBUG:
            print("Se devuelve salida de la API sin procesar")
            return res
        else:
            return None


def existe_posicion(abreviatura: str) -> bool:
    """ Permite consultar si una abreviatura de posición existe"""
    abreviaturas_posibles = extrae_posiciones(True)
    for i in abreviaturas_posibles:
        if(i == abreviatura): return True
    return False


# DEFINICION ADICIONAL DE OTRAS CONSTANTES ÚTILES
if True: #!!!main == __name__:
    NUMERO_MAXIMO_REGISTROS = extrae_num_maximo_registros()
    FUNCIONES_AGREGACION = extrae_funciones_agregacion()
    PARAMETROS = extrae_parametros()
    FRECUENCIAS = extrae_frecuencias()
    POSICIONES = extrae_posiciones()


# FUNCIONES MÉTODO ESTACIONES #!!! A archivo cas_funciones_servicio_estaciones.py
def extrae_estaciones(extrae_codigos: bool = False, codigo_estacion: str = None) -> list:
    """ 
    genera lista de diccionarios con la respuesta del servicio ./estaciones
    si extrae_abreviatura = True, simplifica respuesta y devuelve lista de str con
    los codigo_estacion válidos para esta variable al extraer datos climaticos
    """
    api_url = API_URL_ROOT + "estaciones"
    if(codigo_estacion is not None):
        api_url = API_URL_ROOT + "estaciones/" + codigo_estacion
    
    res = requests.get(api_url)
    
    if res.ok:
        res = res.json()
        res = res["estaciones"]
        if extrae_codigos:
            codigo_estacion = list()  #[]
            for i in range(0, len(res)):
                codigo_estacion.append(res[i]["codigo_estacion"])
            return codigo_estacion
        else:
            return res

    else:
        print("Error al comunicar con la API http.status != 200")
        if DEBUG:
            print("Se devuelve salida de la API sin procesar")
            return res
        else:
            return None


def existe_estacion(codigo_estacion: str) -> bool:
    """ Permite consultar si una codigo_estación existe"""
    codigos_posibles = extrae_estaciones(True)
    for i in codigos_posibles:
        if(i == str(codigo_estacion)): return True #conversion de tipo porque el valor de la API se registra como str
    return False


def extraer_primera_fecha(estacion: str, frecuencia: str) -> str:
    res = extrae_estaciones(extrae_codigos = False, codigo_estacion = estacion)
    if res is None:
        return None
    if frecuencia == 'T':
        return res["fecha_primer_semihorario"]
    else:
        return res["fecha_primer_diario"]


def extraer_ultima_fecha(estacion: str, frecuencia: str) -> str:
    res = extrae_estaciones(extrae_codigos = False, codigo_estacion = estacion)
    if res is None:
        return None
    if frecuencia == 'T':
        return res["fecha_ultimo_semihorario"] # comprobar sintaxis
    else:
        return res["fecha_ultimo_diario"] # comprobar sintaxis


#FUNCIONES EXTRACCIÓN DATOS CLIMÁTICOS # a módulo cas_funciones_extraccion_datos.py
def genera_url_datos_climaticos(estacion: str, frecuencia: str, **filtros: dict):
    """
    Es función auxiliar de extrae_datos_climaticos_API()
    
    La url a la que se envía la petición descarta los valores de filtros no válidos
    en esta primera version no se analizan en esta funcion si los filtros son ok
    Ej de la variable filtros = {fecha_inicio: "2015-06-02", funcion = "Max"}, 
    ver manual API los filtros aceptados
    """
    
    api_url = API_URL_ROOT + "datos-climaticos/" + str(estacion) + "/" + frecuencia # Creamos URL según manual API
    
    if len(filtros) > 0: # probar esta función sin esta condición, si len = 0 (la variable filtro no está definida / está vacía funciona?¿?¿?)
        char_union = "?" # Si hay un filtro se usa el caracter "?" para separar la sintaxis de la consulta principal de los filtros
        for key, value in filtros.items():
            api_url = api_url + char_union + key + "=" + value
            char_union = "&" # Después del primer filtro, si hay otros, se encadenan con "&"
    
    return(api_url)


def extrae_datos_climaticos_API(estacion: str, frecuencia: str, **filtros: dict):
    """
        Obtiene la respuesta de la apisiar. Si es correcta devuelve los datos (según la descripción del objeto de respuesta descritos en manual)
        Si es incorrecta puede ser por dos razones:
            - La API responde OK pero hay exceso de parámetros en la respuesta !!! PENDIENTE DE AÑADIR RECURSIVIDAD
            - La API responde OK pero hay algún otro error (???PUEDE SUCEDER???,un caso es que los filtros añadidos hagan que la respuesta contenga 0 registros)
            - Error de comunicación con la API (!!!Pendiente gestionar excepción)

        Observaciones:
    """

    api_url = genera_url_datos_climaticos(estacion, frecuencia,  **filtros)
    res = requests.get(api_url) # conectamos con esa url método GET y guardamos el contenido en la variable res
    
    if res.ok:
        res = res.json() # lo que nos interesa de la respuesta está en el json, contiene variable "count", "success" y "datos"
        if(res["success"]):
            numero_registros = int(res["count"])
            if numero_registros == 0:
                print("Ningun dato disponible. str(res) = " + str(res))
                return(None)
            elif numero_registros < NUMERO_MAXIMO_REGISTROS:
                return(res)["datos"]
            else:
                print("Se supera el número máximo de registros, numero_registros = ", numero_registros)
                return(extrae_datos_climaticos_exceso_registros(numero_registros, estacion, frecuencia, **filtros))
        else:
            print("Error al recibir los datos. str(res) = " + str(res))
            if(DEBUG):
                return(res)
            else:
                return(None)
    else:
        print("Error al comunicar con la API")
        if(DEBUG):
            return(res)
        else:
            return(None)


def extrae_datos_climaticos_exceso_registros(numero_registros, estacion, frecuencia, **filtros):
    # chequear si existen filtros de fecha_inicio y/o fecha_fin
    fecha_inicio = None
    fecha_fin = None
    for key, value in filtros.items():
        if key == fecha_inicio: fecha_inicio = value
        if key == fecha_fin: fecha_fin = value
    
    # si no existen añadir fecha_inicio y fin para usarlos como filtros 
    if(fecha_inicio == None): fecha_inicio = extraer_primera_fecha(estacion, frecuencia)
    if(fecha_fin == None): fecha_fin = extraer_ultima_fecha(estacion, frecuencia)

    #calcular el número de peticiones necesarias y otros parámetros útiles:
    numero_peticiones = math.ceil(numero_registros/NUMERO_MAXIMO_REGISTROS)
    
    diferencia = datetime.strptime(fecha_inicio, '%Y-%m-%d') - datetime.strptime(fecha_fin, '%Y-%m-%d %H:%M:%S')

    amplitud_intervalo_fechas = round(diferencia.total_seconds() / numero_peticiones) 
    amplitud_intervalo_en_dias = math.floor(amplitud_intervalo_fechas / (3600 * 24))

    # rehacemos la variable filtros para eliminar fecha_inicio y fecha_fin
    exclude_keys = ['fecha_inicio', 'fecha_fin'] # https://stackoverflow.com/questions/8717395/retain-all-entries-except-for-one-key-python
    filtros_nuevo = {k: filtros[k] for k in set(list(filtros.keys())) - set(exclude_keys)}
    
    f_ini = fecha_inicio
    datos = []
    for i in range(0, numero_peticiones):
        f_fin = datetime.strptime(f_ini, '%Y-%m-%d') + amplitud_intervalo_en_dias * 3600 * 24
        f_fin = datetime.strptime(f_fin, '%Y-%m-%d')
        filtros_nuevo['fecha_inicio'] = f_ini
        filtros_nuevo['fecha_fin'] = f_fin
        datos.append(extrae_datos_climaticos_API(estacion, frecuencia, filtros_nuevo))
        f_ini = f_fin
    
    return(datos)


def filtra_datos_validos(response, incluir_datos_Sospechosos = False, valor_por_defecto_si_no_valido = ""):
    """
    Este es un primer borrador de esta función, modifica la salida para simplificarla, 
    la modificación está adaptada a los usos comunes de los datos extraidos
    desde la API
    """
    datos_validados = []
    #!!! si solo tiene un valor, da fallos, usar otra forma para gestionar el json
    if  isinstance(response, dict): # si solo tiene un registro, es un diccionario
        dato_valido = response["dato_valido"]
        
        if dato_valido == "V":
            valor = response["valor"]
        elif (incluir_datos_Sospechosos and dato_valido == "S"):
            valor = response["valor"]
        #elif (valor_por_defecto_si_no_valido != ""):
        #    valor = valor_por_defecto_si_no_valido
        else:
            valor = valor_por_defecto_si_no_valido
            
        datos_validados.append({"parametro": response["parametro"],
                                "funcion_agregacion": response["funcion_agregacion"],
                                "fecha": response["fecha"],
                                "valor": valor})
    else:
        for i in range(0, len(response)):
            dato_valido = response[i]["dato_valido"]
        
            if dato_valido == "V":
                valor = response[i]["valor"]
            elif (incluir_datos_Sospechosos and dato_valido == "S"):
                valor = response[i]["valor"]
            #elif (valor_por_defecto_si_no_valido != ""):
            #    valor = valor_por_defecto_si_no_valido
            else:
                valor = valor_por_defecto_si_no_valido
            
            datos_validados.append({"parametro": response[i]["parametro"],
                                "funcion_agregacion": response[i]["funcion_agregacion"],
                                "fecha": response[i]["fecha"],
                                "valor": valor})
    
    return(datos_validados)


def extrae_datos_parametro(datos_brutos, parametro):
    """
        Dada un objeto de salida con el formato de la apisiar o el formato simplificado tras función filtra_datos
        extrae del objeto aquellos registros cuyo parámetro sea el solicitado
    """
    datos_filtrados = []
    for i in range(0, len(datos_brutos)):
        if datos_brutos[i]["parametro"] == parametro:
            datos_filtrados.append(datos_brutos[i])
    
    return(datos_filtrados)


def tiempo_cronometro(inicio, final):

    pasar = "%Y-%m-%d %H:%M:%S.%f" #Este será el formato con el que convertiré las fechas
    
    inicio = datetime.strptime(inicio, pasar)
    final = datetime.strptime(final, pasar)
    cronometro = final -inicio

    totals = int(cronometro.total_seconds())
    horas = totals // 3600 
    minutos = (totals % 3600) // 60 
    segundos = totals % 60
    dias = cronometro.days

    return f"{dias} dias : {horas} horas : {minutos} minutos : {segundos} segundos"


def obtencion_API(frecuencia, num_dias_mes,
        mes,anio, estacion, fichero,
        fecha_inicio, fecha_fin,
        ):
    if frecuencia == "T":
        for dia in range(1, num_dias_mes + 1):
            # La API requiere un formato de fecha YYYY-MM-DD. Adimos un 0 a los días y meses menores de 10
            if len(str(dia)) == 1:
                dia = f"0{dia}"
            if len(str(mes)) == 1:
                mes = f"0{mes}"
            # Usamos el siguiente filtro para obtener unos registros específicos de la API
            filtros = {"fecha_inicio": f"{anio}-{mes}-{dia}", 
                        "fecha_fin": f"{anio}-{mes}-{dia}%2023:59:00", 
                        "parametro": "T", 
                        "funcion": "Med"}
            
            api_huecos_url = genera_url_datos_climaticos(estacion,
                                                    frecuencia,
                                                    **filtros
                                                    )

            resultado = requests.get(api_huecos_url)

            if resultado.ok: # Si la respuesta de la API es correcta, se procesa el resultado
                resultado = resultado.json() # Lo que nos interesa de la respuesta está en el json
                if(resultado["success"]):
                    numero_registros = int(resultado["count"])
                    if numero_registros == 0:
                        print("Ningun dato disponible. str(res) = " + str(resultado))
                    elif numero_registros < 30000:
                        
                        lista = []

                        resultadod = resultado["datos"]
                        # Si solo tiene un registro, es un diccionario, lo convertimos a lista
                        if isinstance(resultadod, dict):
                            resultadod = [resultadod]
                        
                        for i in resultadod:
                            fecha = str(i["fecha"])
                            res = fecha.split(" ")
                            lista.append(res[1])
                        
                        horas_esperadas = []
                        t = datetime.strptime("23:30:00", "%H:%M:%S")

                        for i in range(48):
                            horas_esperadas.append(t.strftime("%H:%M:%S"))
                            t -= timedelta(minutes=30)
                        
                        faltantes = [h for h in horas_esperadas if h not in lista]
                        for reg in faltantes:
                            linea = [estacion, frecuencia, res[0] + " " + reg, "El registro no se encuentra en la API"]
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
            resultado = resultado.json() # lo que nos interesa de la respuesta está en el json
            if(resultado["success"]):
                numero_registros = int(resultado["count"])                    
                
                if numero_registros == 0:
                    # Si no hay registros, se añaden todos los días del mes como huecos
                    for i in range(1, num_dias_mes + 1):
                        linea = [estacion, frecuencia, str(anio) + "-" + str(mes) 
                                 +  "-" + str(i) + " 00:00:00", "El registro no se encuentra en la API"]
                        fichero.writerow(linea)

                elif numero_registros < 30000:
                    
                    lista = []

                    resultado_datos = resultado["datos"]
                    
                    if isinstance(resultado_datos, dict):
                        resultado_datos = [resultado_datos]
                    
                    for i in resultado_datos:
                        fecha = str(i["fecha"])
                        res = fecha.split(" ")
                        resf = res[0]
                        resh = res[1]
                        lista.append(res)
                        res = datetime.strptime(resf, "%Y-%m-%d")
                        res_dia = res.day
                        lista.append(res_dia)
                    
                    for i in range(1, num_dias_mes + 1):
                        if i in lista:
                            pass
                        else:
                            linea = [estacion, frecuencia,
                                resf + " " + resh, "El registro no se encuentra en la API"
                                ]
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
                if numero_registros == 0:
                    linea = [estacion, frecuencia, str(fecha_fin[0]), "El registro no se encuentra en la API"]
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