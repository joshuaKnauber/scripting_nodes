import { baseOptions } from "@/lib/layout.shared";
import { HomeLayout } from "fumadocs-ui/layouts/home";
import { Link } from "react-router";
import type { Route } from "./+types/home";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Scripting Nodes" },
    { name: "description", content: "Visual scripting add-on for Blender" },
  ];
}

export default function Home() {
  return (
    <HomeLayout {...baseOptions()}>
      <main className="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
        <div className="max-w-3xl">
          <h1 className="mb-4 text-4xl font-bold md:text-5xl">
            Scripting Nodes
          </h1>
          <p className="mb-2 text-xl text-fd-muted-foreground md:text-2xl">
            Visual Scripting for Blender
          </p>
          <p className="mb-8 text-fd-muted-foreground">
            Create powerful Blender add-ons without writing a single line of
            code. Build with nodes, export production-ready Python.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              className="rounded-full bg-fd-primary px-6 py-3 font-medium text-fd-primary-foreground transition-colors hover:bg-fd-primary/90"
              to="/docs"
            >
              Get Started
            </Link>
            <a
              className="rounded-full border border-fd-border px-6 py-3 font-medium transition-colors hover:bg-fd-accent"
              href="https://discord.com/invite/NK6kyae"
              target="_blank"
              rel="noopener noreferrer"
            >
              Join Discord
            </a>
          </div>
        </div>
      </main>
    </HomeLayout>
  );
}
