import { getCollection } from 'astro:content';

export async function GET() {
	const site = 'https://directorio-unas.vercel.app';
	const posts = (await getCollection('blog')).sort(
		(a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
	);

	const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${posts.map(post => `  <url>
    <loc>${site}/blog/${post.id}/</loc>
    <lastmod>${post.data.updatedDate?.toISOString().split('T')[0] ?? post.data.pubDate.toISOString().split('T')[0]}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>`).join('\n')}
</urlset>`;

	return new Response(xml, {
		headers: { 'Content-Type': 'application/xml' },
	});
}
