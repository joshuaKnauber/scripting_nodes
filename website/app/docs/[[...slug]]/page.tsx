import { source } from '@/lib/source';
import { DocsBody, DocsDescription, DocsPage, DocsTitle } from 'fumadocs-ui/layouts/docs/page';
import { notFound } from 'next/navigation';
import { getMDXComponents } from '@/components/mdx';
import type { Metadata } from 'next';
import { createRelativeLink } from 'fumadocs-ui/mdx';
import { getBreadcrumbItems } from 'fumadocs-core/breadcrumb';
import { JsonLd } from '@/components/json-ld';
import { appName, getPageImageUrl, siteUrl } from '@/lib/shared';
import { PageTOC } from '@/components/toc';

export default async function Page(props: PageProps<'/docs/[[...slug]]'>) {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();

  const MDX = page.data.body;

  // Breadcrumb and page actions live in the layout header (components/docs-header.tsx)
  return (
    <DocsPage
      toc={page.data.toc}
      full={page.data.full}
      breadcrumb={{ enabled: false }}
      tableOfContent={{ component: <PageTOC /> }}
      // 650px text column, as on linear.app/docs
      className="max-w-[714px] md:pt-10 xl:pt-12"
    >
      <JsonLd data={breadcrumbJsonLd(page)} />
      <DocsTitle className="text-[32px] leading-9 tracking-[-0.022em]">{page.data.title}</DocsTitle>
      <DocsDescription className="mt-2 mb-0 text-[15px] leading-6 text-fd-foreground">
        {page.data.description}
      </DocsDescription>
      <DocsBody>
        <MDX
          components={getMDXComponents({
            // this allows you to link to other pages with relative file paths
            a: createRelativeLink(source, page),
          })}
        />
      </DocsBody>
    </DocsPage>
  );
}

/** Docs > folders that have a page > this page, as shown in search results */
function breadcrumbJsonLd(page: NonNullable<ReturnType<typeof source.getPage>>) {
  const folders = getBreadcrumbItems(page.url, source.getPageTree()).filter(
    (item) => item.url && item.url !== page.url && typeof item.name === 'string',
  );
  const items = [
    { name: 'Docs', url: '/docs' },
    ...folders.map((item) => ({ name: item.name as string, url: item.url! })),
    { name: page.data.title, url: page.url },
  ].filter((item, i, all) => all.findIndex((other) => other.url === item.url) === i);

  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: item.name,
      item: `${siteUrl}${item.url}`,
    })),
  };
}

export async function generateStaticParams() {
  return source.generateParams();
}

export async function generateMetadata(props: PageProps<'/docs/[[...slug]]'>): Promise<Metadata> {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();

  return {
    title: page.data.title,
    description: page.data.description,
    alternates: { canonical: page.url },
    // Replaces the root openGraph object, so repeat the site name
    openGraph: {
      siteName: appName,
      type: 'article',
      url: page.url,
      images: getPageImageUrl(page).url,
    },
  };
}
