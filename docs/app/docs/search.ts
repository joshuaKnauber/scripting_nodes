import { source } from "@/lib/source";
import { createFromSource } from "fumadocs-core/search/server";

const server = createFromSource(source, {
  language: "english",
});

// Use staticGET for static export - generates a pre-built search index
export async function loader() {
  return server.staticGET();
}
