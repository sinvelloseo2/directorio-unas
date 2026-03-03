export async function GET() {
	const site = 'https://directorio-unas.vercel.app';
	const sitemaps = [
		'sitemap-paginas.xml',
		'sitemap-blog.xml',
		'sitemap-directorio-provincias.xml',
		'sitemap-directorio-negocios.xml',
	];

	const xml = `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemaps.map(s => `  <sitemap><loc>${site}/${s}</loc></sitemap>`).join('\n')}
</sitemapindex>`;

	return new Response(xml, {
		headers: { 'Content-Type': 'application/xml' },
	});
}
