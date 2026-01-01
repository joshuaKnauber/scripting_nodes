import type { Config } from "@react-router/dev/config";
import fg from "fast-glob";
import { createGetUrl, getSlugs } from "fumadocs-core/source";

const getUrl = createGetUrl("/docs");
const isProduction = process.env.NODE_ENV === "production";

export default {
  ssr: true,
  basename: isProduction ? "/scripting_nodes" : "/",
  async prerender({ getStaticPaths }) {
    const paths: string[] = [];
    const excluded: string[] = [];

    for (const path of getStaticPaths()) {
      if (!excluded.includes(path)) paths.push(path);
    }

    const entries = await fg("**/*.mdx", { cwd: "content/docs" });
    for (const entry of entries) {
      paths.push(getUrl(getSlugs(entry)));
    }

    return paths;
  },
} satisfies Config;
