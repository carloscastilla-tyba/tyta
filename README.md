# tyta

Agente de tagging de Tyba. Gobierno del ciclo de vida de los tags de analítica: qué está vivo, qué se puede deprecar y dónde el plan no coincide con la realidad.

**[→ Abrir el explorador](https://carloscastilla-tyba.github.io/tyta/)**

---

## Qué resuelve

Los tags se documentan en un tracking plan, se implementan en Front End y disparan hacia Google Analytics. Las tres fuentes se desincronizan: se instrumenta lo que no está documentado, se documenta lo que nunca se construyó, y dos squads miden lo mismo con IDs distintos.

Este repo cruza las tres y responde una pregunta por tag: **¿está vivo o conviene deprecarlo?**

## El estado actual

828 tags en el tracking plan · 548 filas en Analytics · 472 en Front End.

| Estado | Tags | Qué significa |
|---|---|---|
| 🟢 **Vivo** | 269 | Implementado y disparando |
| 🟠 **Falta en código** | 104 | Genera datos pero no aparece en la extracción de Front End |
| 🟠 **No dispara** | 44 | Está en el código pero no llega nada a Analytics |
| ⚫ **Sin datos** | 61 | Le faltan campos para poder evaluarlo |
| 🔴 **Sin rastro** | 350 | Sin implementación ni tráfico. Candidato a deprecar |

25,4 millones de eventos cubiertos.

Los 350 sin rastro son el número real de trabajo pendiente. Una versión anterior del motor reportaba 295 "no encontrados" que resultaron ser en su mayoría falsos negativos, y otra llegó a marcar 334 con el problema inverso. La cifra actual está verificada tag por tag.

---

## El explorador

`index.html` es un archivo autónomo, sin dependencias ni backend. Se abre en cualquier navegador y toda la búsqueda ocurre en local.

- **Navegación** por producto y squad, con los IDs en orden natural.
- **Filtro por estado** haciendo clic en las tarjetas del resumen.
- **Comparación campo por campo** de las tres fuentes, con el porcentaje de coincidencia de cada una.
- **Archivo de código** donde vive cada tag implementado.
- **Colisiones** y **1:N programático** marcados por separado.

---

## Cómo se decide si un tag está vivo

La reconciliación responde dos preguntas distintas, y mezclarlas fue el error que costó más iteraciones resolver.

### ¿Existe? — cobertura N:M

Un tag está cubierto si existe **al menos una** fila que le corresponda, sin competir con otros tags. Esto importa porque la relación real no es uno a uno: 182 pantallas del plan tienen varios tags (`HomeAcciones` tiene 20), y una misma pantalla aparece en varias filas de cada fuente.

Reglas, en orden:

1. **ID exacto** en la fuente.
2. **`screen_figma` idéntico Y `screen_analytics` idéntico** (≥85%).
3. Si el plan no declara `screen_analytics`, basta la pantalla más el ID exacto.
4. Si la pantalla coincide pero el `screen_analytics` no → **no cubierto**: es otro evento en la misma pantalla.

El punto 4 es clave. `Purchase_Order_Completed` y `Purchase_Order_Pending_Run` ocurren en la misma pantalla pero son pasos distintos del funnel. El `screen_analytics` define la identidad del evento, no es ruido de documentación.

### ¿Cuál es su mejor correspondencia? — matching 1:1

Para mostrar la huella y el diagnóstico se elige la fila con mejor puntaje. Es informativo: no determina si el tag existe.

### Reglas bloqueantes

Descartan un match sin importar el puntaje:

- **Conflicto de ID** — si ambos lados tienen ID y difieren, son tags distintos.
- **País** — `_CO` no casa con `_CL`.
- **Estado** — `Start` no casa con `Completed`.
- **Flujo** — `cash_in` no casa con `cash_out` (difieren en tres letras y el fuzzy los ve casi idénticos).

### Detalles del matcher

- **`token_sort_ratio`**, no `token_set_ratio`. El segundo devuelve 100% cuando los tokens de una cadena son subconjunto de la otra, y hacía que `Cashin_Investment_PE` casara con `Cashin_SummaryInvestmentFFMM_PE`. Cambiarlo redujo las colisiones un 21%.
- **Jerarquía de campos clave.** `screen_figma` identifica la pantalla; `screen_analytics` suele ser un nombre de evento reutilizado entre productos. Con la pantalla ≥85 se acepta; con solo el analytics alto y la pantalla baja, se descarta.
- **El país no penaliza.** Las divergencias son de formato: el plan declara `CO` y Front End declara `dynamic` o `cl, co, pe` porque la implementación cubre varios países.
- **Normalización** de camelCase, snake_case, acentos, placeholders (`$country`, `(param)`) y prefijos de método (`tag`, `log`, `on`).

---

## Archivos

```
index.html              el explorador
data/tags.json          los 828 tags con su estado y evidencia
data/tracking_plan.csv  el tracking plan reconciliado, en plano
```

---

## Regenerar las miniaturas de Figma

Las imágenes que se ven en el explorador están versionadas en `img/`. No se enlazan
en vivo desde Figma porque las URLs que genera la fórmula `IMAGE()` de Google Sheets
son enlaces prefirmados de S3 que **expiran a los 7 días**, y en más de la mitad de
los casos llegan sin el parámetro `X-Amz-Signature`, así que ni siquiera se pueden
descargar.

`scripts/fetch_figma_images.py` las regenera desde la API de Figma:

```bash
export FIGMA_TOKEN=figd_xxxxx
python scripts/fetch_figma_images.py

# opciones
python scripts/fetch_figma_images.py --solo-faltantes   # no rebaja lo ya descargado
python scripts/fetch_figma_images.py --limite 20        # prueba corta
python scripts/fetch_figma_images.py --escala 1         # más resolución
```

El token se genera en Figma → Settings → Security → Personal access tokens, con
permiso de solo lectura, y se lee de la variable de entorno: nunca va en el código
ni se sube al repo.

El script pide las imágenes **en lotes de 50 nodos por llamada**, así que los ~1.170
nodos se resuelven en unas 25 peticiones en lugar de una por imagen. Después
actualiza `data/tags.json` para que la interfaz apunte a los archivos locales.

Cuando un nodo ya no existe, la API devuelve `null` y el script lo anota en
`data/nodos_borrados.json` en vez de fallar. Esa ausencia confirma de forma
independiente el estado *nodo borrado* que reporta el tracking plan.

---

## Roadmap

El explorador hace visible lo que existe. La otra mitad del problema es evitar que nazcan tags malos.

**Siguiente:** interfaz de creación asistida.

- Ningún campo crítico en texto libre. Producto, flujo, pantalla, objeto y país se eligen de listas cerradas; la pantalla se sincroniza desde Figma, así que solo se pueden elegir nodos vivos.
- El ID se genera según el rango del squad.
- El nombre se compone con el patrón `Flujo_Paso_Estado`.
- **Huella como índice único en base de datos** (`flujo + pantalla + objeto + país`), que mueve el chequeo de duplicados desde una auditoría posterior al momento de crear, donde es una restricción trivial que no falla.
