
# Diagnóstico de Retrasos y Reputación — Marketplace Olist (Brasil)

## Contexto y pregunta de negocio

Este proyecto analiza el dataset público real de Olist, la mayor marketplace
de e-commerce de Brasil (~99,441 pedidos, 2016-2018), con foco en logística
y su impacto en la reputación de los vendedores.

**Pregunta de negocio central**: ¿los retrasos en la entrega dañan la
reputación de los vendedores (medida en reseñas), y ese daño se concentra en
algo específico (categoría, región, vendedor) o es parejo en toda la
plataforma?

## Hallazgo 1: la tasa de retraso es baja, pero el problema es real cuando ocurre

- Sobre 96,470 pedidos entregados, el **6.77%** llegó después de la fecha
  estimada por Olist (6,534 pedidos).
- En promedio general, los pedidos llegan **11.9 días antes** de lo
  estimado — Olist calcula su fecha estimada con un margen de seguridad
  amplio, lo que mantiene la tasa de incumplimiento relativamente baja.

## Hallazgo 2: cuando hay retraso, es severo, no marginal

Tras excluir un artefacto de calidad de datos (ver Hallazgo 4):

- Retraso promedio: **10.1 días**
- Retraso mediano: **7 días**
- Retraso máximo (caso real verificado): **188 días**

## Hallazgo 3 (central): el retraso destruye la reputación — validado estadísticamente

| Categoría       | Pedidos | Review score promedio |
| ---------------- | ------- | --------------------- |
| A tiempo o antes | 89,443  | **4.29**        |
| Tarde            | 6,381   | **2.27**        |

La diferencia (4.29 vs. 2.27 — casi la mitad de la escala completa) se
validó con una prueba t de Student de dos muestras independientes:
**t = -100.76, p ≈ 0.0000000000** (prácticamente cero). La diferencia es
estadísticamente contundente, no atribuible al azar bajo ningún umbral
convencional.

**Nota metodológica**: para este cruce, los pedidos con más de una reseña
(ver Hallazgo 5) se consolidaron a una sola reseña por pedido, usando la
más reciente (`ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_creation_date DESC)`), bajo el criterio de que la opinión más
reciente refleja mejor la evaluación final del cliente.

## Hallazgo 4 (calidad de datos): artefacto de cierre masivo del sistema

Se detectó un grupo de 27 pedidos con fecha de entrega idéntica
(2017-09-19), originados en vendedores, estados de despacho y fechas de
envío al transportador no relacionadas entre sí (dispersas entre marzo y
junio de 2017) — un patrón incompatible con un proceso logístico real.

Se investigó una hipótesis inicial (relación con el paro nacional de
camioneros de Brasil, mayo de 2018) y se **descartó**: las fechas de compra
de estos pedidos cubren casi un año completo (junio 2017 – julio 2018),
incompatible con un evento puntual de 11 días.

Se interpreta como un **cierre masivo automatizado del sistema de Olist**
en esa fecha (posiblemente limpieza de pedidos "huérfanos" sin actualizar),
no como entregas físicas reales. Se verificó sistemáticamente que no existe
un segundo evento similar en el resto del dataset (la siguiente fecha con
mayor concentración de retrasos, 2018-05-07, tiene solo 11 pedidos con un
patrón gradual y decreciente, consistente con variación operativa normal).

Estos 27 casos se excluyeron del cálculo de severidad de retraso (Hallazgo
2), pero se mantienen en el cálculo de tasa general (Hallazgo 1), donde su
impacto proporcional es insignificante (0.03% del total).

## Hallazgo 5 (calidad de datos): reseñas múltiples por pedido

`order_reviews` tiene 104,719 filas para 99,441 pedidos. Se verificó que
los casos con más de una reseña por `order_id` corresponden a **fechas y
puntajes distintos** (no duplicación técnica de carga) — el cliente
actualizó su calificación en un momento posterior. Se resolvió quedándose
con la reseña más reciente por pedido para cualquier análisis que cruce
`orders` con `order_reviews`.

## Próximos pasos de análisis (confirmados, pendientes de ejecutar)

- [ ] **Cuello de botella real**: descomponer el tiempo total de entrega en
  "tiempo del vendedor en despachar" (compra → entrega al
  transportador) vs. "tiempo del transportador" (entrega al
  transportador → entrega al cliente), para identificar cuál de los
  dos tramos concentra el problema.
- [ ] **Flete vs. precio del producto**: identificar regiones donde el
  costo de envío (`freight_value`) representa una proporción
  desproporcionada frente al precio del producto (`price`).
- [ ] Segmentar la tasa de retraso por categoría de producto y por
  estado/región (geolocation), para confirmar si el problema se
  concentra en algo específico.
- [ ] Separar insatisfacción por logística vs. por calidad de producto
  (pedidos a tiempo con reseña baja).
- [ ] Modelo predictivo de riesgo de retraso (scikit-learn), usando
  variables disponibles al momento de la compra (distancia, categoría,
  peso, forma de pago).

## Recomendación

Los retrasos afectan a pocos pedidos pero destruyen la reputación (review de 2.27 vs. 4.29). Se recomienda, como prioridad, (1) implementar alertas tempranas con comunicación proactiva al cliente en pedidos en riesgo, y (2) incorporar el cumplimiento de plazos al scorecard de vendedores. La intervención definitiva (vendedor vs. transportador) debe definirse tras completar el análisis de cuello de botella.

## Limitaciones conocidas

- El dataset cubre 2016-2018 — no refleja necesariamente la operación
  actual de Olist.
- Un pequeño grupo de pedidos (27) se excluyó del análisis de severidad por
  ser un artefacto de sistema, no un comportamiento logístico real —
  documentado en el Hallazgo 4.
- El análisis de causa raíz del cuello de botella (vendedor vs.
  transportador) está pendiente de ejecutar.
