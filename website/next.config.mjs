import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const config = {
  output: 'export',
  reactStrictMode: true,
  // Static hosting has no image optimizer, serve images as-is
  images: { unoptimized: true },
  agentRules: false,
};

export default withMDX(config);
