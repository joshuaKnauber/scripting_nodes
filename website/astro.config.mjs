// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
  integrations: [
    starlight({
      title: 'Scripting Nodes',
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/joshuaknauber/scripting_nodes' },
      ],
      sidebar: [],
    }),
  ],
});