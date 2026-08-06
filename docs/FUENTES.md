# Fuentes de datos

El veredicto de cada tag sale de cruzar tres fuentes. Ninguna se modifica desde este repo.

| Fuente | Filas | Rol |
|---|---|---|
| Tagging Consolidado | 690 | La definición oficial de cada tag. Es lo que se audita. |
| Analytics (GA4) | 728 (456 deduplicadas) | Qué dispara realmente y con qué volumen. |
| Front End | 498 | Qué está implementado en el código. |

## Calidad conocida de cada fuente

**Analytics**
- El `ID` falta en el 64% de las filas (467). Es el hueco principal.
- 272 filas (37%) eran duplicados exactos; se colapsan preservando el volumen (24.224.823 eventos).
- El 69% de los valores de `Object` son genéricos (`action_button`, `screen`, `button`), lo que hace que muchos tags compitan por la misma fila.
- Ninguna fila tiene 0 eventos: todo lo que está ahí está vivo.

**Front End**
- El `id` falta en el 55% de las filas.
- Usa camelCase en el 85% de `object`, mientras Analytics usa snake_case en el 82%. Son convenciones incompatibles entre sí, y por eso el cruce necesita fuzzy.
- 71 valores de `screenFigma` traen placeholders dinámicos (`$country`, `(param)`) que hay que normalizar antes de comparar.

**Cruce directo entre las dos** (sin pasar por el consolidado)

| | Claves únicas |
|---|---|
| En ambas | 203 |
| Solo en Front End | 169 |
| Solo en Analytics | 208 |

De las 169 que solo están en Front End, 73 tienen equivalente difuso en Analytics: disparan con otro nombre.
