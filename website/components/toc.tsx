'use client';
import { useTOCItems } from 'fumadocs-ui/components/toc';
import { useEffect, useMemo, useState } from 'react';
import { cn } from '@/lib/cn';

// A heading becomes active once it scrolls above this line (px from the top)
const ACTIVE_LINE = 160;

/** The last heading above the active line, or the last one at the page end. */
function useActiveHeading(urls: string[]) {
  const [active, setActive] = useState<string | undefined>(urls[0]);

  useEffect(() => {
    const update = () => {
      const root = document.documentElement;
      if (window.scrollY + window.innerHeight >= root.scrollHeight - 2) {
        setActive(urls.at(-1));
        return;
      }
      let current = urls[0];
      for (const url of urls) {
        const top = document.getElementById(url.slice(1))?.getBoundingClientRect().top;
        if (top !== undefined && top < ACTIVE_LINE) current = url;
      }
      setActive(current);
    };
    update();
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    return () => {
      window.removeEventListener('scroll', update);
      window.removeEventListener('resize', update);
    };
  }, [urls]);

  return active;
}

/**
 * Table of contents modeled on linear.app/docs: plain list on a hairline
 * track (each entry's left border), the active entry darkens its text and
 * its piece of the track.
 * Replaces Fumadocs' animated thumb (DocsPage `tableOfContent.component`).
 */
export function PageTOC() {
  const items = useTOCItems();
  const urls = useMemo(() => items.map((item) => item.url), [items]);
  const active = useActiveHeading(urls);

  if (items.length === 0) {
    return <div id="nd-toc-placeholder" className="hidden xl:layout:[--fd-toc-width:268px]" />;
  }

  return (
    <div
      id="nd-toc"
      className="sticky [grid-area:toc] flex w-(--fd-toc-width) flex-col pt-12 pe-6 pb-2 max-xl:hidden xl:layout:[--fd-toc-width:268px]"
    >
      <ul className="min-h-0 overflow-y-auto [scrollbar-width:none]">
        {items.map((item) => (
          <li key={item.url}>
            <a
              href={item.url}
              data-active={item.url === active}
              className={cn(
                'block border-s py-1 text-[13px] leading-[19.5px] text-fd-muted-foreground transition-colors hover:text-fd-foreground data-[active=true]:border-fd-foreground data-[active=true]:text-fd-foreground',
                item.depth <= 2 ? 'ps-3.5' : 'ps-6.5',
              )}
            >
              {item.title}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
