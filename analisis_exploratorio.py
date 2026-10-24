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
            f"El dataset no cumple el minimo exigido de 50.000 filas. Posee: {n_filas:,}"
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
    """Aplica deduplicacion, conversion de tipos, extraccion temporal y limpieza de formato."""
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
    df_limpio["positive"] = pd.to_numeric(df_limpio["positive"], errors="coerce").fillna(0)
    df_limpio["negative"] = pd.to_numeric(df_limpio["negative"], errors="coerce").fillna(0)
    df_limpio["average_playtime_forever"] = pd.to_numeric(
        df_limpio["average_playtime_forever"], errors="coerce"
    ).fillna(0)

    # 3. Derivacion de variables analiticas (Creamos ambos nombres para evitar KeyErrors)
    df_limpio["total_reviews"] = df_limpio["positive"] + df_limpio["negative"]
    horas_calc = (df_limpio["average_playtime_forever"] / 60.0).round(2)
    df_limpio["playtime_hours"] = horas_calc
    df_limpio["playtime_horas"] = horas_calc  # Cobertura total en español e inglés
    
    df_limpio["positive_ratio"] = np.where(
        df_limpio["total_reviews"] > 0,
        (df_limpio["positive"] / df_limpio["total_reviews"]) * 100,
        0,
    )

    # Extraccion de anio de lanzamiento
    col_fecha = "release_date" if "release_date" in df_limpio.columns else df_limpio.columns[2]
    df_limpio["release_year"] = pd.to_datetime(
        df_limpio[col_fecha], errors="coerce"
    ).dt.year

    # Limpieza estetica de textos en desarrolladores y géneros
    if "developers" in df_limpio.columns:
        df_limpio["developers"] = (
            df_limpio["developers"]
            .astype(str)
            .str.replace(r"[\[\]\"']", "", regex=True)
            .str.strip()
        )

    col_genero = "genres" if "genres" in df_limpio.columns else "genre"
    if col_genero in df_limpio.columns:
        df_limpio[col_genero] = (
            df_limpio[col_genero]
            .astype(str)
            .str.replace(r"[\{\}\[\]\"']", "", regex=True)
            .str.replace("description:", "", regex=False)
            .str.replace("id:", "", regex=False)
            .str.strip()
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

    print(f"Registros finales listos para analisis: {filas_post_filtro:,} juegos.")
    print("[OK] Trazabilidad y estadisticas descriptivas guardadas.")
    return df_filtrado


def responder_preguntas_y_graficar(df):
    """Responde las 5 preguntas de negocio, genera tablas CSV y 5 figuras PNG limpias."""
    print("\n" + "=" * 60)
    print("4. GENERACION DE RESULTADOS (TABLAS Y FIGURAS)")
    print("=" * 60)

    # -------------------------------------------------------------
    # PREGUNTA 1: Top 10 juegos con mayor tiempo promedio en horas
    # -------------------------------------------------------------
    cols_p1 = ["name", "playtime_hours", "total_reviews", "price"]
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
    plt.title("Figura 1: Top 10 Juegos con Mayor Tiempo Promedio de Juego (En Horas)", fontsize=13)
    plt.xlabel("Tiempo Promedio de Juego (Horas)", fontsize=11)
    plt.ylabel("Título del Videojuego", fontsize=11)
    for i, row in top10_horas.iterrows():
        plt.text(row["playtime_hours"] + 2, i, f"{row['playtime_hours']:.1f} hrs", va="center", fontsize=9)
    plt.xlim(0, top10_horas["playtime_hours"].max() * 1.15)
    plt.savefig(os.path.join(DIR_FIGURAS, "figura1_top10_horas_promedio.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] P1 procesada -> 'figura1' y 'tabla_p1' guardadas.")

    # -------------------------------------------------------------
    # PREGUNTA 2: Desarrolladores con mas juegos en el Top 100
    # -------------------------------------------------------------
    top100_juegos = df.dropna(subset=["developers"]).nlargest(100, "total_reviews")
    top_devs = top100_juegos["developers"].value_counts().head(8).reset_index()
    top_devs.columns = ["developer", "juegos_en_top100"]
    top_devs.to_csv(
        os.path.join(DIR_TABLAS, "tabla_p2_top_desarrolladores_top100.csv"), index=False
    )

    plt.figure(figsize=(10, 5))
    sns.barplot(
        data=top_devs,
        y="developer",
        x="juegos_en_top100",
        palette="crest",
        edgecolor="black",
    )
    plt.title("Figura 2: Desarrolladores con Mayor Presencia en el Top 100 de Juegos Evaluados", fontsize=13)
    plt.xlabel("Cantidad de Títulos Dentro del Top 100", fontsize=11)
    plt.ylabel("Desarrollador / Estudio", fontsize=11)
    for i, row in top_devs.iterrows():
        plt.text(row["juegos_en_top100"] + 0.1, i, f"{row['juegos_en_top100']}", va="center", fontsize=10)
    plt.xlim(0, top_devs["juegos_en_top100"].max() + 1)
    plt.savefig(os.path.join(DIR_FIGURAS, "figura2_desarrolladores_top100.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] P2 procesada -> 'figura2' y 'tabla_p2' guardadas.")

    # -------------------------------------------------------------
    # PREGUNTA 3: Juegos de menos de 20 USD con mas reseñas positivas
    # -------------------------------------------------------------
    juegos_accesibles = df[(df["price"] > 0) & (df["price"] < 20)]
    cols_p3 = ["name", "positive", "price", "positive_ratio"]
    top10_economicos = (
        juegos_accesibles.dropna(subset=["name"])
        .nlargest(10, "positive")[cols_p3]
        .reset_index(drop=True)
    )
    top10_economicos.to_csv(
        os.path.join(DIR_TABLAS, "tabla_p3_top10_economicos_positivas.csv"), index=False
    )

    plt.figure(figsize=(11, 6))
    sns.barplot(
        data=top10_economicos,
        y="name",
        x="positive",
        palette="mako",
        edgecolor="black",
    )
    plt.title("Figura 3: Top 10 Videojuegos de Menos de 20 USD con Mayor Volumen de Reseñas Positivas", fontsize=13)
    plt.xlabel("Cantidad Total de Reseñas Positivas", fontsize=11)
    plt.ylabel("Título del Videojuego", fontsize=11)
    for i, row in top10_economicos.iterrows():
        plt.text(row["positive"] * 1.01, i, f"{row['positive']:,} (USD {row['price']})", va="center", fontsize=9)
    plt.xlim(0, top10_economicos["positive"].max() * 1.25)
    plt.savefig(os.path.join(DIR_FIGURAS, "figura3_top10_economicos_positivas.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] P3 procesada -> 'figura3' y 'tabla_p3' guardadas.")

    # -------------------------------------------------------------
    # PREGUNTA 4: Géneros con mayor porcentaje de reseñas positivas (LIMPIO)
    # -------------------------------------------------------------
    col_genero = "genres" if "genres" in df.columns else "genre"
    df_generos = df.dropna(subset=[col_genero, "positive_ratio"]).copy()
    
    df_generos[col_genero] = df_generos[col_genero].astype(str).str.replace(",", ";").str.split(";")
    df_generos = df_generos.explode(col_genero)
    
    # Función para limpiar caracteres técnicos, comillas, corchetes y descartar números puros (IDs)
    def limpiar_genero(txt):
        t = pd.Series([txt]).str.replace(r'[\{\}\[\]"\'_:]', '', regex=True).values[0]
        t = t.replace('id', '').replace('description', '').strip()
        if t.isdigit() or t == '' or len(t) <= 1:
            return None
        return t

    df_generos["genero_limpio"] = df_generos[col_genero].apply(limpiar_genero)
    df_generos = df_generos.dropna(subset=["genero_limpio"])

    top_generos = (
        df_generos.groupby("genero_limpio")
        .agg({"positive_ratio": "mean", "total_reviews": "count"})
        .rename(columns={"total_reviews": "cantidad_juegos"})
        .reset_index()
    )
    
    top_generos = top_generos[top_generos["cantidad_juegos"] >= 5].nlargest(10, "positive_ratio")
    top_generos.to_csv(
        os.path.join(DIR_TABLAS, "tabla_p4_top_generos_positivos.csv"), index=False
    )

    plt.figure(figsize=(11, 6))
    sns.barplot(
        data=top_generos,
        y="genero_limpio",
        x="positive_ratio",
        palette="viridis",
        edgecolor="black",
    )
    plt.title("Figura 4: Géneros de Videojuegos con Mayor Porcentaje Promedio de Reseñas Positivas", fontsize=13)
    plt.xlabel("Porcentaje Promedio de Reseñas Positivas (%)", fontsize=11)
    plt.ylabel("Género", fontsize=11)
    for i, row in top_generos.reset_index(drop=True).iterrows():
        plt.text(row["positive_ratio"] + 0.5, i, f"{row['positive_ratio']:.1f}%", va="center", fontsize=9)
    plt.xlim(0, 105)
    plt.savefig(os.path.join(DIR_FIGURAS, "figura4_generos_positivos.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] P4 procesada -> 'figura4' y 'tabla_p4' guardadas.")

    # -------------------------------------------------------------
    # PREGUNTA 5: Juego mejor valorado de cada año (últimos 20 años)
    # -------------------------------------------------------------
    df_anios = df.dropna(subset=["release_year", "name"]).copy()
    df_anios["release_year"] = df_anios["release_year"].astype(int)
    
    df_recientes = df_anios[(df_anios["release_year"] >= 2006) & (df_anios["release_year"] <= 2026)]
    
    idx_mejores = df_recientes.groupby("release_year")["positive_ratio"].idxmax()
    mejores_por_anio = df_recientes.loc[idx_mejores, ["release_year", "name", "positive_ratio", "total_reviews"]]
    mejores_por_anio = mejores_por_anio.sort_values("release_year", ascending=False).reset_index(drop=True)
    
    mejores_por_anio.to_csv(
        os.path.join(DIR_TABLAS, "tabla_p5_mejor_juego_por_anio.csv"), index=False
    )

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=mejores_por_anio,
        x="release_year",
        y="positive_ratio",
        marker="o",
        color="teal",
        linewidth=2.5,
        markersize=8,
    )
    plt.title("Figura 5: Evolución del Porcentaje de Reseñas Positivas del Juego Líder por Año (Últimos 20 Años)", fontsize=13)
    plt.xlabel("Año de Lanzamiento", fontsize=11)
    plt.ylabel("Porcentaje de Reseñas Positivas (%)", fontsize=11)
    plt.ylim(50, 105)
    plt.savefig(os.path.join(DIR_FIGURAS, "figura5_mejor_juego_por_anio.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] P5 procesada -> 'figura5' y 'tabla_p5' guardadas.")

def main():
    inicializar_entorno()
    df_crudo = cargar_datos(RUTA_STEAM_GAMES)
    diagnostico_calidad(df_crudo)
    df_filtrado = limpieza_y_preparacion(df_crudo)
    responder_preguntas_y_graficar(df_filtrado)
    print("\n[PROCESO TERMINADO] Tablas y figuras guardadas exitosamente.")


if __name__ == "__main__":
    main()