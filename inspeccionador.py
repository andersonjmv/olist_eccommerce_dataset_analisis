import pandas as pd
import os

carpeta = "data/raw"

for archivo in sorted(os.listdir(carpeta)):
    if archivo.endswith(".csv"):
        ruta = os.path.join(carpeta, archivo)
        df = pd.read_csv(ruta, nrows=5)
        total_filas = sum(1 for _ in open(ruta, encoding="utf-8")) - 1  # -1 por el header
        print(f"\n=== {archivo} ===")
        print(f"Filas totales: {total_filas}")
        print(f"Columnas: {df.columns.tolist()}")