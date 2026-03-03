"""
Scrapea las provincias faltantes y añade al JSON existente.
"""

import json
import time
import urllib.request
import urllib.error
import base64
import os

USERNAME = "cto@sinvelloporlaser.es"
PASSWORD = "0c332e910dfe0849"
API_URL = "https://api.dataforseo.com/v3/business_data/business_listings/search/live"

# Ciudades que FALTAN por scrapear (capitales de provincia)
CIUDADES_FALTANTES = [
    {"nombre": "Albacete", "lat": 38.9942, "lon": -1.8585, "radio": 20},
    {"nombre": "Avila", "lat": 40.6560, "lon": -4.6813, "radio": 20},
    {"nombre": "Badajoz", "lat": 38.8794, "lon": -6.9707, "radio": 20},
    {"nombre": "Caceres", "lat": 39.4753, "lon": -6.3724, "radio": 20},
    {"nombre": "Castellon", "lat": 39.9864, "lon": -0.0513, "radio": 20},
    {"nombre": "Ciudad Real", "lat": 38.9848, "lon": -3.9274, "radio": 20},
    {"nombre": "Cuenca", "lat": 40.0704, "lon": -2.1374, "radio": 20},
    {"nombre": "Girona", "lat": 41.9794, "lon": 2.8214, "radio": 20},
    {"nombre": "Guadalajara", "lat": 40.6337, "lon": -3.1668, "radio": 20},
    {"nombre": "Huelva", "lat": 37.2614, "lon": -6.9447, "radio": 20},
    {"nombre": "Huesca", "lat": 42.1401, "lon": -0.4089, "radio": 20},
    {"nombre": "Jaen", "lat": 37.7796, "lon": -3.7849, "radio": 20},
    {"nombre": "Leon", "lat": 42.5987, "lon": -5.5671, "radio": 20},
    {"nombre": "Lleida", "lat": 41.6176, "lon": 0.6200, "radio": 20},
    {"nombre": "Lugo", "lat": 43.0097, "lon": -7.5567, "radio": 20},
    {"nombre": "Ourense", "lat": 42.3360, "lon": -7.8639, "radio": 20},
    {"nombre": "Palencia", "lat": 42.0095, "lon": -4.5288, "radio": 20},
    {"nombre": "Pontevedra", "lat": 42.4310, "lon": -8.6445, "radio": 15},
    {"nombre": "Segovia", "lat": 40.9429, "lon": -4.1088, "radio": 20},
    {"nombre": "Soria", "lat": 41.7636, "lon": -2.4649, "radio": 20},
    {"nombre": "Tarragona", "lat": 41.1189, "lon": 1.2445, "radio": 20},
    {"nombre": "Teruel", "lat": 40.3456, "lon": -1.1065, "radio": 20},
    {"nombre": "Zamora", "lat": 41.5034, "lon": -5.7445, "radio": 20},
]

CATEGORIAS = ["nail_salon", "beauty_salon", "manicure"]
ITEMS_PER_PAGE = 100
MAX_OFFSET = 1000


def make_request(payload):
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
    negocios = []
    offset = 0
    coord = f"{ciudad['lat']},{ciudad['lon']},{ciudad['radio']}"
    while offset < MAX_OFFSET:
        payload = [{
            "categories": [categoria],
            "location_coordinate": coord,
            "limit": ITEMS_PER_PAGE,
            "offset": offset,
            "filters": [["rating.value", ">", 0]],
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
            break
        task_result = task.get("result", [])
        if not task_result:
            break
        items = task_result[0].get("items", [])
        if not items:
            break
        total = task_result[0].get("total_count", 0)
        negocios.extend(items)
        print(f"  [{categoria}] offset={offset}, items={len(items)}, total={total}, acc={len(negocios)}")
        if len(items) < ITEMS_PER_PAGE:
            break
        offset += ITEMS_PER_PAGE
        time.sleep(0.3)
    return negocios


def extraer_datos(item, ciudad_nombre):
    address_info = item.get("address_info", {})
    rating = item.get("rating", {})
    work_time = item.get("work_time", {}).get("work_hours", {})
    return {
        "cid": item.get("cid"),
        "nombre": item.get("title", ""),
        "descripcion": (item.get("description") or "")[:300],
        "categoria": item.get("category", ""),
        "categorias": item.get("category_ids", []),
        "direccion": item.get("address", ""),
        "ciudad": address_info.get("city", ciudad_nombre),
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
        "imagen": "",
        "total_fotos": item.get("total_photos", 0),
        "horarios": work_time.get("timetable"),
        "estado": work_time.get("current_status", ""),
        "atributos": item.get("attributes", {}).get("available_attributes", {}),
        "google_maps_url": item.get("check_url", ""),
        "ultima_actualizacion": item.get("last_updated_time", ""),
        "ciudad_busqueda": ciudad_nombre,
    }


def main():
    # Load existing data
    data_file = os.path.join(os.path.dirname(__file__), "..", "src", "data", "negocios.json")
    with open(data_file, "r", encoding="utf-8") as f:
        existing = json.load(f)

    # Collect existing CIDs to avoid duplicates
    existing_cids = set()
    for prov_data in existing.get("provincias", {}).values():
        for n in prov_data.get("capital_negocios", []):
            existing_cids.add(n.get("cid"))
        for sub in prov_data.get("subcities", {}).values():
            for n in sub.get("negocios", []):
                existing_cids.add(n.get("cid"))

    print(f"Existing CIDs: {len(existing_cids)}")
    print(f"Scraping {len(CIUDADES_FALTANTES)} missing cities...\n")

    new_negocios = {}  # city -> [negocios]

    for i, ciudad in enumerate(CIUDADES_FALTANTES):
        print(f"[{i+1}/{len(CIUDADES_FALTANTES)}] {ciudad['nombre']}...")
        for cat in CATEGORIAS:
            items = scrape_ciudad(ciudad, cat)
            for item in items:
                cid = item.get("cid")
                if cid and cid not in existing_cids:
                    datos = extraer_datos(item, ciudad["nombre"])
                    if datos["estado"] != "closed_forever":
                        city = datos["ciudad"]
                        if city not in new_negocios:
                            new_negocios[city] = []
                        new_negocios[city].append(datos)
                        existing_cids.add(cid)

        total_new = sum(len(ns) for ns in new_negocios.values())
        print(f"  => Total nuevos acumulados: {total_new}")

    # Save new businesses to a separate temp file first
    temp_file = os.path.join(os.path.dirname(__file__), "..", "src", "data", "negocios_faltantes.json")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump({
            "total": sum(len(ns) for ns in new_negocios.values()),
            "ciudades": len(new_negocios),
            "fecha_scraping": time.strftime("%Y-%m-%d"),
            "negocios_por_ciudad": new_negocios,
        }, f, ensure_ascii=False)

    total_new = sum(len(ns) for ns in new_negocios.values())
    print(f"\nTotal nuevos negocios: {total_new}")
    print(f"Ciudades nuevas: {len(new_negocios)}")
    print(f"Guardado en: {temp_file}")

    for c, ns in sorted(new_negocios.items(), key=lambda x: -len(x[1]))[:20]:
        print(f"  {c}: {len(ns)}")


if __name__ == "__main__":
    main()
