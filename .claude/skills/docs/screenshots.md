# Screenshots

The look follows Linear's product shots: a cropped Blender window with rounded corners and a soft shadow, set on a crop of `website/wallpaper.jpg`, often running off one edge of the image. The framing is automatic. Your job is the **composition**: what's in the window and how big it is.

## Pipeline

```bash
python scripts/docs_screenshots.py interface-layouts   # names containing this; no args = all
```

1. `website/screenshots/<name>.py` builds the scene in GUI Blender (`tests/visual/driver.py`, a throwaway profile, about 5 s per shot).
2. The capture is cropped (`CROP`) and framed on the wallpaper (`scripts/screenshot_frame.py`). Each name gets its own wallpaper crop, so shots next to each other differ.
3. Saved as `website/public/screenshots/<name>.webp`, at most 2400 px wide.

Files starting with `_` are shared builders (`_demo.py`, `_properties.py`). Reuse them so several shots show the same example add-on.

## Scenario settings

| Setting | Default | |
| --- | --- | --- |
| `setup()` | | Builds the scene, returns the tree to show (or `None` to keep the 3D viewport) |
| `after(context)` | | Runs once the add-on has compiled: open panels, hide the sidebar, select things |
| `WINDOW_SIZE` | `(1600, 1000)` | Blender window in points (the capture is 2x on Retina) |
| `AREA_ONLY` | `False` | Capture only the biggest area instead of the whole window |
| `LAYOUT = "split"` | | Node editor left, 3D viewport right |
| `SIDEBAR_TAB` | `"Scripting Nodes"` | Sidebar tab shown in every area |
| `ZOOM_OUT` | `0` | Zoom steps out after framing all nodes |
| `UI_SCALE` | `1.0` | Blender's resolution scale |
| `CROP` | `None` | `(x0, y0, x1, y1)` as fractions: keep only this part of the capture |
| `FRAME` | `"float"` | Where the window sits on the wallpaper, see below |

## Placement (`FRAME`)

- `float`: wallpaper on all sides. For small, complete captures: a few nodes, a single panel.
- `corner`: runs off the right and bottom edges. For full windows and split layouts. The cut edges hide the clutter of the window (properties editor, timeline).
- `right` / `bottom`: runs off one edge. For a wide or tall capture where one side doesn't matter, e.g. a viewport with the panel on the right.

A cut edge says "this continues". Cut only where nothing important is, and only through the edges that run off the image. If `CROP` cuts the left or top, the cut runs straight through the window's content, because those edges keep their padding. Crop left and top only along area borders.

## Composition rules

1. **One subject per shot.** Decide what the reader should see (the panel the nodes draw, the operator's settings) and make that the biggest, clearest thing. Leave out what doesn't help: crop away the properties editor, timeline and status bar, and hide the node editor's sidebar unless it's the subject.
2. **Readable at page size.** The docs column is about 800 px wide. Read the .webp and ask whether the subject's text is readable at that width. If not:
   - make the window smaller (`WINDOW_SIZE`). The capture scales down less, so text stays bigger;
   - place the nodes closer together. `view_all` fits the whole tree, so wide trees get tiny nodes. Space nodes about 200–250 units apart horizontally, not 400;
   - crop tighter (`CROP`), or split one busy shot into two (nodes, then result);
   - `UI_SCALE` grows the sidebar and headers, but nodes only grow if the tree is compact, so fix spacing first.
3. **No empty space.** A shot that is half empty grid or empty viewport wastes the reader's attention. Shrink the area or move the nodes.
4. **Real content.** Name trees, panels and operators like a real add-on ("Object Tools", "Arrange Objects"), not "Node Tree" or "Test". Fill in values ("Hello!", `3`) so fields aren't empty. Select an object when the panel depends on it.
5. **Clean state.** No tooltips (the driver turns them off), no error popups, no half-typed fields, no `[INFO]` overlays unless they're the point.
6. **Consistent example.** Within a section, reuse one example add-on (a shared `_*.py` builder), so readers recognize the same nodes across pages.

## Helpers that already exist

- **Popups and dialogs** (operator dialogs, menus, settings popups): an operator started directly in `after()` opens nothing in the capture. Use `invoke_in(context, "VIEW_3D", "my_addon.op", mouse=(0.5, 0.55), delay=1.0)` from `_operators_common.py`. It moves the cursor to where the popup should open and runs the operator with `INVOKE_DEFAULT` from a timer, in that area. See `operators-dialog.py`.
- **Small nodes:** `view_all` leaves wide margins. `zoom_in()` in `_operators_common.py`, or `_blend_data_zoom.py`, zooms in again after the driver has framed the tree.
- **Example add-ons:** `_start_addon.py` (Monkey Tools), `_interface_tools.py` (Object Tools panel), `_data_panel.py`, `_concepts_graph.py`, `_publishing.py`. Reuse them before building a new one.

## Checking a shot

Always look at the result (Read the .webp) before you're done. Check these:

- Is the subject the first thing you see, and readable?
- Are the cut edges only where nothing matters, with no label or button sliced in half?
- Did the scenario fail silently? A missing panel, the wrong sidebar tab or a node error badge usually means a socket key changed. Fix the scenario.
- Does the wallpaper crop clash with the window (dark window on dark purple)? Renaming the file changes the crop. Usually it's fine.

Iterate: change one setting, re-render that one name, look again.
