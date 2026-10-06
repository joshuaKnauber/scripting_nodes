import type { CSSProperties } from 'react';
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { DocsHeader, type PageLinks, SearchButton } from '@/components/docs-header';
import { SidebarFooter } from '@/components/sidebar-footer';
import { baseOptions } from '@/lib/layout.shared';
import { getPageMarkdownUrl, githubUrl, gitConfig } from '@/lib/shared';
import { source } from '@/lib/source';

const pages: PageLinks = Object.fromEntries(
  source.getPages().map((page) => [
    page.url,
    {
      markdownUrl: getPageMarkdownUrl(page).url,
      githubUrl: `${githubUrl}/blob/${gitConfig.branch}/website/content/docs/${page.path}`,
    },
  ]),
);

// Fumadocs' grid, but the header row spans the page and TOC columns (like
// linear.app/docs) and is shown at every width.
const containerStyle = {
  gridTemplate: `"sidebar sidebar header header header"
"sidebar sidebar toc-popover toc toc"
"sidebar sidebar main toc toc" 1fr / minmax(min-content, 1fr) var(--fd-sidebar-col) minmax(0, calc(var(--fd-layout-width,97rem) - var(--fd-sidebar-width) - var(--fd-toc-width))) var(--fd-toc-width) minmax(min-content, 1fr)`,
  '--fd-header-height': '64px',
} as CSSProperties;

export default function Layout({ children }: LayoutProps<'/docs'>) {
  const base = baseOptions();
  return (
    <DocsLayout
      tree={source.getPageTree()}
      {...base}
      // Theme toggle and GitHub live in the header and sidebar footer instead
      githubUrl={undefined}
      themeSwitch={{ enabled: false }}
      searchToggle={{ enabled: false }}
      nav={{
        ...base.nav,
        children: <SearchButton className="ms-auto" />,
        component: <DocsHeader pages={pages} />,
      }}
      sidebar={{ collapsible: false, footer: <SidebarFooter /> }}
      containerProps={{ style: containerStyle }}
    >
      {children}
    </DocsLayout>
  );
}
