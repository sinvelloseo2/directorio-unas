"""
Reorganiza negocios.json en estructura jerárquica:
Provincia → Capital + Sub-ciudades

Las 50 provincias de España con sus capitales.
"""

import json
import os
import unicodedata
import re

INPUT = os.path.join(os.path.dirname(__file__), "..", "src", "data", "negocios.json")
OUTPUT = INPUT

# Mapeo de regiones de DataForSEO → Provincia española + Capital
PROVINCIAS = {
    # Region DataForSEO: (nombre_provincia, capital)
    "A Coruña": ("A Coruña", "A Coruña"),
    "Álava": ("Álava", "Vitoria-Gasteiz"),
    "Albacete": ("Albacete", "Albacete"),
    "Alicante": ("Alicante", "Alicante"),
    "Almería": ("Almería", "Almería"),
    "Asturias": ("Asturias", "Oviedo"),
    "Ávila": ("Ávila", "Ávila"),
    "Badajoz": ("Badajoz", "Badajoz"),
    "Barcelona": ("Barcelona", "Barcelona"),
    "Biscay": ("Bizkaia", "Bilbao"),
    "Burgos": ("Burgos", "Burgos"),
    "Cáceres": ("Cáceres", "Cáceres"),
    "Cádiz": ("Cádiz", "Cádiz"),
    "Cantabria": ("Cantabria", "Santander"),
    "Castellón": ("Castellón", "Castellón"),
    "Ciudad Real": ("Ciudad Real", "Ciudad Real"),
    "Córdoba": ("Córdoba", "Córdoba"),
    "Cuenca": ("Cuenca", "Cuenca"),
    "Gipuzkoa": ("Gipuzkoa", "San Sebastián"),
    "Girona": ("Girona", "Girona"),
    "Granada": ("Granada", "Granada"),
    "Guadalajara": ("Guadalajara", "Guadalajara"),
    "Huelva": ("Huelva", "Huelva"),
    "Huesca": ("Huesca", "Huesca"),
    "Balearic Islands": ("Islas Baleares", "Palma de Mallorca"),
    "Jaén": ("Jaén", "Jaén"),
    "La Rioja": ("La Rioja", "Logroño"),
    "Las Palmas": ("Las Palmas", "Las Palmas"),
    "León": ("León", "León"),
    "Lleida": ("Lleida", "Lleida"),
    "Lugo": ("Lugo", "Lugo"),
    "Madrid": ("Madrid", "Madrid"),
    "Málaga": ("Málaga", "Málaga"),
    "Murcia": ("Murcia", "Murcia"),
    "Navarre": ("Navarra", "Pamplona"),
    "Ourense": ("Ourense", "Ourense"),
    "Palencia": ("Palencia", "Palencia"),
    "Pontevedra": ("Pontevedra", "Pontevedra"),
    "Salamanca": ("Salamanca", "Salamanca"),
    "Santa Cruz de Tenerife": ("Santa Cruz de Tenerife", "Santa Cruz de Tenerife"),
    "Segovia": ("Segovia", "Segovia"),
    "Seville": ("Sevilla", "Sevilla"),
    "Soria": ("Soria", "Soria"),
    "Tarragona": ("Tarragona", "Tarragona"),
    "Teruel": ("Teruel", "Teruel"),
    "Toledo": ("Toledo", "Toledo"),
    "Valencia": ("Valencia", "Valencia"),
    "Valladolid": ("Valladolid", "Valladolid"),
    "Zamora": ("Zamora", "Zamora"),
    "Zaragoza": ("Zaragoza", "Zaragoza"),
}

# Ciudades que son la capital aunque tengan nombre diferente en los datos
CAPITAL_ALIASES = {
    "Palma": "Palma de Mallorca",
    "Palma De Mallorca": "Palma de Mallorca",
    "Donostia / San Sebastián": "San Sebastián",
    "Donostia": "San Sebastián",
    "Las Palmas de Gran Canaria": "Las Palmas",
    "Elx": "Elche",  # NOT capital - capital is Alicante
    "València": "Valencia",
}


def slugify(text):
    text = text.lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Collect all businesses and assign province
    provincias = {}  # provincia_slug -> { info, capital_negocios, subcities: { city -> negocios } }

    for ciudad, negocios in data["negocios_por_ciudad"].items():
        if not negocios:
            continue

        # Get region from first business
        region = negocios[0].get("region") or ""

        # Map region to province
        if region in PROVINCIAS:
            prov_name, capital = PROVINCIAS[region]
        else:
            # Try to find by partial match or skip
            found = False
            for r_key, (prov_name, capital) in PROVINCIAS.items():
                if r_key.lower() in region.lower() or region.lower() in r_key.lower():
                    found = True
                    break
            if not found:
                # Assign to nearest search city's province
                busqueda = negocios[0].get("ciudad_busqueda", "")
                for r_key, (prov_name, capital) in PROVINCIAS.items():
                    if capital.lower() == busqueda.lower() or slugify(capital) == slugify(busqueda):
                        found = True
                        break
                if not found:
                    print(f"  SKIP: {ciudad} (region='{region}', busqueda='{busqueda}')")
                    continue

        prov_slug = slugify(prov_name)

        if prov_slug not in provincias:
            provincias[prov_slug] = {
                "nombre": prov_name,
                "capital": capital,
                "capital_slug": slugify(capital),
                "ciudades": {}
            }

        # Normalize city name
        actual_city = CAPITAL_ALIASES.get(ciudad, ciudad)

        # Check if this city IS the capital
        is_capital = (
            slugify(actual_city) == slugify(capital) or
            actual_city.lower() == capital.lower()
        )

        if is_capital:
            city_key = "__capital__"
        else:
            city_key = actual_city

        if city_key not in provincias[prov_slug]["ciudades"]:
            provincias[prov_slug]["ciudades"][city_key] = []

        provincias[prov_slug]["ciudades"][city_key].extend(negocios)

    # Deduplicate within each city by cid
    for prov_slug, prov_data in provincias.items():
        for city_key in prov_data["ciudades"]:
            seen = set()
            unique = []
            for n in prov_data["ciudades"][city_key]:
                if n["cid"] not in seen:
                    seen.add(n["cid"])
                    # Update city name for capital businesses
                    if city_key == "__capital__":
                        n["ciudad"] = prov_data["capital"]
                    unique.append(n)
            unique.sort(key=lambda x: (x.get("rating") or 0, x.get("num_resenas") or 0), reverse=True)
            prov_data["ciudades"][city_key] = unique

    # Build final structure
    output_provincias = {}
    total_negocios = 0

    for prov_slug in sorted(provincias.keys()):
        prov = provincias[prov_slug]
        capital_negocios = prov["ciudades"].pop("__capital__", [])
        subcities = {}

        for city_name, negocios in sorted(prov["ciudades"].items()):
            if len(negocios) >= 1:  # Include all sub-cities with at least 1 business
                subcities[city_name] = negocios
                total_negocios += len(negocios)

        total_negocios += len(capital_negocios)
        total_provincia = len(capital_negocios) + sum(len(ns) for ns in subcities.values())

        output_provincias[prov_slug] = {
            "nombre": prov["nombre"],
            "capital": prov["capital"],
            "capital_slug": prov["capital_slug"],
            "total": total_provincia,
            "capital_negocios": capital_negocios,
            "subcities": {
                slugify(c): {
                    "nombre": c,
                    "negocios": ns
                }
                for c, ns in sorted(subcities.items(), key=lambda x: -len(x[1]))
            }
        }

    output = {
        "total": total_negocios,
        "provincias_count": len(output_provincias),
        "fecha_scraping": data["fecha_scraping"],
        "provincias": output_provincias,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)

    print(f"\nTotal negocios: {total_negocios}")
    print(f"Provincias: {len(output_provincias)}")
    print(f"Tamaño: {size_mb:.1f} MB")
    print(f"\nDesglose:")
    for prov_slug in sorted(output_provincias.keys()):
        p = output_provincias[prov_slug]
        cap_count = len(p["capital_negocios"])
        sub_count = sum(len(s["negocios"]) for s in p["subcities"].values())
        sub_cities = len(p["subcities"])
        print(f"  {p['nombre']} ({p['capital']}): {cap_count} capital + {sub_count} en {sub_cities} localidades = {p['total']}")


if __name__ == "__main__":
    main()
