#!/usr/bin/env python3
"""
Descarga las miniaturas de los nodos de Figma referenciados en el tracking plan.

Por qué existe
--------------
Las URLs que genera la fórmula IMAGE() en Google Sheets son enlaces prefirmados
de S3 que expiran a los 7 días, y en más de la mitad de los casos llegan sin el
parámetro X-Amz-Signature, así que ni siquiera se pueden descargar. Este script
las regenera desde la API de Figma y las guarda en el repo, donde no caducan.

Uso
---
    export FIGMA_TOKEN=figd_xxxxx
    python scripts/fetch_figma_images.py

    # opciones
    python scripts/fetch_figma_images.py --solo-faltantes   # no rebaja lo ya descargado
    python scripts/fetch_figma_images.py --escala 1         # 1x en vez de 0.5x
    python scripts/fetch_figma_images.py --limite 100       # prueba corta

El token se lee de la variable de entorno FIGMA_TOKEN. Nunca lo pongas en el
código ni lo subas al repo. Se genera en Figma → Settings → Security →
Personal access tokens, con permiso de solo lectura sobre archivos.

Qué hace
--------
1. Lee data/figma_nodes.json (el manifiesto: tag, fileKey, nodeId, tipo).
2. Agrupa por archivo y pide las imágenes en lotes de 50 nodos.
   La API acepta varios ids por llamada, así que 1.168 nodos se resuelven en
   ~25 peticiones en vez de 1.168.
3. Descarga cada PNG, lo redimensiona y lo guarda como JPG en img/.
4. Actualiza data/tags.json para que la interfaz apunte a los archivos locales.

Nodos borrados
--------------
Si un nodo ya no existe, la API devuelve null para ese id. El script lo registra
en el informe final en vez de fallar: esa ausencia es información útil, confirma
de forma independiente el estado "nodo borrado" del tracking plan.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

RAIZ = Path(__file__).resolve().parent.parent
MANIFIESTO = RAIZ / "data" / "figma_nodes.json"
TAGS = RAIZ / "data" / "tags.json"
DESTINO = RAIZ / "img"
API = "https://api.figma.com/v1"
LOTE = 50          # ids por petición; la API admite más, pero 50 va sobrado
PAUSA = 0.6        # segundos entre peticiones, para no toparse con el rate limit


def pedir(url: str, token: str, reintentos: int = 3) -> dict:
    """GET a la API de Figma con reintento ante 429 y errores de red."""
    for intento in range(reintentos):
        try:
            req = Request(url, headers={"X-Figma-Token": token})
            with urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except HTTPError as e:
            if e.code == 429:                      # rate limit
                espera = 2 ** (intento + 3)
                print(f"    rate limit, esperando {espera}s…")
                time.sleep(espera)
                continue
            if e.code in (403, 404):
                # 403: el token no tiene acceso a ese archivo. 404: no existe.
                return {"_error": f"HTTP {e.code}"}
            raise
        except URLError:
            time.sleep(2 ** intento)
    return {"_error": "sin respuesta"}


def nombre_archivo(file_key: str, node_id: str) -> str:
    """Nombre estable: mismo nodo, mismo archivo, sin importar cuándo se corra."""
    return hashlib.md5(f"{file_key}:{node_id}".encode()).hexdigest()[:12] + ".jpg"


def optimizar(bruto: bytes, ruta: Path, ancho_max: int = 420) -> int:
    """Convierte a JPG y limita el ancho. Sin Pillow, guarda el PNG tal cual."""
    try:
        from PIL import Image
        from io import BytesIO
        im = Image.open(BytesIO(bruto)).convert("RGB")
        im.thumbnail((ancho_max, ancho_max))
        im.save(ruta, "JPEG", quality=78, optimize=True)
    except ImportError:
        ruta = ruta.with_suffix(".png")
        ruta.write_bytes(bruto)
    return ruta.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--solo-faltantes", action="store_true",
                    help="salta los nodos que ya tienen imagen en img/")
    ap.add_argument("--escala", type=float, default=0.5,
                    help="escala de render (0.5 por defecto; 1 o 2 para más detalle)")
    ap.add_argument("--limite", type=int, default=0,
                    help="procesa solo los primeros N nodos, para probar")
    args = ap.parse_args()

    token = os.environ.get("FIGMA_TOKEN", "").strip()
    if not token:
        print("Falta FIGMA_TOKEN.\n\n    export FIGMA_TOKEN=figd_xxxxx\n")
        return 1

    if not MANIFIESTO.exists():
        print(f"No encuentro {MANIFIESTO}")
        return 1

    nodos = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    DESTINO.mkdir(exist_ok=True)

    # deduplicar: el mismo nodo puede estar referenciado por varios tags
    unicos: dict[tuple, dict] = {}
    for n in nodos:
        unicos.setdefault((n["file"], n["node"]), n)
    pendientes = list(unicos.values())

    if args.solo_faltantes:
        pendientes = [n for n in pendientes
                      if not (DESTINO / nombre_archivo(n["file"], n["node"])).exists()]
    if args.limite:
        pendientes = pendientes[: args.limite]

    print(f"{len(unicos)} nodos únicos · {len(pendientes)} por descargar\n")
    if not pendientes:
        print("No hay nada pendiente.")
        return 0

    # agrupar por archivo: la API pide los ids de un archivo a la vez
    por_archivo: dict[str, list[str]] = {}
    for n in pendientes:
        por_archivo.setdefault(n["file"], []).append(n["node"])

    descargadas = borrados = fallidas = 0
    peso = 0
    sin_acceso: list[str] = []
    nodos_borrados: list[tuple] = []

    for file_key, ids in por_archivo.items():
        print(f"archivo {file_key} · {len(ids)} nodos")
        for i in range(0, len(ids), LOTE):
            trozo = ids[i : i + LOTE]
            url = f"{API}/images/{file_key}?ids={','.join(trozo)}&format=png&scale={args.escala}"
            datos = pedir(url, token)
            time.sleep(PAUSA)

            if "_error" in datos:
                print(f"    sin acceso ({datos['_error']}) — se omite el archivo")
                sin_acceso.append(file_key)
                fallidas += len(trozo)
                break

            imagenes = datos.get("images") or {}
            for node_id in trozo:
                url_img = imagenes.get(node_id)
                if not url_img:
                    # la API devuelve null cuando el nodo ya no existe
                    nodos_borrados.append((file_key, node_id))
                    borrados += 1
                    continue
                try:
                    with urlopen(url_img, timeout=60) as r:
                        bruto = r.read()
                    ruta = DESTINO / nombre_archivo(file_key, node_id)
                    peso += optimizar(bruto, ruta)
                    descargadas += 1
                except Exception as e:
                    print(f"    fallo al bajar {node_id}: {e}")
                    fallidas += 1
            print(f"    {min(i+LOTE,len(ids))}/{len(ids)}")

    # --- enlazar las imágenes en tags.json para que la interfaz las use
    if TAGS.exists() and descargadas:
        d = json.loads(TAGS.read_text(encoding="utf-8"))
        import re
        enlazadas = 0
        for r in d.get("r", []):
            fg = r.get("fg") or {}
            for x in fg.get("im", []):
                m = re.search(r"figma\.com/design/([A-Za-z0-9]+)", x.get("u", ""))
                n = re.search(r"node-id=([0-9]+[-:][0-9]+)", x.get("u", ""))
                if not (m and n):
                    continue
                archivo = nombre_archivo(m.group(1), n.group(1).replace("-", ":"))
                if (DESTINO / archivo).exists():
                    x["f"] = archivo
                    enlazadas += 1
        TAGS.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\ntags.json actualizado · {enlazadas} referencias enlazadas")

    print("\n" + "=" * 52)
    print(f"  descargadas      : {descargadas}  ({peso/1024/1024:.1f} MB)")
    print(f"  nodos inexistentes: {borrados}")
    print(f"  fallidas         : {fallidas}")
    if sin_acceso:
        print(f"\n  Sin acceso a {len(set(sin_acceso))} archivo(s). El token debe pertenecer")
        print("  a una cuenta con permiso de lectura sobre ellos.")
    if nodos_borrados:
        salida = RAIZ / "data" / "nodos_borrados.json"
        salida.write_text(json.dumps(
            [{"file": f, "node": n} for f, n in nodos_borrados], indent=1), encoding="utf-8")
        print(f"\n  Los nodos inexistentes quedaron en {salida.name}.")
        print("  Confirman de forma independiente el estado 'nodo borrado' del plan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
