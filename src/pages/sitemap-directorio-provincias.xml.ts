import { getProvincias, getSubcities } from '../data/directorio';

export async function GET() {
	const site = 'https://directorio-unas.vercel.app';
	const provincias = getProvincias();

	const urls: string[] = [];

	for (const p of provincias) {
		urls.push(`  <url>
    <loc>${site}/directorio/${p.slug}/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`);

		const subcities = getSubcities(p.slug);
		for (const sc of subcities) {
			urls.push(`  <url>
    <loc>${site}/directorio/${p.slug}/${sc.slug}/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>`);
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
