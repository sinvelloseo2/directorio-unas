export async function GET() {
	const site = 'https://directorio-unas.vercel.app';

	const pages = [
		{ url: '/', priority: '1.0', changefreq: 'weekly' },
		{ url: '/about/', priority: '0.5', changefreq: 'monthly' },
		{ url: '/tecnicas/', priority: '0.8', changefreq: 'monthly' },
		{ url: '/tendencias/', priority: '0.8', changefreq: 'monthly' },
		{ url: '/blog/', priority: '0.8', changefreq: 'weekly' },
	];

	const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map(p => `  <url>
    <loc>${site}${p.url}</loc>
    <changefreq>${p.changefreq}</changefreq>
    <priority>${p.priority}</priority>
  </url>`).join('\n')}
</urlset>`;

	return new Response(xml, {
		headers: { 'Content-Type': 'application/xml' },
	});
}
