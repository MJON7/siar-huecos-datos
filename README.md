# API SIAR - Gestión de Registros Climáticos

## Descripción General

Conjunto de scripts en Python diseñados para gestionar la sincronización de registros climáticos entre la **API SIAR** (Sistema de Información Agroclimática de La Rioja) y la **base de datos Oracle**. El proyecto identifica, busca y envía los registros faltantes con el objetivo de mantener la integridad de los datos climáticos.

## Estructura del Proyecto

### Módulos Principales (`src/Mod_Funciones/`)

#### `clienteAPISIAR.py`
Módulo que contiene todas las funciones necesarias para:
- Conectar y consultar los servicios de la API SIAR
- Buscar huecos de datos en los registros de la API
- Gestionar diferentes frecuencias (horaria "T", diaria "D", mensual "M")
- Procesar parámetros, funciones de agregación y estaciones disponibles
- Funciones auxiliares para cálculo de registros y validación de datos

**Funciones clave:**
- `obtencion_API()`: Obtiene registros de la API y detecta huecos
- `contar_numero_registros()`: Cuenta registros disponibles con filtros específicos
- `extrae_estaciones()`: Obtiene listado de estaciones disponibles
- `extrae_frecuencias()`: Obtiene frecuencias disponibles en la API
- `tiempo_cronometro()`: Mide el tiempo de ejecución

#### `clienteBDSIAR.py`
Módulo que contiene funciones para:
- Conectar y consultar la base de datos Oracle (credenciales centralizadas)
- Generar búsquedas en las tablas de datos horarios, diarios y mensuales de la base de datos
- Comparar registros entre API y BD
- Generar archivos CSV con información detallada

**Funciones clave:**
- `conectar_bd_oracle()`: Establece conexión a la BD Oracle según el servidor
- `generarcsv_sql_API_csv()`: Busca registros en BD y genera CSV con resultados
- `comparacion()`: Compara registros entre API y BD

### Scripts de Ejecución Principales

#### `Obtencion_SQL_API_CSV.py` ⭐ **RECOMENDADO (Más Detallado)**
**Propósito:** Identificar y gestionar registros faltantes en la API con máximo detalle.

**Proceso:**
1. Busca registros faltantes en la API según los rangos de fechas especificados
2. Para cada registro faltante hallado en la API, busca en la base de datos
3. Si está en la BD → escribe "**N**" en el CSV (pendiente de envío/revalidación)
4. Si NO está en la BD → escribe "**KO**" en el CSV (registro no existe)
5. Si está completo en la API → no añade la entrada (sin hueco)

**Salida:** Genera archivo `Registros_Faltantes.csv` con estructura:
```
Estación;Frecuencia;Fecha/Hora;Estado
501;T;2005-01-01 00:00:00;KO
501;T;2005-03-27 02:30:00;N
```

**Ventajas:**
- **Máxima precisión:** Especifica **hora exacta** de cada registro faltante
- **Información de BD:** Distingue entre registros faltantes en API pero en BD (N) vs. inexistentes (KO)
- **Localización exacta:** Facilita búsqueda y validación manual si es necesario
- **Procesable:** El tercero script `reenvio_sql_API.py` usa este archivo para revalidar registros

**Parámetros configurables:** (ajustables en el código)
- Rango de fechas a analizar
- Frecuencias a verificar (T, D, M)
- Estaciones específicas o todas

---

#### `reenvio_sql_API.py` ⭐ **RECOMENDADO**
**Propósito:** Enviar/revalidar registros faltantes identificados previamente.

**Proceso:**
1. Lee el archivo `Registros_Faltantes.csv`
2. Para cada registro con estado "**N**":
   - Busca el registro en la base de datos
   - Marca como revalidado/reenviado (cambia estado a "**OK**")
3. Registros con estado diferente a "N" → se omiten
4. **Límite de seguridad:** Configurable en el código (por defecto 500 modificaciones por ejecución para evitar sobrecargas)

**Archivo requerido:** `Registros_Faltantes.csv` (generado por `Obtencion_SQL_API_CSV.py`)

**Recomendación:** Programar ejecuciones periódicas (ej. diarias o semanales) para procesamiento incremental sin sobrecargar el servidor.

---

### Scripts Informativos (Secundarios)

#### `Huecos_Datos_APISIAR.py`
**Propósito:** Generar resumen visual y compacto de huecos de datos por mes.

**Salida:** Archivo `resultado_analisis_huecoDatos_APIV01.csv` mostrando:
```
Estacion,frecuencia,Mes/anio,Observaciones,num_registros_faltantes
501,T,1/2005,Faltan 1 registros,1
501,T,2/2005,OK,0
511,T,11/2005,Faltan 415 registros,415
```

**Características:**
- **Agregado por mes:** Resumen de toda la integridad de datos mensualmente
- **Más visual:** Formato compacto ideal para dashboards o reportes rápidos
- **Sin detalle de fechas/horas:** Solo conteo total por mes
- **Rápida lectura:** Identifica meses/estaciones con problemas a golpe de vista

**Utilidad:** Visión general rápida del estado de la integridad de datos; ideal para detectar patrones mensuales

---

#### `Comparacion_API_BD.py` ⭐ **RECOMENDADO (Más Visual)**
**Propósito:** Comparar registros faltantes entre la API y la base de datos de forma visual y compacta.

**Salida:** Genera archivo `Comparacion_huecoDatos_API.csv` con análisis detallado y delimitador `|`:
```
501 | T | 1/2005 | Hay mas o los mismos registros que provienen de la base de datos que de la API: faltan API 1, BD 1
Falta 1 registros en la base de datos en la fecha 1/1/2005
---
```

**Análisis:**
- Identifica discrepancias entre sistemas a nivel de **mes y fecha** (sin hora exacta)
- Muestra la diferencia de conteos: "faltan API X, BD Y"
- Detecta inconsistencias e incoherencias entre fuentes de datos
- Agrupa por separadores "---" para mejor legibilidad

**Ventajas:**
- **Visual:** Formato compacto y fácil de leer
- **Comparativa:** Muestra claramente diferencias API vs BD
- **Resumen:** Agrupa por mes, menos verboso que `Obtencion_SQL_API_CSV.py`
- **Casos edge:** Detecta anomalías como "API tiene datos pero BD está vacía" o viceversa

---

#### `Estado_Datos_API.py`
**Propósito:** Analizar registros faltantes en la API generando archivo con timestamp.

**Salida:** Genera archivo `ReenvioAPI_{DD-MM-AAAA}_{HH-MM-SS}.csv` con estructura:
```
501,T,2005-01-01 00:00:00,El registro no se encuentra en la API
```

**Características:**
- Similar a `Obtencion_SQL_API_CSV.py` pero **sin verificar en Base de Datos**
- Muestra solo huecos de la API (no diferencia si existen en BD o no)
- Genera archivo con **timestamp único** en cada ejecución
- Menos informativo que `Obtencion_SQL_API_CSV.py` (sin estados KO/N)

**Nota:** Para obtener información más completa sobre si los registros existen en BD, usar `Obtencion_SQL_API_CSV.py`.

---

#### `Reset_OK.py`
**Propósito:** Resetear registros marcados como "OK" de vuelta a "N" en el CSV de registros faltantes.

**Proceso:**
1. Lee el archivo `Registros_Faltantes.csv`
2. Cambia todos los registros con estado "**OK**" a "**N**"
3. Sobrescribe el archivo con los cambios

**Utilidad:** Permite reprocesar registros que ya fueron marcados como enviados, útil para pruebas o correcciones.

---

## Comparativa de Scripts Principales

| Característica | `Obtencion_SQL_API_CSV.py` | `Comparacion_API_BD.py` | `Huecos_Datos_APISIAR.py` |
|---------------|---------------------------|------------------------|-------------------------|
| **Propósito** | Identifica registros SIN enviar | Compara API vs BD visualmente | Resumen mensual |
| **Granularidad** | ⏰ Hora exacta | 📅 Fecha (sin hora) | 📊 Mes completo |
| **Verifica BD** | ✅ Sí (KO/N) | ✅ Sí (conteo) | ❌ No |
| **Salida** | Detallada/Procesable | Compacta/Visual | Visual/Resumen |
| **Ideal para** | Revalidar con `reenvio_sql_API.py` | Auditoría y análisis | Dashboards y reportes |
| **Volumen datos** | 📈 Mayor | 📊 Medio | 📉 Menor |

**Recomendación:**
- **Buscar problemas específicos:** Usar `Obtencion_SQL_API_CSV.py` (máxima precisión)
- **Auditoría rápida:** Usar `Comparacion_API_BD.py` (visual y compacto)
- **Reportes ejecutivos:** Usar `Huecos_Datos_APISIAR.py` (resumen mensual)

---

## Flujo de Trabajo Recomendado

```
Ejecutar Obtencion_SQL_API_CSV.py
↓
Revisar archivo Registros_Faltantes.csv
↓
Ejecutar reenvio_sql_API.py (máximo 500 registros por ejecución)
↓
[OPCIONAL] Ejecutar scripts informativos para análisis
↓
Repetir en intervalos regulares (programar ejecución periódica)
```


## Requisitos

- **Python 3.x**
- **oracledb** - Conexión a base de datos Oracle
- **requests** - Consultas HTTP a la API SIAR
- **oracle-client** - Cliente Oracle instalado en el servidor
- **Variables de entorno configuradas:**
  - `ORACLE_CLIENT` - Ruta al cliente Oracle
  - `ORACLE_CONFIG` - Ruta de configuración Oracle
  - `ORACLE_WALLET` - Ruta del wallet de credenciales
  - `SERVIDOR_PRODUCCION` / `SERVIDOR_DESARROLLO` - Nombres de host de cada entorno
  - `DSN_PROD_L`, `DSN_DESA_L`, `DSN_PROD_R`, `DSN_DESA_R` - Nombres de servicio (DSN) de Oracle
  - `TABLA_HORARIA`, `TABLA_DIARIA`, `TABLA_MENSUAL` - Tablas de la BD para cada frecuencia (formato `ESQUEMA.TABLA`)

Copia `.env.example` a `.env` y rellena los valores. Ver `requirements.txt` para lista completa de dependencias.

## Configuración

### Conexión a Base de Datos
La conexión a la base de datos Oracle está centralizada en la función `conectar_bd_oracle()` del módulo `clienteBDSIAR.py`. El proyecto detecta automáticamente el servidor y conecta a la base de datos correspondiente:
- **Servidor de desarrollo** (`SERVIDOR_DESARROLLO`) → conecta con el DSN de desarrollo local o de producción remoto
- **Servidor de producción** (`SERVIDOR_PRODUCCION`) → conecta con el DSN de producción local o de desarrollo remoto

Los nombres de servidor y los DSN se definen en el archivo `.env` (ver `.env.example`).

Las credenciales se obtienen del wallet de Oracle configurado en las variables de entorno.

### Tablas y seguridad de las consultas
- Los nombres de las tablas no están en el código: se leen del `.env` mediante la función `obtener_tabla()` de `clienteBDSIAR.py`, que además valida su formato.
- Los valores de las consultas (estación, fecha, hora) se pasan como **variables enlazadas** (`:estacion`, `:fecha`...), nunca concatenados en el SQL, para evitar inyección SQL.

### Frecuencias Soportadas

| Código | Descripción        | Intervalo      |
|--------|-------------------|----------------|
| **T**  | Horaria (Trihoraria) | Cada 30 min  |
| **D**  | Diaria            | 1 registro/día |
| **M**  | Mensual           | 1 registro/mes |

### Parámetros API

- **Parámetro analizado:** Temperatura media (T)
- **Función de agregación:** Media (Med)

## Características Importantes

✅ **Automatización:** Permite programación de ejecuciones periódicas  
✅ **Límite de seguridad:** Configurable en el código (por defecto 500 registros por ejecución para evitar sobrecargas)  
✅ **Detección inteligente:** Busca en API → luego en BD si no encuentra  
✅ **Trazabilidad:** Genera CSV con registro detallado de cada operación  
✅ **Multi-servidor:** Soporte para entornos de desarrollo y producción  
✅ **Gestión de huecos:** Identifica exactamente cuándo y dónde faltan datos  