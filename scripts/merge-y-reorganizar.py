"""
Fusiona datos existentes + faltantes y reorganiza en estructura de provincias.
"""

import json
import os
import unicodedata
import re
import time

BASE = os.path.join(os.path.dirname(__file__), "..", "src", "data")
EXISTING = os.path.join(BASE, "negocios.json")
FALTANTES = os.path.join(BASE, "negocios_faltantes.json")
OUTPUT = EXISTING

PROVINCIAS = {
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
    "Castellón": ("Castellón", "Castellón de la Plana"),
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
    # Extra region names from DataForSEO
    "Castellon": ("Castellón", "Castellón de la Plana"),
    "Castile-La Mancha": ("Ciudad Real", "Ciudad Real"),
    "Castilla-La Mancha": ("Ciudad Real", "Ciudad Real"),
    "Bizkaia": ("Bizkaia", "Bilbao"),
    "Vizcaya": ("Bizkaia", "Bilbao"),
}

CAPITAL_ALIASES = {
    "Palma": "Palma de Mallorca",
    "Palma De Mallorca": "Palma de Mallorca",
    "Donostia / San Sebastián": "San Sebastián",
    "Donostia": "San Sebastián",
    "Donostia-San Sebastián": "San Sebastián",
    "Las Palmas de Gran Canaria": "Las Palmas",
    "València": "Valencia",
    "Castelló de la Plana": "Castellón de la Plana",
    "Castellón de la Plana": "Castellón de la Plana",
    "Castellon de la Plana": "Castellón de la Plana",
    "Castellón": "Castellón de la Plana",
    "CASTELLON": "Castellón de la Plana",
    # A Coruña variants from Google Maps
    "La Coruña": "A Coruña",
    "Coruña (A)": "A Coruña",
    "Coruña ( A )": "A Coruña",
    "Coruña": "A Coruña",
    # Lleida variants
    "Lleida, Tây Ban Nha": "Lleida",
    "Lérida": "Lleida",
    # Girona variants
    "Gerona": "Girona",
    # Ourense variants
    "Orense": "Ourense",
    # Vitoria variants
    "Vitoria": "Vitoria-Gasteiz",
    # Pamplona variants
    "Iruña": "Pamplona",
    "Pamplona/Iruña": "Pamplona",
}

# Mapeo ciudad_busqueda → provincia (para negocios sin region)
BUSQUEDA_TO_REGION = {
    "Madrid": "Madrid",
    "Barcelona": "Barcelona",
    "Valencia": "Valencia",
    "Sevilla": "Seville",
    "Zaragoza": "Zaragoza",
    "Malaga": "Málaga",
    "Murcia": "Murcia",
    "Palma de Mallorca": "Balearic Islands",
    "Las Palmas": "Las Palmas",
    "Bilbao": "Biscay",
    "Alicante": "Alicante",
    "Cordoba": "Córdoba",
    "Valladolid": "Valladolid",
    "Vigo": "Pontevedra",
    "Gijon": "Asturias",
    "Hospitalet de Llobregat": "Barcelona",
    "A Coruna": "A Coruña",
    "Granada": "Granada",
    "Vitoria-Gasteiz": "Álava",
    "Elche": "Alicante",
    "Oviedo": "Asturias",
    "Santa Cruz de Tenerife": "Santa Cruz de Tenerife",
    "Pamplona": "Navarre",
    "Santander": "Cantabria",
    "Almeria": "Almería",
    "San Sebastian": "Gipuzkoa",
    "Burgos": "Burgos",
    "Salamanca": "Salamanca",
    "Logrono": "La Rioja",
    "Cadiz": "Cádiz",
    "Albacete": "Albacete",
    "Avila": "Ávila",
    "Badajoz": "Badajoz",
    "Caceres": "Cáceres",
    "Castellon": "Castellón",
    "Ciudad Real": "Ciudad Real",
    "Cuenca": "Cuenca",
    "Girona": "Girona",
    "Guadalajara": "Guadalajara",
    "Huelva": "Huelva",
    "Huesca": "Huesca",
    "Jaen": "Jaén",
    "Leon": "León",
    "Lleida": "Lleida",
    "Lugo": "Lugo",
    "Ourense": "Ourense",
    "Palencia": "Palencia",
    "Pontevedra": "Pontevedra",
    "Segovia": "Segovia",
    "Soria": "Soria",
    "Tarragona": "Tarragona",
    "Teruel": "Teruel",
    "Zamora": "Zamora",
}


def slugify(text):
    text = text.lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def find_provincia(region, busqueda):
    """Encuentra la provincia para un negocio."""
    if region and region in PROVINCIAS:
        return PROVINCIAS[region]
    # Try busqueda mapping
    if busqueda and busqueda in BUSQUEDA_TO_REGION:
        mapped_region = BUSQUEDA_TO_REGION[busqueda]
        if mapped_region in PROVINCIAS:
            return PROVINCIAS[mapped_region]
    return None


def is_capital(city_name, capital):
    if not city_name:
        return False
    alias = CAPITAL_ALIASES.get(city_name, city_name)
    return slugify(alias) == slugify(capital) or alias.lower() == capital.lower()


def load_flat_negocios(filepath):
    """Carga negocios de formato plano (negocios_por_ciudad)."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_negocios = []
    if "negocios_por_ciudad" in data:
        for city, negocios in data["negocios_por_ciudad"].items():
            all_negocios.extend(negocios)
    return all_negocios


def load_provincial_negocios(filepath):
    """Carga negocios de formato provincial."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_negocios = []
    if "provincias" in data:
        for prov_data in data["provincias"].values():
            all_negocios.extend(prov_data.get("capital_negocios", []))
            for sc in prov_data.get("subcities", {}).values():
                all_negocios.extend(sc.get("negocios", []))
    return all_negocios


def main():
    # Load all businesses from both files
    all_businesses = []

    # Load existing (may be in provincial format or flat)
    with open(EXISTING, "r", encoding="utf-8") as f:
        existing_data = json.load(f)

    if "provincias" in existing_data:
        all_businesses.extend(load_provincial_negocios(EXISTING))
    elif "negocios_por_ciudad" in existing_data:
        all_businesses.extend(load_flat_negocios(EXISTING))

    print(f"Existing businesses: {len(all_businesses)}")

    # Load new businesses
    if os.path.exists(FALTANTES):
        new_businesses = load_flat_negocios(FALTANTES)
        all_businesses.extend(new_businesses)
        print(f"New businesses: {len(new_businesses)}")

    print(f"Total before dedup: {len(all_businesses)}")

    # Deduplicate by cid
    seen = set()
    unique = []
    for n in all_businesses:
        cid = n.get("cid")
        if cid and cid not in seen:
            seen.add(cid)
            unique.append(n)
    all_businesses = unique
    print(f"After dedup: {len(all_businesses)}")

    # Organize by province
    provincias = {}
    skipped = 0

    for n in all_businesses:
        region = n.get("region") or ""
        busqueda = n.get("ciudad_busqueda") or ""
        result = find_provincia(region, busqueda)

        if not result:
            skipped += 1
            continue

        prov_name, capital = result
        prov_slug = slugify(prov_name)
        ciudad = n.get("ciudad") or ""

        if prov_slug not in provincias:
            provincias[prov_slug] = {
                "nombre": prov_name,
                "capital": capital,
                "capital_slug": slugify(capital),
                "capital_negocios": [],
                "subcities": {}
            }

        actual_city = CAPITAL_ALIASES.get(ciudad, ciudad)

        if is_capital(actual_city, capital):
            n["ciudad"] = capital
            provincias[prov_slug]["capital_negocios"].append(n)
        else:
            city_slug = slugify(actual_city)
            # Skip invalid city slugs: empty, "null", purely numeric, or same as province slug
            if not city_slug or city_slug == "null" or city_slug.isdigit() or city_slug == prov_slug:
                # Assign to capital instead of creating bogus subcity
                n["ciudad"] = capital
                provincias[prov_slug]["capital_negocios"].append(n)
                continue
            if city_slug not in provincias[prov_slug]["subcities"]:
                provincias[prov_slug]["subcities"][city_slug] = {
                    "nombre": actual_city,
                    "negocios": []
                }
            provincias[prov_slug]["subcities"][city_slug]["negocios"].append(n)

    # Sort businesses within each group
    for prov_slug in provincias:
        provincias[prov_slug]["capital_negocios"].sort(
            key=lambda x: (x.get("rating") or 0, x.get("num_resenas") or 0), reverse=True
        )
        for sc in provincias[prov_slug]["subcities"].values():
            sc["negocios"].sort(
                key=lambda x: (x.get("rating") or 0, x.get("num_resenas") or 0), reverse=True
            )

    # Calculate totals
    total = 0
    for prov_slug in provincias:
        prov_total = len(provincias[prov_slug]["capital_negocios"])
        prov_total += sum(len(sc["negocios"]) for sc in provincias[prov_slug]["subcities"].values())
        provincias[prov_slug]["total"] = prov_total
        total += prov_total

    output = {
        "total": total,
        "provincias_count": len(provincias),
        "fecha_scraping": time.strftime("%Y-%m-%d"),
        "provincias": provincias,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)

    print(f"\nSkipped: {skipped}")
    print(f"Total negocios: {total}")
    print(f"Provincias: {len(provincias)}")
    print(f"Size: {size_mb:.1f} MB")
    print(f"\nDesglose:")
    for prov_slug in sorted(provincias.keys()):
        p = provincias[prov_slug]
        cap = len(p["capital_negocios"])
        sub = sum(len(sc["negocios"]) for sc in p["subcities"].values())
        n_sub = len(p["subcities"])
        print(f"  {p['nombre']} ({p['capital']}): {cap} capital + {sub} en {n_sub} localidades = {p['total']}")


if __name__ == "__main__":
    main()
