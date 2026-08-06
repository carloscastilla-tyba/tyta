# tyta

Agente de tagging de Tyba. Herramientas para gobernar el ciclo de vida de los tags de analítica: saneamiento del inventario existente y, más adelante, creación asistida de tags nuevos.

---

## El problema

Los tags de Tyba se documentan a mano, en una hoja de cálculo distinta por squad. Nadie ve el inventario completo antes de crear un tag nuevo, y ningún campo se valida al escribirlo. El resultado, medido sobre el inventario real de 690 tags:

| | |
|---|---|
| Tags que hay que consolidar (miden lo mismo) | 224 |
| Tags que requieren revisión | 316 |
| Tags a eliminar | 54 |
| **Tags correctos y en uso** | **96 (14%)** |

Dos causas, ambas del momento de la creación:

- **Redundancia** — 50 tags son el mismo tag con IDs distintos entre squads y 17 son copias exactas. El flujo de KYC está instrumentado dos veces, en los rangos `AMP-5` y `AMP-9`.
- **Error humano** — 148 nombres de evento no cumplen `lowercase_snake_case` (GA4 trata `kyc` y `KYC` como eventos distintos), 50 IDs quedaron fuera del rango de su squad, 223 valores de país están sin normalizar y 166 enlaces apuntan a nodos de Figma que ya no existen.

El costo agregado: 4,65 millones de eventos (19% del tráfico) disparan desde pantallas que no están en el código documentado, y no se pueden construir funnels de conversión confiables.

---

## Qué hay hoy en este repo

### `index.html` — Árbol de saneamiento

Explorador autónomo del inventario. Un solo archivo, sin dependencias: se abre en cualquier navegador.

**Cuatro ejes de exploración**

- Producto → evento → pantalla
- Evento → producto → pantalla
- Use case → evento → pantalla
- Pantalla de Figma → evento → producto

**Filtros** por estado (eliminar, consolidar, revisar, se queda), producto, recomendación, buscador, y atajos para ver solo colisiones o solo tags con el nodo de Figma borrado.

**Panel de detalle** por tag: definición, trazabilidad (fila exacta en Analytics y en Front End, volumen de eventos, estado de Figma), con qué otros tags colisiona, su use case y el siguiente paso concreto.

### `data/tags.json`

Los 690 tags con su veredicto, para reutilizar desde otras herramientas.

---

## Cómo se construye el veredicto

Cada tag del inventario se compara **campo por campo** contra las dos fuentes de verdad:

- **Analytics** — 728 filas (456 tras deduplicar)
- **Front End** — 498 filas

Campos comparados: `event`, `screen_figma`, `screen_analytics`, `object`, `object_text`, `country`, `product`.

Tres decisiones de diseño que importan:

1. **Denominador dinámico.** Analytics no tiene `object_text`, `country` ni `product`, así que solo se exigen los campos que ambas fuentes comparten. El score es el promedio ponderado de los campos comparables, no de todos.
2. **`token_sort_ratio`, no `token_set_ratio`.** El segundo devuelve 100% cuando los tokens de una cadena son subconjunto de la otra, y hacía que `Cashin_Investment_PE` casara perfecto con `Cashin_SummaryInvestmentFFMM_PE`. Cambiarlo redujo las colisiones un 21% sin perder precisión.
3. **Ranking y presencia separados.** `screen_figma` se usa para elegir el mejor candidato (peso calibrado en 0.6–0.9 contra verdad de terreno), pero la decisión de "existe o no" se toma sobre el campo clave del candidato elegido.

Precisión medida sobre los tags con ID único en ambas fuentes: **80% en Analytics**.

---

## Roadmap

El árbol resuelve la mitad del problema: hace visible lo que ya existe. La otra mitad es evitar que nazcan tags malos.

**Siguiente:** interfaz de creación asistida.

- Ningún campo crítico en texto libre. Producto, flujo, pantalla, objeto y país se eligen de listas cerradas; la pantalla se sincroniza desde Figma, así que solo se pueden elegir nodos vivos.
- El ID se genera según el rango del squad (`Fury AMP-1`, `Banner AMP-4`, `Barton AMP-5`, `Rogers AMP-6`, `Loki AMP-7`, `Thor AMP-9`, `Natasha AMP-15`).
- El nombre se compone solo con el patrón `Flujo_Paso_Estado`.
- **Huella como índice único en base de datos** (`flujo + pantalla + objeto + país`). Mueve el chequeo de duplicados desde una auditoría posterior con fuzzy matching a una restricción de unicidad en el momento de crear, donde es trivial y no falla.

Fuera del alcance de esa fase: edición masiva de tags existentes, implementación en código, dashboards de métricas y el modelo de funnels.
