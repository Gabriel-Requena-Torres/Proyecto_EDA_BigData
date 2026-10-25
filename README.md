# Análisis Exploratorio de Datos (EDA) - Catálogo de Videojuegos en Steam

Este proyecto consiste en un análisis exploratorio de datos reproducible sobre el catálogo de videojuegos de la plataforma Steam. El desarrollo se realizó en Python y tiene como objetivo responder preguntas analíticas sobre tiempos de juego, presencia de estudios desarrolladores, impacto de títulos económicos, géneros destacados y la evolución histórica de los videojuegos mejor valorados.

---

## 1. Descripción del Proyecto

El flujo de trabajo toma un archivo masivo de videojuegos, diagnostica su calidad original, aplica transformaciones técnicas y establece un filtro global de representatividad estadística (títulos con al menos 1.000 reseñas acumuladas). A partir de este subconjunto consistente, genera automáticamente tablas de resumen numérico en formato CSV y gráficos estadísticos en formato PNG guardados a 300 DPI.

---

## 2. Requisitos Previos

* Sistema operativo Linux, Windows o macOS.
* Python 3.10 o superior instalado.
* Gestor de paquetes `pip` actualizado.
* Git para control de versiones.

---

## 3. Descarga y Ubicación de los Datos

Por restricciones técnicas de almacenamiento en repositorios de GitHub (límite de 100 MB por archivo), el dataset no se incluye en el control de versiones.

1. Descarga el conjunto de datos desde Kaggle:  
   **Dataset:** [Steam Games Dataset Daily Updates (por Hubert Sidorowicz)](https://www.kaggle.com/datasets/hubertsidorowicz/steam-games-dataset-daily-updates?resource=download)
2. Descomprime el archivo descargado y extrae `steam_games.csv`.
3. Crea la estructura de carpetas necesaria y coloca el archivo en la siguiente ruta exacta:

```text
Proyecto_EDA/
└── Datos/
    └── archive/
        └── steam_games.csv
```
---

## 4. Estructura del Directorio

```text
Proyecto_EDA/
├── Datos/
│   ├── archive/                          # Directorio local para steam_games.csv (ignorado por Git)
│   └── resultados/                       # Directorio autogenerado con salidas del análisis
│       ├── figuras/                      # Gráficos analíticos generados (.png a 300 DPI)
│       └── tablas/                       # Reportes y tablas de resumen generadas (.csv)
├── .gitignore                            # Reglas de exclusión para Git
├── README.md                             # Documentación general del repositorio
├── analisis_exploratorio.py              # Script principal con el pipeline de limpieza y análisis
└── requirements.txt
```

## 5. Instalación y Configuración del Entorno

Abre una terminal en la raíz del proyecto (Proyecto_EDA/) y sigue estos pasos:

### Paso 1: Crear y activar el entorno virtual

* En Linux o MacOS: 
```text 
python3 -m venv .venv
source .venv/bin/activate
```

* En Windows (PowerShell):
```text
python -m venv .venv
.venv\Scripts\Activate.ps1
```
* En Windows (CMD):
```text
python -m venv .venv
.venv\Scripts\activate.bat
```

### Paso 2: Instalar dependencias

Con el entorno virtual activo, actualiza pip e instala los paquetes necesarios:

```text 
pip install --upgrade pip
pip install -r requirements.txt
```

Las dependencias que se usaron para este proyecto son: 

* pandas
* numpy
* matplotlib
* seaborn

## 6. Ejecución del Script

Verifica que el entorno virtual siga activado (debe mostrar el prefijo (.venv)) y ejecuta:

* En Linux: 
```text 
python3 analisis_exploratorio.py
```
* En Windows: 
```text 
python analisis_exploratorio.py
```
## 7. Salidas y Resultados Generados

El script ejecuta cuatro etapas principales y deposita los resultados en Datos/resultados/:

### Tablas de Datos: 

* diagnostico_calidad.csv: Conteo y porcentaje de valores nulos por columna antes de limpiar.

* registro_limpieza_trazabilidad.csv: Conteo de filas iniciales, descartadas por duplicados y filtradas por el umbral de representatividad.

* estadistica_descriptiva_numerica.csv: Medidas de resumen estadístico (media, desviación estándar, cuartiles, mínimos y máximos) del conjunto final.

* tabla_p1_top10_horas_promedio.csv: Top 10 títulos con mayor cantidad de tiempo de juego promedio registrado.

* tabla_p2_top_desarrolladores_top100.csv: Cantidad de títulos por desarrollador presentes dentro de los 100 juegos más evaluados.

* tabla_p3_top10_economicos_positivas.csv: Top 10 juegos de pago menores a 20 USD ordenados por reseñas positivas.

* tabla_p4_top_generos_positivos.csv: Categorías y géneros con mayor tasa promedio de aprobación.

* tabla_p5_mejor_juego_por_anio.csv: Juego líder en porcentaje de reseñas positivas por cada año evaluado.

### Figuras y Gráficos:

* figura1_top10_horas_promedio.png: Gráfico de barras con los 10 juegos con mayor tiempo promedio de juego (en horas).

* figura2_desarrolladores_top100.png: Gráfico de barras con los estudios predominantes dentro del Top 100.

* figura3_top10_economicos_positivas.png: Gráfico de barras horizontales de títulos accesibles más aclamados.

* figura4_generos_positivos.png: Gráfico comparativo de la tasa de aprobación promedio según género.

* figura5_mejor_juego_por_anio.png: Gráfico de línea con la trayectoria de valoración de los títulos líderes por año.