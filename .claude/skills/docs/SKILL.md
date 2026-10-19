---
name: docs
description: Write or edit Scripting Nodes docs pages (website/content/docs) and make their screenshots. Use when asked to write, rewrite or review documentation, add a docs page, or create, update or fix screenshots for the docs.
---

# Docs

The docs site is Fumadocs in `website/`. Pages are MDX in `website/content/docs/`. Screenshots come from Python scenarios in `website/screenshots/`. `website/README.md` covers the site mechanics: frontmatter, `meta.json`, components.

Before making screenshots, read [screenshots.md](screenshots.md).

## Who reads this

Three readers, in this order:

1. **Beginners.** They know Blender, maybe not Python. They want to make the thing work. The top of every page is for them.
2. **People who want depth.** Edge cases, limitations, what the generated Python looks like. This goes further down the page or in an `<Accordion>`.
3. **LLMs** read `llms-full.txt`, the whole MDX including collapsed accordions. Be exact: real node and socket names, menu paths, property names. Don't leave out a detail because it's dull. Put it below, collapsed.

The page gets more detailed as it goes down. A beginner can stop after the first screen and still have something working.

## Page shape

```mdx
---
title: Timers
description: Run a flow after a delay or repeatedly.   # one sentence: what you can do with it
icon: Timer
---

One to three sentences: what it is and when you'd use it.

![Alt text that says what the shot shows](/screenshots/events-timers.webp)

## Using it        (the common case: <Steps> or a few bullets)
## <Options>       (a table of nodes, inputs or settings, when there are several)
## Limitations     (what doesn't work and what to do instead)

<Accordions>
  <Accordion title="What it generates">...Python...</Accordion>
</Accordions>
```

Leave out any section that has nothing to say. Short pages are fine. `nodes/interface/layouts.mdx` and `nodes/operators/creating-operators.mdx` are good examples of the tone.

## Writing rules

- **Lead with the task.** Start with "A **Timer** runs its flow after **Delay** seconds", not a history of the feature or a definition of timers in general.
- **Plain words, short sentences**, second person, present tense. Explain a Python or Blender term the first time a beginner meets it ("an operator, the action behind a button").
- **Name UI exactly as it appears.** Bold node, socket, panel and button names: **Run Operator**, **Execute**. Menu paths use ›: **Add › Logic › Modal**. Code, Python names and values go in backticks: `bpy.context`, `"MESH_DATA"`.
- **One idea per paragraph.** Use a table when you compare three or more things, and bullets for options or steps.
- **Link instead of re-explaining.** Link the first mention of a concept that has its own page.
- **Check against the code.** Read the node's source (`addon/scripting_nodes/src/nodes/categories/...`) for socket names, defaults and behavior. Never document what you assume a node does.
- **No filler.** No "simply", "just", "easily", "powerful", "seamlessly", no "In this guide we will", no closing summary. No emojis. Follow the `unslop` skill.
- **Callouts are rare.** Use at most one per page, for something that would otherwise bite the reader (`type="warn"`), not to decorate.
- **Generated Python is depth.** Show it in an `<Accordion title="What it generates">` or on development pages, not in the main text.

## Screenshots on a page

- The first screenshot goes right after the intro and shows the **result**, or the nodes next to the result. Further shots only when a section needs one.
- Alt text describes what's visible: "A sidebar panel with a split, a grid of objects and a progress ring, next to its nodes". Avoid "Screenshot of…".
- Reference `/screenshots/<name>.webp`. The scenario lives in `website/screenshots/<name>.py`. Name it `<section>-<topic>` (`interface-layouts`).
- Never drop in a manual screenshot. Everything is regenerated from scenarios when the UI changes.

## MDX pitfalls

One broken page breaks the whole dev server, so avoid these:

- Quote a frontmatter `description` that contains `: ` (`description: "Store settings: define them in a list"`).
- Write a `<` in text as `&lt;` (`**&lt;**`), and `{` / `}` outside code as `&#123;` / `&#125;`.
- Don't indent `<Accordion>` / `</Accordion>` tags: after a list item an indented closing tag doesn't parse.

## After editing

- `cd website && npm run check` must pass: it compiles every page and checks links and images.
- `npm run build` must pass when nothing else uses the folder (it shares `.next` with a running dev server).
- Look at the page in `npm run dev` when you changed layout or components.
- Run `python scripts/docs_screenshots.py <name>` for every scenario you touched, then look at each image (Read the .webp).
