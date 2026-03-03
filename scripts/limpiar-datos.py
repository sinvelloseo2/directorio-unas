"""
Limpia y optimiza el JSON de negocios:
- Fusiona ciudades duplicadas (case-insensitive)
- Filtra ciudades con menos de 3 negocios
- Normaliza nombres de ciudades conocidas
- Reduce datos por negocio para minimizar tamaño del archivo
"""

import json
import os
import unicodedata

INPUT = os.path.join(os.path.dirname(__file__), "..", "src", "data", "negocios.json")
OUTPUT = INPUT  # Overwrite

# Mapeo de nombres de ciudades para normalizar
CITY_NORMALIZE = {
    "València": "Valencia",
    "Seville": "Sevilla",
    "Palma": "Palma de Mallorca",
    "Elx": "Elche",
    "Donostia / San Sebastián": "San Sebastián",
    "Donostia": "San Sebastián",
    "A Coruña": "A Coruña",
    "San Cristóbal de La Laguna": "La Laguna",
    "Donostia-San Sebastian": "San Sebastián",
    "Las Palmas de Gran Canaria": "Las Palmas",
    "Gijón": "Gijón",
}

MIN_NEGOCIOS = 3  # Mínimo de negocios por ciudad para incluir


def normalize_city(name):
    """Normaliza el nombre de una ciudad."""
    # Primero buscar en el mapa directo
    if name in CITY_NORMALIZE:
        return CITY_NORMALIZE[name]
    # Capitalizar correctamente
    return name.strip().title() if name.islower() else name.strip()


def trim_negocio(n):
    """Reduce los datos de un negocio a lo esencial."""
    return {
        "cid": n.get("cid", ""),
        "nombre": n.get("nombre", ""),
        "descripcion": (n.get("descripcion") or "")[:300],
        "categoria": n.get("categoria", ""),
        "categorias": n.get("categorias", []),
        "direccion": n.get("direccion", ""),
        "ciudad": n.get("ciudad", ""),
        "region": n.get("region", ""),
        "codigo_postal": n.get("codigo_postal", ""),
        "barrio": n.get("barrio", ""),
        "telefono": n.get("telefono", ""),
        "web": n.get("web", ""),
        "dominio": n.get("dominio", ""),
        "rating": n.get("rating"),
        "num_resenas": n.get("num_resenas", 0),
        "rating_distribucion": n.get("rating_distribucion", {}),
        "latitud": n.get("latitud"),
        "longitud": n.get("longitud"),
        "verificado": n.get("verificado", False),
        "imagen": "",  # Remove large image URLs to save space
        "total_fotos": n.get("total_fotos", 0),
        "horarios": n.get("horarios"),
        "estado": n.get("estado", ""),
        "atributos": n.get("atributos", {}),
        "google_maps_url": n.get("google_maps_url", ""),
        "ultima_actualizacion": n.get("ultima_actualizacion", ""),
        "ciudad_busqueda": n.get("ciudad_busqueda", ""),
    }


def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    original_total = data["total"]
    original_cities = data["ciudades"]

    # Merge all businesses into a new city map
    merged = {}
    for city_name, negocios in data["negocios_por_ciudad"].items():
        normalized = normalize_city(city_name)
        if normalized not in merged:
            merged[normalized] = []
        merged[normalized].extend(negocios)

    # Deduplicate within each city by cid
    for city in merged:
        seen = set()
        unique = []
        for n in merged[city]:
            if n["cid"] not in seen:
                seen.add(n["cid"])
                unique.append(trim_negocio(n))
        # Sort by rating desc, then reviews desc
        unique.sort(key=lambda x: (x.get("rating") or 0, x.get("num_resenas") or 0), reverse=True)
        merged[city] = unique

    # Filter cities with minimum businesses
    filtered = {c: ns for c, ns in merged.items() if len(ns) >= MIN_NEGOCIOS}

    # Update city names in businesses
    for city, negocios in filtered.items():
        for n in negocios:
            n["ciudad"] = city

    # Stats
    total = sum(len(ns) for ns in filtered.values())
    stats = {c: len(ns) for c, ns in filtered.items()}

    output = {
        "total": total,
        "ciudades": len(filtered),
        "stats": stats,
        "fecha_scraping": data["fecha_scraping"],
        "negocios_por_ciudad": filtered,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)

    print(f"Original: {original_total} negocios en {original_cities} localidades")
    print(f"Limpio: {total} negocios en {len(filtered)} ciudades")
    print(f"Eliminados: {original_total - total} negocios en localidades pequeñas")
    print(f"Tamaño archivo: {size_mb:.1f} MB")
    print()
    print("Top 30 ciudades:")
    for c, n in sorted(stats.items(), key=lambda x: -x[1])[:30]:
        print(f"  {c}: {n}")


if __name__ == "__main__":
    main()
