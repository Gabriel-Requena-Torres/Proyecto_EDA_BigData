import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Configuracion visual y semilla de reproducibilidad
sns.set_theme(style="whitegrid")
np.random.seed(521)

# Rutas del proyecto
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_DATOS = os.path.join(DIR_BASE, "Datos")
DIR_ARCHIVE = os.path.join(DIR_DATOS, "archive")
RUTA_STEAM_GAMES = os.path.join(DIR_ARCHIVE, "steam_games.csv")

DIR_RESULTADOS = os.path.join(DIR_DATOS, "resultados")
DIR_TABLAS = os.path.join(DIR_RESULTADOS, "tablas")
DIR_FIGURAS = os.path.join(DIR_RESULTADOS, "figuras")


def inicializar_entorno():
  """Crea las carpetas de salida si no existen."""
  os.makedirs(DIR_TABLAS, exist_ok=True)
  os.makedirs(DIR_FIGURAS, exist_ok=True)


def cargar_datos(ruta_archivo):
  """Carga el dataset y valida que supere el minimo inicial de 50.000 filas."""
  print("=" * 60)
  print("1. CARGA DE DATOS")
  print("=" * 60)

  if not os.path.exists(ruta_archivo):
    raise FileNotFoundError(f"No se encontro el archivo en: {ruta_archivo}")

  df = pd.read_csv(ruta_archivo, low_memory=False)
  n_filas, n_cols = df.shape
  print(f"Dimensiones iniciales: {n_filas:,} filas y {n_cols} columnas.")

  if n_filas < 50000:
    raise ValueError(
        f"El dataset no cumple el minimo exigido de 50.000 filas. Posee:"
        f" {n_filas:,}"
    )

  return df


def diagnostico_calidad(df):
  """Genera reporte de nulos y duplicados antes de limpiar."""
  print("\n" + "=" * 60)
  print("2. DIAGNOSTICO DE CALIDAD")
  print("=" * 60)

  n_filas = len(df)
  duplicados = df.duplicated().sum()
  print(f"Filas duplicadas exactas detectadas: {duplicados:,}")

  conteo_nulos = df.isnull().sum()
  pct_nulos = (conteo_nulos / n_filas) * 100

  reporte_calidad = pd.DataFrame({
      "columna": df.columns,
      "valores_nulos": conteo_nulos,
      "porcentaje_nulos": pct_nulos.round(2),
  }).reset_index(drop=True)

  reporte_calidad.to_csv(
      os.path.join(DIR_TABLAS, "diagnostico_calidad.csv"), index=False
  )
  print("[OK] Tabla 'diagnostico_calidad.csv' guardada.")
  return reporte_calidad


def limpieza_y_preparacion(df):
  """Aplica deduplicacion, conversion de tipos y filtro global de representatividad."""
  print("\n" + "=" * 60)
  print("3. LIMPIEZA Y PREPARACION DE DATOS")
  print("=" * 60)

  filas_iniciales = len(df)
  trazabilidad = []

  # 1. Deduplicacion
  df_limpio = df.drop_duplicates().copy()
  filas_post_dedup = len(df_limpio)
  trazabilidad.append({
      "paso": "Eliminacion de duplicados exactos",
      "filas_resultantes": filas_post_dedup,
      "filas_excluidas": filas_iniciales - filas_post_dedup,
  })

  # 2. Conversion de columnas numericas
  df_limpio["price"] = pd.to_numeric(df_limpio["price"], errors="coerce")
  df_limpio["positive"] = pd.to_numeric(
      df_limpio["positive"], errors="coerce"
  ).fillna(0)
  df_limpio["negative"] = pd.to_numeric(
      df_limpio["negative"], errors="coerce"
  ).fillna(0)
  df_limpio["average_playtime_forever"] = pd.to_numeric(
      df_limpio["average_playtime_forever"], errors="coerce"
  ).fillna(0)

  # 3. Derivacion de variables analiticas
  df_limpio["total_reviews"] = df_limpio["positive"] + df_limpio["negative"]
  df_limpio["playtime_hours"] = (
      df_limpio["average_playtime_forever"] / 60.0
  ).round(2)
  df_limpio["positive_ratio"] = np.where(
      df_limpio["total_reviews"] > 0,
      (df_limpio["positive"] / df_limpio["total_reviews"]) * 100,
      0,
  )

  # 4. Filtro global de representatividad (>= 1.000 resenas totales)
  filas_pre_filtro = len(df_limpio)
  df_filtrado = df_limpio[df_limpio["total_reviews"] >= 1000].copy()
  filas_post_filtro = len(df_filtrado)

  trazabilidad.append({
      "paso": "Filtro representatividad (total_reviews >= 1000)",
      "filas_resultantes": filas_post_filtro,
      "filas_excluidas": filas_pre_filtro - filas_post_filtro,
  })

  # Guardar trazabilidad
  df_trazabilidad = pd.DataFrame(trazabilidad)
  df_trazabilidad.to_csv(
      os.path.join(DIR_TABLAS, "registro_limpieza_trazabilidad.csv"), index=False
  )

  # Estadistica descriptiva numerica del conjunto filtrado
  df_filtrado.describe().T.to_csv(
      os.path.join(DIR_TABLAS, "estadistica_descriptiva_numerica.csv")
  )

  print(
      f"Registros finales listos para analisis: {filas_post_filtro:,} juegos."
  )
  print("[OK] Trazabilidad y estadisticas descriptivas guardadas.")
  return df_filtrado


def responder_preguntas_y_graficar(df):
  """Responde cada pregunta de negocio, genera su tabla CSV y su figura PNG."""
  print("\n" + "=" * 60)
  print("4. GENERACION DE RESULTADOS (TABLAS Y FIGURAS)")
  print("=" * 60)

  # -------------------------------------------------------------
  # PREGUNTA 1: Top 10 juegos con mayor tiempo promedio en horas
  # -------------------------------------------------------------
  cols_p1 = [
      "name",
      "playtime_hours",
      "average_playtime_forever",
      "total_reviews",
      "price",
  ]
  top10_horas = (
      df.dropna(subset=["name"])
      .nlargest(10, "playtime_hours")[cols_p1]
      .reset_index(drop=True)
  )

  top10_horas.to_csv(
      os.path.join(DIR_TABLAS, "tabla_p1_top10_horas_promedio.csv"), index=False
  )

  plt.figure(figsize=(11, 6))
  sns.barplot(
      data=top10_horas,
      y="name",
      x="playtime_hours",
      palette="Blues_r",
      edgecolor="black",
  )
  plt.title(
      "Figura 1: Top 10 Juegos con Mayor Tiempo Promedio de Juego (En Horas)",
      fontsize=13,
  )
  plt.xlabel("Tiempo Promedio de Juego (Horas)", fontsize=11)
  plt.ylabel("Titulo del Videojuego", fontsize=11)

  for i, row in top10_horas.iterrows():
    plt.text(
        row["playtime_hours"] + 2,
        i,
        f"{row['playtime_hours']:.1f} hrs",
        va="center",
        fontsize=10,
    )

  plt.xlim(0, top10_horas["playtime_hours"].max() * 1.15)
  plt.savefig(
      os.path.join(DIR_FIGURAS, "figura1_top10_horas_promedio.png"),
      dpi=300,
      bbox_inches="tight",
  )
  plt.close()
  print("[OK] P1 procesada -> 'figura1' y 'tabla_p1' guardadas.")

  # -------------------------------------------------------------
  # PREGUNTA 2: Desarrolladores con mas juegos en el Top 100 de resenas
  # -------------------------------------------------------------
  top100_juegos = df.dropna(subset=["developers"]).nlargest(
      100, "total_reviews"
  )
  top_devs = (
      top100_juegos["developers"].value_counts().head(8).reset_index()
  )  # Top 8 para evitar barras unitarias
  top_devs.columns = ["developer", "juegos_en_top100"]

  top_devs.to_csv(
      os.path.join(DIR_TABLAS, "tabla_p2_top_desarrolladores_top100.csv"),
      index=False,
  )

  plt.figure(figsize=(10, 5))
  sns.barplot(
      data=top_devs,
      y="developer",
      x="juegos_en_top100",
      palette="crest",
      edgecolor="black",
  )
  plt.title(
      "Figura 2: Desarrolladores con Mayor Presencia en el Top 100 de Juegos"
      " Evaluados",
      fontsize=13,
  )
  plt.xlabel("Cantidad de Titulos Dentro del Top 100", fontsize=11)
  plt.ylabel("Desarrollador / Estudio", fontsize=11)

  for i, row in top_devs.iterrows():
    plt.text(
        row["juegos_en_top100"] + 0.1,
        i,
        f"{row['juegos_en_top100']}",
        va="center",
        fontsize=10,
    )

  plt.xlim(0, top_devs["juegos_en_top100"].max() + 1)
  plt.savefig(
      os.path.join(DIR_FIGURAS, "figura2_desarrolladores_top100.png"),
      dpi=300,
      bbox_inches="tight",
  )
  plt.close()
  print("[OK] P2 procesada -> 'figura2' y 'tabla_p2' guardadas.")

  # -------------------------------------------------------------
  # PREGUNTA 3: Juegos de menos de 20 USD con mayor cantidad de resenas positivas
  # -------------------------------------------------------------
  # Excluimos juegos gratuitos (price > 0) para enfocarnos en compras accesibles
  juegos_accesibles = df[(df["price"] > 0) & (df["price"] < 20)]
  cols_p3 = ["name", "positive", "price", "positive_ratio"]
  top10_economicos = (
      juegos_accesibles.dropna(subset=["name"])
      .nlargest(10, "positive")[cols_p3]
      .reset_index(drop=True)
  )

  top10_economicos.to_csv(
      os.path.join(DIR_TABLAS, "tabla_p3_top10_economicos_positivas.csv"),
      index=False,
  )

  plt.figure(figsize=(11, 6))
  sns.barplot(
      data=top10_economicos,
      y="name",
      x="positive",
      palette="mako",
      edgecolor="black",
  )
  plt.title(
      "Figura 3: Top 10 Videojuegos de Menos de 20 USD con Mayor Volumen de"
      " Resenas Positivas",
      fontsize=13,
  )
  plt.xlabel("Cantidad Total de Resenas Positivas", fontsize=11)
  plt.ylabel("Titulo del Videojuego", fontsize=11)

  for i, row in top10_economicos.iterrows():
    plt.text(
        row["positive"] * 1.01,
        i,
        f"{row['positive']:,} (USD {row['price']})",
        va="center",
        fontsize=9,
    )

  plt.xlim(0, top10_economicos["positive"].max() * 1.25)
  plt.savefig(
      os.path.join(DIR_FIGURAS, "figura3_top10_economicos_positivas.png"),
      dpi=300,
      bbox_inches="tight",
  )
  plt.close()
  print("[OK] P3 procesada -> 'figura3' y 'tabla_p3' guardadas.")


def main():
  inicializar_entorno()
  df_crudo = cargar_datos(RUTA_STEAM_GAMES)
  diagnostico_calidad(df_crudo)
  df_filtrado = limpieza_y_preparacion(df_crudo)
  responder_preguntas_y_graficar(df_filtrado)
  print("\n[PROCESO TERMINADO] Tablas y figuras guardadas exitosamente.")


if __name__ == "__main__":
  main()