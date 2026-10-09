import { source } from '@/lib/source';
import { notFound } from 'next/navigation';
import { ogImage } from '@/lib/og/image';
import { appName, getPageImageUrl } from '@/lib/shared';

export const revalidate = false;

export async function GET(_req: Request, { params }: RouteContext<'/og/docs/[...slug]'>) {
  const { slug } = await params;
  const page = source.getPage(slug.slice(0, -1));
  if (!page) notFound();

  return ogImage({ title: page.data.title, label: `${appName} Docs` });
}

export function generateStaticParams() {
  return source.getPages().map((page) => ({
    lang: page.locale,
    slug: getPageImageUrl(page).segments,
  }));
}
