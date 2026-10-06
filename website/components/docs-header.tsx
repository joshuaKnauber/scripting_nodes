'use client';
import { useDocsLayout } from 'fumadocs-ui/layouts/docs';
import { useTreePath } from 'fumadocs-ui/contexts/tree';
import { useSearchContext } from 'fumadocs-ui/contexts/search';
import { Moon, Search, SidebarIcon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { type ComponentProps, Fragment } from 'react';
import { PageActions, type PageActionsProps } from '@/components/page-actions';
import { Logo } from '@/components/logo';
import { cn } from '@/lib/cn';
import { releasesUrl } from '@/lib/shared';

export type PageLinks = Record<string, Omit<PageActionsProps, 'className'>>;

const iconButton =
  'inline-flex size-8 shrink-0 items-center justify-center rounded-full text-fd-muted-foreground transition-colors hover:bg-fd-accent hover:text-fd-accent-foreground [&_svg]:size-4';

export function SearchButton({ className, ...props }: ComponentProps<'button'>) {
  const { setOpenSearch, enabled } = useSearchContext();
  if (!enabled) return null;
  return (
    <button
      type="button"
      aria-label="Search"
      onClick={() => setOpenSearch(true)}
      className={cn(iconButton, className)}
      {...props}
    >
      <Search />
    </button>
  );
}

function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  return (
    <button
      type="button"
      aria-label="Toggle theme"
      onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
      className={iconButton}
    >
      <Sun className="dark:hidden" />
      <Moon className="hidden dark:block" />
    </button>
  );
}

/** Top bar over the page and TOC columns: breadcrumb left, page actions right. */
export function DocsHeader({ pages }: { pages: PageLinks }) {
  const pathname = usePathname();
  const path = useTreePath();
  const { slots } = useDocsLayout();
  const links = pages[pathname] ?? pages[pathname.replace(/\/$/, '')];

  return (
    // contain + padding on the inner div: the header spans flexible grid
    // columns and must not feed its own width back into them
    <header className="[grid-area:header] [contain:inline-size] sticky top-(--fd-docs-row-1) z-30 h-(--fd-header-height) border-b bg-fd-background/80 backdrop-blur-sm">
      <div className="flex h-full items-center gap-2 px-4 md:px-8">
        <Link href="/" className="inline-flex items-center gap-2 font-medium md:hidden">
          <Logo className="size-5" />
          Docs
        </Link>
        <nav
          aria-label="Breadcrumb"
          className="flex min-w-0 items-center gap-2 text-sm max-md:hidden"
        >
          {path.map((node, i) => (
            <Fragment key={i}>
              {i > 0 && <span className="text-fd-muted-foreground/50">/</span>}
              <span
                className={cn(
                  'truncate',
                  i === path.length - 1 ? 'text-fd-foreground' : 'text-fd-muted-foreground',
                )}
              >
                {node.name}
              </span>
            </Fragment>
          ))}
        </nav>
        <div className="ms-auto flex items-center gap-2">
          <SearchButton className="md:hidden" />
          <ThemeToggle />
          {links && <PageActions {...links} className="max-md:hidden" />}
          <a
            href={releasesUrl}
            className="inline-flex h-8 items-center rounded-full bg-fd-primary px-3.5 text-sm font-medium text-fd-primary-foreground transition-opacity hover:opacity-90 max-sm:hidden"
          >
            Download
          </a>
          <slots.sidebar.trigger className={cn(iconButton, 'md:hidden')}>
            <SidebarIcon />
          </slots.sidebar.trigger>
        </div>
      </div>
    </header>
  );
}
