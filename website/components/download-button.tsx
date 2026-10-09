import { Download } from 'lucide-react';
import { releasesUrl } from '@/lib/shared';

/** Link to the latest release, styled like the header's Download button. */
export function DownloadButton() {
  return (
    <a
      href={`${releasesUrl}/latest`}
      className="not-prose inline-flex h-9 items-center gap-2 rounded-full bg-fd-primary px-4 text-sm font-medium text-fd-primary-foreground no-underline transition-opacity hover:opacity-90 [&_svg]:size-4"
    >
      <Download aria-hidden />
      Download latest release
    </a>
  );
}
