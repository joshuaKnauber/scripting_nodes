import Link from 'next/link';
import { HomeLayout } from 'fumadocs-ui/layouts/home';
import { DiscordIcon, GitHubIcon } from '@/components/brand-icons';
import { Logo } from '@/components/logo';
import { baseOptions } from '@/lib/layout.shared';
import { appName, discordUrl, githubUrl } from '@/lib/shared';

const iconLink =
  'inline-flex size-9 items-center justify-center rounded-full text-fd-muted-foreground transition-colors hover:text-fd-foreground focus-visible:outline-2 focus-visible:outline-fd-ring [&_svg]:size-[18px]';

function HomeHeader() {
  return (
    <header className="mx-auto flex h-16 w-full max-w-[1120px] items-center gap-2 px-6">
      <Link
        href="/"
        className="mr-auto flex items-center gap-2 font-medium focus-visible:outline-2 focus-visible:outline-fd-ring"
      >
        <Logo className="size-5" />
        {appName}
      </Link>
      <Link
        href="/docs"
        className="mr-1 px-2 text-sm font-medium text-fd-muted-foreground transition-colors hover:text-fd-foreground focus-visible:outline-2 focus-visible:outline-fd-ring"
      >
        Docs
      </Link>
      <a href={discordUrl} className={iconLink} aria-label="Discord">
        <DiscordIcon />
      </a>
      <a href={githubUrl} className={iconLink} aria-label="GitHub">
        <GitHubIcon />
      </a>
      <Link
        href="/docs/download"
        className="ml-2 hidden h-9 items-center rounded-full bg-fd-primary px-4 text-sm font-medium text-fd-primary-foreground transition-opacity hover:opacity-90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-fd-ring sm:inline-flex"
      >
        Download
      </Link>
    </header>
  );
}

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <HomeLayout {...baseOptions()} nav={{ enabled: false }}>
      <HomeHeader />
      {children}
    </HomeLayout>
  );
}
