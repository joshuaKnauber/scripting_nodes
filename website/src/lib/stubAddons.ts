export type StubGradient = { from: string; to: string };

export type StubVersion = {
  version: string;
  released_at: string;
  changelog: string;
  blender_min: string;
  blender_max?: string;
  size_bytes: number;
  hash: string;
};

export type StubAddon = {
  id: string;
  name: string;
  tagline: string;
  description: string;
  cover: StubGradient;
  owner: string;
  license: string;
  tags: string[];
  versions: StubVersion[];
  gallery: Array<StubGradient & { alt: string }>;
};

export const stubAddons: StubAddon[] = [
  {
    id: 'node_wrangler_pro',
    name: 'Node Wrangler Pro',
    tagline: 'Power-user shortcuts and helpers for the shader editor.',
    description:
      'Extends the built-in Node Wrangler with quick-group menus, batch material conversion, and a configurable hotkey palette. Built entirely with Scripting Nodes.',
    cover: { from: '#7c3aed', to: '#2563eb' },
    owner: 'joshua_k',
    license: 'GPL-3.0-or-later',
    tags: ['Node', 'Material'],
    versions: [
      {
        version: '2.1.0',
        released_at: '2026-05-12',
        changelog:
          '- Added multi-select for the quick group menu\n- New batch material conversion shortcut (Ctrl+Shift+M)\n- Fixed crash when applying preset to materials with linked nodes',
        blender_min: '4.2.0',
        size_bytes: 412_000,
        hash: 'sha256:a3f5e2…',
      },
      {
        version: '2.0.0',
        released_at: '2026-03-04',
        changelog:
          '- Rewrote the hotkey palette to be fully configurable\n- Removed the legacy 1.x preferences panel\n- Breaking: keymap entries from 1.x will not migrate automatically',
        blender_min: '4.2.0',
        size_bytes: 398_000,
        hash: 'sha256:b1cd33…',
      },
      {
        version: '1.3.1',
        released_at: '2026-01-22',
        changelog: '- Fixed regression where group input sockets lost their default values',
        blender_min: '4.2.0',
        size_bytes: 312_000,
        hash: 'sha256:9e8aa4…',
      },
      {
        version: '1.3.0',
        released_at: '2025-12-08',
        changelog: '',
        blender_min: '4.2.0',
        size_bytes: 310_000,
        hash: 'sha256:114c77…',
      },
    ],
    gallery: [
      { from: '#1e293b', to: '#334155', alt: 'Shader editor overview' },
      { from: '#0f172a', to: '#1e293b', alt: 'Quick group menu' },
      { from: '#312e81', to: '#1e1b4b', alt: 'Hotkey palette' },
    ],
  },
  {
    id: 'quick_asset_browser',
    name: 'Quick Asset Browser',
    tagline: 'Pop-up asset browser bound to a single key.',
    description:
      'Adds a floating, searchable asset picker that opens anywhere in the 3D viewport. Reduces the click-cost of asset libraries to a single keystroke.',
    cover: { from: '#059669', to: '#0d9488' },
    owner: 'finn_k',
    license: 'GPL-3.0-or-later',
    tags: ['Asset Management', 'Workflow'],
    versions: [
      {
        version: '1.4.2',
        released_at: '2026-05-09',
        changelog:
          '- Fuzzy search now matches across both name and tags\n- Reduced first-open latency for libraries with 1k+ assets',
        blender_min: '4.3.0',
        size_bytes: 187_000,
        hash: 'sha256:c81a44…',
      },
      {
        version: '1.4.0',
        released_at: '2026-04-15',
        changelog: '- Added preview thumbnails to the picker\n- New "Recently used" section at the top of results',
        blender_min: '4.3.0',
        size_bytes: 179_000,
        hash: 'sha256:51f0d2…',
      },
    ],
    gallery: [
      { from: '#064e3b', to: '#065f46', alt: 'Floating picker' },
      { from: '#022c22', to: '#064e3b', alt: 'Search results' },
    ],
  },
  {
    id: 'retro_render_effects',
    name: 'Retro Render Effects',
    tagline: 'Scanline, chromatic aberration, and dithering compositor presets.',
    description:
      'A pack of compositor node groups that apply retro-game and analog-video looks. Drop them into your scene compositor and dial in the intensity.',
    cover: { from: '#db2777', to: '#9333ea' },
    owner: 'blender_artist_42',
    license: 'GPL-3.0-or-later',
    tags: ['Render', 'Compositor'],
    versions: [
      {
        version: '0.9.0',
        released_at: '2026-04-28',
        changelog: '- Added CRT bezel preset\n- All presets now expose intensity as a single driver-friendly value',
        blender_min: '4.2.0',
        size_bytes: 2_415_000,
        hash: 'sha256:fe22c7…',
      },
      {
        version: '0.8.0',
        released_at: '2026-03-12',
        changelog: '- New chromatic aberration preset\n- Tightened dithering grain at low intensities',
        blender_min: '4.2.0',
        size_bytes: 2_120_000,
        hash: 'sha256:771bd0…',
      },
      {
        version: '0.7.0',
        released_at: '2026-02-01',
        changelog: '- Initial public release with scanline and dithering presets',
        blender_min: '4.2.0',
        size_bytes: 1_980_000,
        hash: 'sha256:0a92e1…',
      },
    ],
    gallery: [
      { from: '#831843', to: '#581c87', alt: 'Scanline preset' },
      { from: '#4c1d95', to: '#1e1b4b', alt: 'CRT preset comparison' },
    ],
  },
  {
    id: 'auto_rigger_lite',
    name: 'Auto Rigger Lite',
    tagline: 'One-click biped rig from a posed mesh.',
    description:
      'Detects body landmarks on a posed mesh and generates a deformation rig with IK chains. Designed for fast previz, not for production.',
    cover: { from: '#ea580c', to: '#dc2626' },
    owner: 'rigging_master',
    license: 'GPL-3.0-or-later',
    tags: ['Rigging', 'Animation'],
    versions: [
      {
        version: '0.3.1',
        released_at: '2026-05-15',
        changelog: '',
        blender_min: '5.0.0',
        size_bytes: 998_000,
        hash: 'sha256:7d1bce…',
      },
    ],
    gallery: [
      { from: '#7c2d12', to: '#9a3412', alt: 'Landmark detection' },
      { from: '#450a0a', to: '#7f1d1d', alt: 'Generated rig' },
      { from: '#431407', to: '#7c2d12', alt: 'IK controls' },
    ],
  },
];

export function getAddon(id: string): StubAddon | undefined {
  return stubAddons.find((addon) => addon.id === id);
}

export function latestVersion(addon: StubAddon): StubVersion {
  return addon.versions[0];
}

export function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}
