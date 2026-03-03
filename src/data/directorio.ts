import negociosData from './negocios.json';

export interface Negocio {
  cid: string;
  nombre: string;
  descripcion: string;
  categoria: string;
  categorias: string[];
  direccion: string;
  ciudad: string;
  region: string;
  codigo_postal: string;
  barrio: string;
  telefono: string;
  web: string;
  dominio: string;
  rating: number | null;
  num_resenas: number;
  rating_distribucion: Record<string, number>;
  latitud: number | null;
  longitud: number | null;
  verificado: boolean;
  imagen: string;
  total_fotos: number;
  horarios: Record<string, any[]> | null;
  estado: string;
  atributos: Record<string, string[]>;
  google_maps_url: string;
  ultima_actualizacion: string;
  ciudad_busqueda: string;
}

interface SubCity {
  nombre: string;
  negocios: Negocio[];
}

interface ProvinciaData {
  nombre: string;
  capital: string;
  capital_slug: string;
  total: number;
  capital_negocios: Negocio[];
  subcities: Record<string, SubCity>;
}

interface DatosDirectorio {
  total: number;
  provincias_count: number;
  fecha_scraping: string;
  provincias: Record<string, ProvinciaData>;
}

const data = negociosData as DatosDirectorio;

/** Devuelve las provincias para la home (solo capitales) */
export function getProvincias(): { nombre: string; slug: string; capital: string; total: number; capitalCount: number; subcitiesCount: number }[] {
  return Object.entries(data.provincias)
    .map(([slug, p]) => ({
      nombre: p.nombre,
      slug,
      capital: p.capital,
      total: p.total,
      capitalCount: p.capital_negocios.length,
      subcitiesCount: Object.keys(p.subcities).length,
    }))
    .sort((a, b) => b.total - a.total);
}

/** Datos completos de una provincia */
export function getProvincia(slug: string): ProvinciaData | undefined {
  return data.provincias[slug];
}

/** Negocios de la capital de una provincia */
export function getCapitalNegocios(provSlug: string): Negocio[] {
  return data.provincias[provSlug]?.capital_negocios || [];
}

/** Sub-ciudades de una provincia */
export function getSubcities(provSlug: string): { nombre: string; slug: string; count: number }[] {
  const prov = data.provincias[provSlug];
  if (!prov) return [];
  return Object.entries(prov.subcities)
    .map(([slug, sc]) => ({
      nombre: sc.nombre,
      slug,
      count: sc.negocios.length,
    }))
    .sort((a, b) => b.count - a.count);
}

/** Negocios de una sub-ciudad */
export function getSubcityNegocios(provSlug: string, citySlug: string): Negocio[] {
  return data.provincias[provSlug]?.subcities[citySlug]?.negocios || [];
}

/** Nombre de una sub-ciudad */
export function getSubcityNombre(provSlug: string, citySlug: string): string {
  return data.provincias[provSlug]?.subcities[citySlug]?.nombre || citySlug;
}

/** Todos los negocios de una provincia (capital + subcities) */
export function getAllProvinciaNegocios(provSlug: string): Negocio[] {
  const prov = data.provincias[provSlug];
  if (!prov) return [];
  const all = [...prov.capital_negocios];
  for (const sc of Object.values(prov.subcities)) {
    all.push(...sc.negocios);
  }
  return all;
}

/** Busca un negocio por slug en la capital */
export function getNegocioCapital(provSlug: string, negocioSlug: string): Negocio | undefined {
  const negocios = getCapitalNegocios(provSlug);
  return negocios.find((n) => slugify(n.nombre) === negocioSlug);
}

/** Busca un negocio por slug en una sub-ciudad */
export function getNegocioSubcity(provSlug: string, citySlug: string, negocioSlug: string): Negocio | undefined {
  const negocios = getSubcityNegocios(provSlug, citySlug);
  return negocios.find((n) => slugify(n.nombre) === negocioSlug);
}

export function getTotal(): number {
  return data.total;
}

export function getProvinciasCount(): number {
  return data.provincias_count;
}

export function getFechaScraping(): string {
  return data.fecha_scraping;
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export function formatCategoria(cat: string): string {
  const map: Record<string, string> = {
    'nail_salon': 'Salón de uñas',
    'beauty_salon': 'Salón de belleza',
    'manicure': 'Manicura',
    'Nail salon': 'Salón de uñas',
    'Beauty salon': 'Salón de belleza',
    'Hairdresser': 'Peluquería',
    'Facial spa': 'Spa facial',
    'Eyelash salon': 'Pestañas',
    'Laser hair removal service': 'Depilación láser',
    'Waxing hair removal service': 'Depilación con cera',
    'Massage therapist': 'Masajes',
    'Massage spa': 'Spa masajes',
  };
  return map[cat] || cat;
}

export function renderEstrellas(rating: number | null): string {
  if (!rating) return '';
  const full = Math.floor(rating);
  const half = rating - full >= 0.5;
  let stars = '★'.repeat(full);
  if (half) stars += '½';
  return stars;
}
