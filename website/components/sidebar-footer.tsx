import { Bug, Download } from 'lucide-react';
import type { ReactNode } from 'react';
import { DiscordIcon, GitHubIcon } from '@/components/brand-icons';
import { discordUrl, githubUrl, releasesUrl } from '@/lib/shared';

const links: { title: string; href: string; icon: ReactNode }[] = [
  { title: 'GitHub', href: githubUrl, icon: <GitHubIcon /> },
  { title: 'Discord', href: discordUrl, icon: <DiscordIcon /> },
  { title: 'Releases', href: releasesUrl, icon: <Download /> },
  { title: 'Report an issue', href: `${githubUrl}/issues`, icon: <Bug /> },
];

export function SidebarFooter() {
  return (
    <div className="flex flex-col gap-0.5">
      {links.map((link) => (
        <a
          key={link.href}
          href={link.href}
          target="_blank"
          rel="noreferrer noopener"
          className="flex h-8 items-center gap-2.5 rounded-lg px-2 text-sm font-medium text-fd-muted-foreground transition-colors hover:bg-fd-accent/50 hover:text-fd-accent-foreground [&_svg]:size-4"
        >
          {link.icon}
          {link.title}
        </a>
      ))}
    </div>
  );
}
