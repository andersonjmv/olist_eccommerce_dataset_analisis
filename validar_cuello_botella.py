import pandas as pd
from scipy.stats import ttest_ind
from google.cloud import bigquery

PROJECT_ID = "rutaxpress-analytics"  

client = bigquery.Client(project=PROJECT_ID)

query = """
SELECT
    order_id,
    DATE_DIFF(DATE(order_delivered_customer_date), DATE(order_estimated_delivery_date), DAY) AS dias_vs_estimado,
    DATE_DIFF(DATE(order_delivered_carrier_date), DATE(order_purchase_timestamp), DAY) AS dias_vendedor,
    DATE_DIFF(DATE(order_delivered_customer_date), DATE(order_delivered_carrier_date), DAY) AS dias_transportador
FROM olist_analytics.orders
WHERE order_status = 'delivered'
    AND order_delivered_carrier_date IS NOT NULL
    AND order_delivered_customer_date IS NOT NULL
    AND DATE(order_delivered_customer_date) != '2017-09-19'
"""

print("Consultando BigQuery...")
df = client.query(query).to_dataframe()

df["categoria"] = df["dias_vs_estimado"].apply(lambda x: "tarde" if x > 0 else "a_tiempo")

grupo_tarde = df[df["categoria"] == "tarde"]
grupo_a_tiempo = df[df["categoria"] == "a_tiempo"]

print(f"\nTamaño de muestra: tarde={len(grupo_tarde)}, a_tiempo={len(grupo_a_tiempo)}")


t_transportador, p_transportador = ttest_ind(
    grupo_tarde["dias_transportador"], grupo_a_tiempo["dias_transportador"], equal_var=False
)
print(f"\n--- Tramo TRANSPORTADOR ---")
print(f"Promedio tarde: {grupo_tarde['dias_transportador'].mean():.2f} días")
print(f"Promedio a tiempo: {grupo_a_tiempo['dias_transportador'].mean():.2f} días")
print(f"T-statistic: {t_transportador:.2f}, P-valor: {p_transportador:.10f}")

t_vendedor, p_vendedor = ttest_ind(
    grupo_tarde["dias_vendedor"], grupo_a_tiempo["dias_vendedor"], equal_var=False
)
print(f"\n--- Tramo VENDEDOR ---")
print(f"Promedio tarde: {grupo_tarde['dias_vendedor'].mean():.2f} días")
print(f"Promedio a tiempo: {grupo_a_tiempo['dias_vendedor'].mean():.2f} días")
print(f"T-statistic: {t_vendedor:.2f}, P-valor: {p_vendedor:.10f}")

print(f"\n--- Comparación de magnitud del efecto (t-statistic) ---")
print(f"Transportador: {abs(t_transportador):.1f}  |  Vendedor: {abs(t_vendedor):.1f}")
if abs(t_transportador) > abs(t_vendedor):
    print("=> El tramo del TRANSPORTADOR muestra una asociación más fuerte con el retraso.")
else:
    print("=> El tramo del VENDEDOR muestra una asociación más fuerte con el retraso.")