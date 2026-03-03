import { getProvincias, getCapitalNegocios, getSubcities, getSubcityNegocios, slugify } from '../data/directorio';

export async function GET() {
	const site = 'https://directorio-unas.vercel.app';
	const provincias = getProvincias();

	const urls: string[] = [];

	for (const p of provincias) {
		// Capital businesses
		const capitalNegocios = getCapitalNegocios(p.slug);
		const subcities = getSubcities(p.slug);
		const subcitySlugs = new Set(subcities.map(sc => sc.slug));
		const seenCapital = new Set<string>();

		for (const n of capitalNegocios) {
			const nSlug = slugify(n.nombre);
			if (!nSlug || seenCapital.has(nSlug) || subcitySlugs.has(nSlug)) continue;
			seenCapital.add(nSlug);
			urls.push(`  <url>
    <loc>${site}/directorio/${p.slug}/${nSlug}/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.4</priority>
  </url>`);
		}

		// Subcity businesses
		for (const sc of subcities) {
			const negocios = getSubcityNegocios(p.slug, sc.slug);
			const seenSub = new Set<string>();
			for (const n of negocios) {
				const nSlug = slugify(n.nombre);
				if (!nSlug || seenSub.has(nSlug)) continue;
				seenSub.add(nSlug);
				urls.push(`  <url>
    <loc>${site}/directorio/${p.slug}/${sc.slug}/${nSlug}/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.3</priority>
  </url>`);
			}
		}
	}

	const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join('\n')}
</urlset>`;

	return new Response(xml, {
		headers: { 'Content-Type': 'application/xml' },
	});
}
