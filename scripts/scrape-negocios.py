"""
Scraper de negocios locales de uñas en España usando DataForSEO Business Listings API.
Recorre 30 ciudades principales, pagina todos los resultados y guarda en JSON.
"""

import json
import time
import urllib.request
import urllib.error
import base64
import os
import sys

# --- Configuración ---
USERNAME = "cto@sinvelloporlaser.es"
PASSWORD = "0c332e910dfe0849"
API_URL = "https://api.dataforseo.com/v3/business_data/business_listings/search/live"

# 30 ciudades principales de España con coordenadas (lat, lon, radio en km)
CIUDADES = [
    {"nombre": "Madrid", "lat": 40.4168, "lon": -3.7038, "radio": 40},
    {"nombre": "Barcelona", "lat": 41.3874, "lon": 2.1686, "radio": 30},
    {"nombre": "Valencia", "lat": 39.4699, "lon": -0.3763, "radio": 25},
    {"nombre": "Sevilla", "lat": 37.3891, "lon": -5.9845, "radio": 20},
    {"nombre": "Zaragoza", "lat": 41.6488, "lon": -0.8891, "radio": 20},
    {"nombre": "Malaga", "lat": 36.7213, "lon": -4.4214, "radio": 25},
    {"nombre": "Murcia", "lat": 37.9922, "lon": -1.1307, "radio": 20},
    {"nombre": "Palma de Mallorca", "lat": 39.5696, "lon": 2.6502, "radio": 25},
    {"nombre": "Las Palmas", "lat": 28.1235, "lon": -15.4363, "radio": 25},
    {"nombre": "Bilbao", "lat": 43.2630, "lon": -2.9350, "radio": 20},
    {"nombre": "Alicante", "lat": 38.3452, "lon": -0.4810, "radio": 20},
    {"nombre": "Cordoba", "lat": 37.8882, "lon": -4.7794, "radio": 15},
    {"nombre": "Valladolid", "lat": 41.6523, "lon": -4.7245, "radio": 15},
    {"nombre": "Vigo", "lat": 42.2406, "lon": -8.7207, "radio": 15},
    {"nombre": "Gijon", "lat": 43.5322, "lon": -5.6611, "radio": 15},
    {"nombre": "Hospitalet de Llobregat", "lat": 41.3596, "lon": 2.1005, "radio": 10},
    {"nombre": "A Coruna", "lat": 43.3623, "lon": -8.4115, "radio": 15},
    {"nombre": "Granada", "lat": 37.1773, "lon": -3.5986, "radio": 15},
    {"nombre": "Vitoria-Gasteiz", "lat": 42.8469, "lon": -2.6716, "radio": 15},
    {"nombre": "Elche", "lat": 38.2699, "lon": -0.7125, "radio": 15},
    {"nombre": "Oviedo", "lat": 43.3619, "lon": -5.8494, "radio": 15},
    {"nombre": "Santa Cruz de Tenerife", "lat": 28.4636, "lon": -16.2518, "radio": 25},
    {"nombre": "Pamplona", "lat": 42.8125, "lon": -1.6458, "radio": 15},
    {"nombre": "Santander", "lat": 43.4623, "lon": -3.8100, "radio": 15},
    {"nombre": "Almeria", "lat": 36.8340, "lon": -2.4637, "radio": 15},
    {"nombre": "San Sebastian", "lat": 43.3183, "lon": -1.9812, "radio": 15},
    {"nombre": "Burgos", "lat": 42.3439, "lon": -3.6969, "radio": 15},
    {"nombre": "Salamanca", "lat": 40.9701, "lon": -5.6635, "radio": 15},
    {"nombre": "Logrono", "lat": 42.4627, "lon": -2.4445, "radio": 15},
    {"nombre": "Cadiz", "lat": 36.5271, "lon": -6.2886, "radio": 20},
]

# Categorías a buscar
CATEGORIAS = ["nail_salon", "beauty_salon", "manicure"]

ITEMS_PER_PAGE = 100  # Máximo por petición en la API real
MAX_OFFSET = 1000     # Límite de seguridad por ciudad/categoría


def make_request(payload):
    """Hace una petición POST a la API de DataForSEO."""
    credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def scrape_ciudad(ciudad, categoria):
    """Scrapea todos los negocios de una ciudad para una categoría."""
    negocios = []
    offset = 0
    coord = f"{ciudad['lat']},{ciudad['lon']},{ciudad['radio']}"

    while offset < MAX_OFFSET:
        payload = [{
            "categories": [categoria],
            "location_coordinate": coord,
            "limit": ITEMS_PER_PAGE,
            "offset": offset,
            "filters": [
                ["rating.value", ">", 0]
            ],
            "order_by": ["rating.votes_count,desc"]
        }]

        result = make_request(payload)
        if not result:
            break

        tasks = result.get("tasks", [])
        if not tasks:
            break

        task = tasks[0]
        if task.get("status_code") != 20000:
            print(f"  Error en task: {task.get('status_message')}")
            break

        task_result = task.get("result", [])
        if not task_result:
            break

        items = task_result[0].get("items", [])
        if not items:
            break

        total = task_result[0].get("total_count", 0)
        negocios.extend(items)

        print(f"  [{categoria}] offset={offset}, items={len(items)}, total_disponible={total}, acumulados={len(negocios)}")

        if len(items) < ITEMS_PER_PAGE:
            break

        offset += ITEMS_PER_PAGE
        time.sleep(0.3)  # Rate limiting

    return negocios


def extraer_datos(item, ciudad_nombre):
    """Extrae los campos relevantes de un item de la API."""
    address_info = item.get("address_info", {})
    rating = item.get("rating", {})
    work_time = item.get("work_time", {}).get("work_hours", {})

    # Determinar la ciudad real del negocio
    city = address_info.get("city", ciudad_nombre)

    return {
        "cid": item.get("cid"),
        "nombre": item.get("title", ""),
        "descripcion": (item.get("description") or "")[:500],
        "categoria": item.get("category", ""),
        "categorias": item.get("category_ids", []),
        "direccion": item.get("address", ""),
        "ciudad": city,
        "region": address_info.get("region", ""),
        "codigo_postal": address_info.get("zip", ""),
        "barrio": address_info.get("borough", ""),
        "telefono": item.get("phone", ""),
        "web": item.get("url", ""),
        "dominio": item.get("domain", ""),
        "rating": rating.get("value"),
        "num_resenas": rating.get("votes_count", 0),
        "rating_distribucion": item.get("rating_distribution", {}),
        "latitud": item.get("latitude"),
        "longitud": item.get("longitude"),
        "verificado": item.get("is_claimed", False),
        "imagen": item.get("main_image", ""),
        "total_fotos": item.get("total_photos", 0),
        "horarios": work_time.get("timetable"),
        "estado": work_time.get("current_status", ""),
        "atributos": item.get("attributes", {}).get("available_attributes", {}),
        "google_maps_url": item.get("check_url", ""),
        "ultima_actualizacion": item.get("last_updated_time", ""),
        "ciudad_busqueda": ciudad_nombre,
    }


def main():
    todos_negocios = {}  # Diccionario por cid para deduplicar
    stats = {}

    print("=" * 60)
    print("SCRAPER DE SALONES DE UÑAS - ESPAÑA (30 CIUDADES)")
    print("=" * 60)

    for i, ciudad in enumerate(CIUDADES):
        print(f"\n[{i+1}/{len(CIUDADES)}] Scrapeando: {ciudad['nombre']}...")
        ciudad_total = 0

        for categoria in CATEGORIAS:
            items = scrape_ciudad(ciudad, categoria)

            for item in items:
                cid = item.get("cid")
                if cid and cid not in todos_negocios:
                    datos = extraer_datos(item, ciudad["nombre"])
                    # Filtrar negocios cerrados permanentemente
                    if datos["estado"] != "closed_forever":
                        todos_negocios[cid] = datos
                        ciudad_total += 1

        stats[ciudad["nombre"]] = ciudad_total
        print(f"  => {ciudad['nombre']}: {ciudad_total} negocios nuevos (total acumulado: {len(todos_negocios)})")

    # Organizar por ciudad
    por_ciudad = {}
    for negocio in todos_negocios.values():
        ciudad = negocio["ciudad"]
        if ciudad not in por_ciudad:
            por_ciudad[ciudad] = []
        por_ciudad[ciudad].append(negocio)

    # Ordenar cada ciudad por rating (desc) y luego por num_resenas (desc)
    for ciudad in por_ciudad:
        por_ciudad[ciudad].sort(
            key=lambda x: (x.get("rating") or 0, x.get("num_resenas") or 0),
            reverse=True
        )

    # Guardar resultados
    output_dir = os.path.join(os.path.dirname(__file__), "..", "src", "data")
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "negocios.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "total": len(todos_negocios),
            "ciudades": len(por_ciudad),
            "stats": stats,
            "fecha_scraping": time.strftime("%Y-%m-%d"),
            "negocios_por_ciudad": por_ciudad,
        }, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"COMPLETADO")
    print(f"Total negocios únicos: {len(todos_negocios)}")
    print(f"Total ciudades con resultados: {len(por_ciudad)}")
    print(f"Archivo guardado: {output_file}")
    print("=" * 60)

    print("\nDesglose por ciudad:")
    for ciudad, negocios in sorted(por_ciudad.items(), key=lambda x: -len(x[1])):
        print(f"  {ciudad}: {len(negocios)} negocios")


if __name__ == "__main__":
    main()
