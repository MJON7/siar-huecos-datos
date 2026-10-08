import csv # Para trabajar con archivos CSV

NOMBRE_ARCHIVO_RESULTADOS = "./Registros_Faltantes.csv" 
""" Asegúrate de que la ruta al archivo CSV, 
    el cual contiene los registros faltantes obtenidos
    con el script Obtencion_SQL_API_CSV.py, sea correcta
"""

lista_filas = [] # Lista para almacenar las filas modificadas. Luego se asignará a la variable "registros" para escribir en el archivo CSV

with open(NOMBRE_ARCHIVO_RESULTADOS, "r", encoding="utf-8") as f:
    registros = csv.reader(f, delimiter=";") # El delimitador es ";" porque el archivo CSV tiene el formato europeo
    for fila_registro in registros:
        if fila_registro[3] == "OK": # Solo se modificarán los registros que tengan un "N" en la columna 4, el cual indica que debe ser exportado
            fila_registro[3] = "N"
            lista_filas.append(fila_registro)
        else:
            lista_filas.append(fila_registro)

# Abrir el archivo CSV en modo escritura para escribir las filas modificadas
with open(NOMBRE_ARCHIVO_RESULTADOS, "w", newline="", encoding="utf-8") as f:
    registros = csv.writer(f, delimiter=";")
    registros.writerows(lista_filas) # Escribo las filas modificadas en el archivo CSV. El delimitador es ";" porque el archivo CSV tiene el formato europeo