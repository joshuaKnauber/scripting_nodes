import { createGetUrl } from 'fumadocs-core/source';

export const appName = 'Scripting Nodes';
export const siteUrl = 'https://scriptingnodes.com';
export const siteDescription =
  'Build Blender add-ons with nodes. Connect nodes and Scripting Nodes writes the Python, or ask an AI assistant to build the graph for you.';
export const docsRoute = '/docs';
export const docsImageRoute = '/og/docs';
export const docsContentRoute = '/llms.mdx/docs';

export const gitConfig = {
  user: 'joshuaknauber',
  repo: 'scripting_nodes',
  branch: 'main',
};

export const githubUrl = `https://github.com/${gitConfig.user}/${gitConfig.repo}`;
export const releasesUrl = `${githubUrl}/releases`;
export const discordUrl = 'https://discord.com/invite/NK6kyae';
export const supportFormUrl = 'https://tally.so/r/GxN99Z';

const getContentUrl = createGetUrl(docsContentRoute);

export function getPageMarkdownUrl(page: { slugs: string[]; locale?: string }) {
  const segments = [...page.slugs, 'content.md'];

  return { segments, url: getContentUrl(segments, page.locale) };
}

const getImageUrl = createGetUrl(docsImageRoute);

export function getPageImageUrl(page: { slugs: string[]; locale?: string }) {
  const segments = [...page.slugs, 'image.png'];

  return { segments, url: getImageUrl(segments, page.locale) };
}
