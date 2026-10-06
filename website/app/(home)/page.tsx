import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
      <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Scripting Nodes</h1>
      <p className="max-w-md text-lg text-fd-muted-foreground">
        Build Blender add-ons visually with nodes.
      </p>
      <div className="mt-4 flex flex-wrap justify-center gap-3">
        <Link
          href="/docs"
          className="rounded-lg bg-fd-primary px-5 py-2.5 font-medium text-fd-primary-foreground"
        >
          Read the docs
        </Link>
        <a
          href="https://github.com/joshuaknauber/scripting_nodes"
          className="rounded-lg border px-5 py-2.5 font-medium hover:bg-fd-accent"
        >
          GitHub
        </a>
      </div>
    </main>
  );
}
