# Metodología de reconciliación

Registro de las decisiones de diseño del motor y de por qué se tomaron. Sirve para que quien retome el proyecto no repita los errores que ya costaron iteraciones.

## El error de fondo: una sola pregunta para dos problemas

Durante varias versiones el motor intentó responder con una sola lógica dos preguntas distintas:

1. **¿Cuál es la mejor correspondencia de este tag?** — competitiva, 1:1.
2. **¿Este tag existe?** — no competitiva, N:M.

Forzar la segunda a través de la primera producía falsos negativos sistemáticos: cuando varios tags comparten pantalla, el que "llega segundo" se quedaba sin candidato y se reportaba como inexistente, aunque estuviera perfectamente implementado.

La relación real en estos datos:

- 182 pantallas del tracking plan tienen más de un tag (`HomeAcciones` tiene 20, `Dashboard_NewUser` 12).
- En Analytics, 85 pantallas aparecen en varias filas (44% de la hoja). En Front End, 87 pantallas en 264 filas (56%).

Separar las dos preguntas fue el cambio que estabilizó los resultados.

## Errores medidos y corregidos

| Problema | Síntoma | Causa | Corrección |
|---|---|---|---|
| Falsos negativos por competencia | 295 "No encontrado", 47% con match real | Asignación 1:1 | Cobertura N:M |
| Filas imán | 8 tags en la misma fila de GA4 | Denominador dinámico con 2 campos genéricos | Piso de campos condicionado a evidencia |
| Colisiones infladas | 305 tags en colisión | `token_set_ratio` premia subconjuntos | `token_sort_ratio` (−21%) |
| Matches por nombre genérico | 97 sostenidos solo por `screen_analytics` | Campos clave tratados como equivalentes | Jerarquía: `screen_figma` manda |
| Tags distintos unificados | `AMP-4-1-002` casando con `AMP-1-0008` | ID de la fuente ignorado | Conflicto de ID como regla bloqueante |
| Huérfanos falsos | 54% de Analytics sin dueño | `matchedSet` solo guardaba al ganador | Barrido inverso, luego cobertura N:M |

## Calidad de las fuentes

Limitaciones que condicionan lo que el motor puede lograr:

**Analytics**
- El `ID` falta en el 64% de las filas.
- El 69% de los valores de `Object` son genéricos (`action_button`, `screen`), lo que impide distinguir eventos en una misma pantalla.

**Front End**
- El `id` falta en el 55% de las filas.
- Usa camelCase donde el plan usa snake_case.
- Declara la cobertura real de la implementación en `country` (`dynamic`, `cl, co, pe`), no el país del tag.

**Tracking plan**
- 218 de 828 tags no declaran `screen_analytics`.
- 61 no tienen ni pantalla ni screen_analytics: no son evaluables.

Mientras el `id_tag` no viaje en el payload de GA4 ni en el código, el fuzzy no es un lujo sino la única vía, y el techo de precisión seguirá acotado.

## Casos que conviene conocer

**1:N programático.** Una implementación paramétrica sirve a varios tags: `Profilling_Q$numQuestion` cubre las cinco preguntas de perfilamiento, `conditional_by_product` cubre el cash-in de cinco productos. No es duplicación y no debe consolidarse.

**Divergente ≠ inexistente.** Un tag cuyo `screen_analytics` no existe en las fuentes está correctamente marcado sin rastro: significa que ese evento nunca se implementó. La serie `KYC_*_Information_Completed` es el ejemplo — la pantalla existe, el evento de completado no.

**Conflicto de ID.** Cuando la pantalla coincide pero el ID de la fuente pertenece a otro tag, hay una disputa de gobierno entre squads. Son 46 casos que requieren decisión humana, no una regla.
