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
      <div className="p-4 flex flex-col items-center justify-center text-center flex-1">
        <h1 className="text-xl font-bold mb-2">Scripting Nodes</h1>
        <p className="text-fd-muted-foreground mb-4">
          Visual scripting add-on for Blender that lets you create add-ons
          through node graphs
        </p>
        <Link
          className="text-sm bg-fd-primary text-fd-primary-foreground rounded-full font-medium px-4 py-2.5"
          to="/docs"
        >
          Get Started
        </Link>
      </div>
    </HomeLayout>
  );
}
