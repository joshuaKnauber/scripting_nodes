# Scripting Nodes

Docs site built with [Fumadocs](https://fumadocs.dev) on Next.js, exported as a static site.

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # static site in out/
```

## Adding a docs page

Pages are MDX files in `content/docs/`. The file path is the URL:
`content/docs/concepts/sockets.mdx` → `/docs/concepts/sockets`.

```mdx
---
title: Sockets
description: One line shown under the title and in search.
---

Content goes here.
```

Sidebar order and folder titles come from `meta.json` in each folder. Pages not
listed in `pages` are appended alphabetically, so listing them is only needed to
control order. `"---Label---"` adds a separator.

Available components without imports: `Callout`, `Cards`/`Card`, `Steps`/`Step`,
`Tabs`/`Tab`. See `components/mdx.tsx` to add more.

## Screenshots

Images live in `public/screenshots/` and are referenced from MDX with an
absolute path. Every image can be clicked to zoom.

```mdx
![A Trigger node connected to a Print node](/screenshots/first-addon.png)
```

You can drop a manual screenshot in there, but prefer a scenario so it can be
regenerated when the UI changes. A scenario is a Python file in `screenshots/`
that builds a node tree inside Blender:

```python
# screenshots/first-addon.py
import helpers  # tests/helpers.py

AREA_ONLY = True            # capture only the node editor, not the whole window
WINDOW_SIZE = (900, 480)    # Blender window size in pixels
ZOOM_OUT = 3                # zoom steps out after framing the nodes


def setup():
    tree = helpers.new_tree("My Addon")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-200, 0))
    printer = helpers.add_node(tree, "SNA_Node_Print", (50, 0))
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    return tree


def after(context):  # optional, runs once the add-on has compiled the tree
    ...
```

Then render it to `public/screenshots/<name>.png` (needs `BLENDER_EXECUTABLE`
in the repo's `config.yaml`):

```bash
npm run screenshots                 # all scenarios
npm run screenshots -- first-addon  # only names containing "first-addon"
```

## Layout and styling

The docs chrome follows linear.app/docs (structure and type scale, not colors):

- `components/docs-header.tsx`: top bar with breadcrumb, theme toggle, page actions, Download
- `components/page-actions.tsx`: "Copy page" split button and its "Open in…" menu
- `components/sidebar-footer.tsx`: links at the bottom of the sidebar
- `app/docs/layout.tsx`: wires these into Fumadocs' `DocsLayout` and widens the header row
- `app/global.css`: typography and sidebar/TOC overrides
