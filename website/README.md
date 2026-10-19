# Scripting Nodes

Docs site built with [Fumadocs](https://fumadocs.dev) on Next.js, exported as a static site.

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # static site in out/
```

## Adding a docs page

Pages are MDX files in `content/docs/`. The file path is the URL:
`content/docs/nodes/events.mdx` → `/docs/nodes/events`. A folder in parentheses
groups pages in the sidebar without adding to the URL:
`content/docs/(getting-started)/concepts.mdx` → `/docs/concepts`.

```mdx
---
title: Events
description: One line shown under the title and in search.
icon: Zap  # sidebar icon, any lucide-react icon name
---

Content goes here.
```

Sidebar order and folder titles come from `meta.json` in each folder. Pages not
listed in `pages` are appended alphabetically, so listing them is only needed to
control order. `"---Label---"` adds a separator.

Available components without imports: `Accordions`/`Accordion` (`title`;
for details most readers can skip), `Callout` (`type`: info, tip, warn,
error, success; optional `title`), `Cards`/`Card`, `Steps`/`Step`, `Tabs`/`Tab`,
`Video` (`title`, `src`; a placeholder without `src`) and `DownloadButton`. See
`components/mdx.tsx` to add more.

## Screenshots

Images live in `public/screenshots/` and are referenced from MDX with an
absolute path. Every image can be clicked to zoom.

```mdx
![A Trigger node connected to a Print node](/screenshots/first-addon.webp)
```

Every screenshot is a scenario: a Python file in `screenshots/` that builds a
node tree inside Blender. The capture is framed on `wallpaper.jpg` (rounded
corners, shadow, a crop of the wallpaper per name), so don't drop in manual
screenshots.

```python
# screenshots/first-addon.py
import helpers  # tests/helpers.py

AREA_ONLY = True            # capture only the biggest area, not the whole window
WINDOW_SIZE = (900, 480)    # Blender window size in points
ZOOM_OUT = 3                # zoom steps out after framing the nodes
FRAME = "float"             # float, corner, right or bottom (edges it runs off)
# CROP = (0, 0, 0.8, 0.7)   # keep only this part of the capture (fractions)
# UI_SCALE = 1.25           # Blender's resolution scale
# LAYOUT = "split"          # node editor left, 3D viewport right
# SIDEBAR_TAB = "My Tab"    # sidebar tab to show


def setup():
    tree = helpers.new_tree("My Addon")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-200, 0))
    printer = helpers.add_node(tree, "SNA_Node_Print", (50, 0))
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    return tree


def after(context):  # optional, runs once the add-on has compiled the tree
    ...
```

Then render it to `public/screenshots/<name>.webp` (needs Pillow and
`BLENDER_EXECUTABLE` in the repo's `config.yaml`):

```bash
npm run screenshots                 # all scenarios
npm run screenshots -- first-addon  # only names containing "first-addon"
```

The `docs` skill (`.claude/skills/docs/`) has the guidelines for composing
shots and writing pages.

## Layout and styling

The docs chrome follows linear.app/docs (structure and type scale, not colors):

- `components/docs-header.tsx`: top bar with breadcrumb, theme toggle, page actions, Download
- `components/page-actions.tsx`: "Copy page" split button and its "Open in…" menu
- `components/sidebar-footer.tsx`: links at the bottom of the sidebar
- `app/docs/layout.tsx`: wires these into Fumadocs' `DocsLayout` and widens the header row
- `app/global.css`: typography and sidebar/TOC overrides
