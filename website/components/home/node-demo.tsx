'use client';

import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
} from 'react';

/*
 * A small Blender window: a node editor next to a 3D viewport (or text
 * editor). Pick a request, the graph builds itself and the viewport's
 * sidebar shows the panel it makes. Nodes can be dragged, the editor
 * panned, and the text fields in the nodes edited live.
 */

type Kind = 'flow' | 'logic' | 'interface' | 'string' | 'number' | 'data';

const SOCKET: Record<Kind, string> = {
  flow: '#8f8f8f',
  logic: '#e8e8e8',
  interface: '#f2a60d',
  string: '#6f9cff',
  number: '#a8a8a8',
  data: '#3fc1a3',
};

interface Row {
  id: string;
  label: string;
  kind: Kind;
  side: 'in' | 'out';
  /** key of an editable value shown as a field while the socket is free */
  field?: string;
  /** read-only value shown in the row */
  fixed?: string;
}

interface NodeDef {
  id: string;
  title: string;
  x: number;
  y: number;
  w: number;
  rows: Row[];
}

type Link = [from: string, out: string, to: string, input: string];
type Values = Record<string, string>;
type Point = { x: number; y: number };

interface Scenario {
  /** tab label */
  label: string;
  prompt: string;
  /** what the right area shows: the 3D viewport sidebar or the Info log */
  result: 'panel' | 'log';
  nodes: NodeDef[];
  links: Link[];
  defaults: Values;
  panel?: (v: Values, actions: Actions) => ReactNode;
  code: (v: Values) => string;
}

interface Actions {
  /** the Add Cube operator */
  addCube: () => void;
  /** objects in the scene: the cubes plus the default camera and light */
  objects: number;
}

const snake = (text: string, fallback: string) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '') || fallback;

const py = (text: string) => `'${text.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}'`;

const SCENARIOS: Scenario[] = [
  {
    label: 'A button',
    prompt: 'Add a button to the sidebar that adds a cube',
    result: 'panel',
    nodes: [
      {
        id: 'panel',
        title: 'Panel',
        x: 40,
        y: 70,
        w: 170,
        rows: [
          { id: 'body', label: 'Interface', kind: 'interface', side: 'out' },
          { id: 'label', label: 'Label', kind: 'string', side: 'in', field: 'panel' },
        ],
      },
      {
        id: 'button',
        title: 'Button',
        x: 330,
        y: 110,
        w: 190,
        rows: [
          { id: 'next', label: 'Interface', kind: 'interface', side: 'out' },
          { id: 'in', label: 'Interface', kind: 'interface', side: 'in' },
          { id: 'op', label: 'Operator', kind: 'data', side: 'in', fixed: 'Add Cube' },
          { id: 'label', label: 'Label', kind: 'string', side: 'in', field: 'button' },
        ],
      },
    ],
    links: [['panel', 'body', 'button', 'in']],
    defaults: { panel: 'My Tools', button: 'Add Cube' },
    panel: (v, { addCube }) => (
      <BlenderPanel title={v.panel}>
        <BlenderButton onClick={addCube}>{v.button || 'Add Cube'}</BlenderButton>
      </BlenderPanel>
    ),
    code: (v) => `import bpy


class MY_ADDON_PT_${snake(v.panel, 'panel')}(bpy.types.Panel):
    bl_label = ${py(v.panel)}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        self.layout.operator('mesh.primitive_cube_add', text=${py(v.button)})`,
  },
  {
    label: 'A live label',
    prompt: 'Show how many objects are in the scene, with a button to add cubes',
    result: 'panel',
    nodes: [
      {
        id: 'panel',
        title: 'Panel',
        x: 10,
        y: 30,
        w: 150,
        rows: [
          { id: 'body', label: 'Interface', kind: 'interface', side: 'out' },
          { id: 'label', label: 'Label', kind: 'string', side: 'in', field: 'panel' },
        ],
      },
      {
        id: 'button',
        title: 'Button',
        x: 210,
        y: 14,
        w: 175,
        rows: [
          { id: 'next', label: 'Interface', kind: 'interface', side: 'out' },
          { id: 'in', label: 'Interface', kind: 'interface', side: 'in' },
          { id: 'op', label: 'Operator', kind: 'data', side: 'in', fixed: 'Add Cube' },
          { id: 'label', label: 'Label', kind: 'string', side: 'in', field: 'button' },
        ],
      },
      {
        id: 'objects',
        title: 'Scene Objects',
        x: 10,
        y: 215,
        w: 130,
        rows: [{ id: 'objects', label: 'Objects', kind: 'data', side: 'out' }],
      },
      {
        id: 'length',
        title: 'Length',
        x: 175,
        y: 225,
        w: 105,
        rows: [
          { id: 'length', label: 'Length', kind: 'number', side: 'out' },
          { id: 'list', label: 'List', kind: 'data', side: 'in' },
        ],
      },
      {
        id: 'join',
        title: 'Combine Strings',
        x: 315,
        y: 200,
        w: 150,
        rows: [
          { id: 'text', label: 'Combined', kind: 'string', side: 'out' },
          { id: 'a', label: 'String', kind: 'string', side: 'in', field: 'prefix' },
          { id: 'b', label: 'String', kind: 'string', side: 'in' },
        ],
      },
      {
        id: 'label',
        title: 'Label',
        x: 475,
        y: 60,
        w: 140,
        rows: [
          { id: 'next', label: 'Interface', kind: 'interface', side: 'out' },
          { id: 'in', label: 'Interface', kind: 'interface', side: 'in' },
          { id: 'text', label: 'Text', kind: 'string', side: 'in' },
        ],
      },
    ],
    links: [
      ['panel', 'body', 'button', 'in'],
      ['button', 'next', 'label', 'in'],
      ['objects', 'objects', 'length', 'list'],
      ['length', 'length', 'join', 'b'],
      ['join', 'text', 'label', 'text'],
    ],
    defaults: { panel: 'Scene', button: 'Add Cube', prefix: 'Objects: ' },
    panel: (v, { addCube, objects }) => (
      <BlenderPanel title={v.panel}>
        <BlenderButton onClick={addCube}>{v.button || 'Add Cube'}</BlenderButton>
        <p className="px-1 pt-1.5 pb-0.5">
          {v.prefix}
          {objects}
        </p>
      </BlenderPanel>
    ),
    code: (v) => `import bpy


class MY_ADDON_PT_${snake(v.panel, 'panel')}(bpy.types.Panel):
    bl_label = ${py(v.panel)}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        self.layout.operator('mesh.primitive_cube_add', text=${py(v.button)})
        count = len(context.scene.objects)
        self.layout.label(text=${py(v.prefix)} + str(count))`,
  },
  {
    label: 'An event',
    prompt: 'Print a message every time the file is saved',
    result: 'log',
    nodes: [
      {
        id: 'save',
        title: 'On Save',
        x: 70,
        y: 110,
        w: 160,
        rows: [{ id: 'flow', label: 'Logic', kind: 'logic', side: 'out' }],
      },
      {
        id: 'print',
        title: 'Print',
        x: 330,
        y: 110,
        w: 190,
        rows: [
          { id: 'next', label: 'Program', kind: 'flow', side: 'out' },
          { id: 'in', label: 'Program', kind: 'flow', side: 'in' },
          { id: 'text', label: 'Text', kind: 'string', side: 'in', field: 'message' },
        ],
      },
    ],
    links: [['save', 'flow', 'print', 'in']],
    defaults: { message: 'Saved!' },
    code: (v) => `import bpy
from bpy.app.handlers import persistent


@persistent
def on_save_post(*args):
    print(${py(v.message)})


def register():
    bpy.app.handlers.save_post.append(on_save_post)`,
  },
];

// -- geometry ----------------------------------------------------------------

/** design size of the graph; the canvas fits it, then the user can pan */
const WIDTH = 620;
const HEIGHT = 330;
const HEADER = 26;
const ROW = 24;

function socketPoint(node: NodeDef, at: Point, rowId: string, side: 'in' | 'out') {
  const index = node.rows.findIndex((r) => r.id === rowId && r.side === side);
  return {
    x: side === 'out' ? at.x + node.w : at.x,
    y: at.y + HEADER + 4 + index * ROW + ROW / 2,
  };
}

function linkPath(a: Point, b: Point) {
  const dx = Math.max(40, Math.abs(b.x - a.x) / 2);
  return `M ${a.x} ${a.y} C ${a.x + dx} ${a.y}, ${b.x - dx} ${b.y}, ${b.x} ${b.y}`;
}

// -- pieces of Blender UI ----------------------------------------------------

function BlenderPanel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-[5px] bg-[var(--sn-panel)] p-1.5 text-[12px] text-[var(--sn-strong)]">
      <div className="flex items-center gap-1.5 px-1 pb-1.5">
        <Chevron />
        {title || 'Panel'}
      </div>
      {children}
    </div>
  );
}

function BlenderButton({ children, onClick }: { children: ReactNode; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded-[4px] bg-[var(--sn-button)] py-[3px] text-center text-[var(--sn-strong)] shadow-[0_1px_0_rgba(0,0,0,0.3)] ring-1 ring-black/10 dark:ring-0 hover:bg-[var(--sn-button-hover)] focus-visible:outline-1 focus-visible:outline-[#f2a60d] active:brightness-90"
    >
      {children}
    </button>
  );
}

function Chevron() {
  return (
    <svg viewBox="0 0 10 10" className="size-2.5 shrink-0 text-[var(--sn-dim)]" aria-hidden>
      <path d="M2 3.5 5 6.5 8 3.5" fill="none" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  );
}

function SocketDot({ kind, side }: { kind: Kind; side: 'in' | 'out' }) {
  const diamond = kind === 'flow' || kind === 'logic' || kind === 'interface';
  return (
    <span
      aria-hidden
      className="absolute top-1/2 size-[10px] border border-black/60"
      style={{
        background: SOCKET[kind],
        [side === 'in' ? 'left' : 'right']: -5,
        borderRadius: diamond ? 1 : '50%',
        transform: `translateY(-50%)${diamond ? ' rotate(45deg) scale(0.85)' : ''}`,
      }}
    />
  );
}

/** Header row of a Blender area: editor type, menus, extras */
function AreaHeader({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-[30px] shrink-0 items-center gap-0.5 bg-[var(--sn-header)] px-1.5 text-[12px] text-[var(--sn-text)]">
      {children}
    </div>
  );
}

function Menus({ items }: { items: string[] }) {
  return (
    <>
      {items.map((item) => (
        <span key={item} className="rounded-[4px] px-2 py-0.5" aria-hidden>
          {item}
        </span>
      ))}
    </>
  );
}

function EditorIcon({ kind }: { kind: 'node' | 'view3d' | 'text' | 'info' }) {
  const paths = {
    node: 'M2 3h4v3H2zM10 9h4v3h-4zM6 4.5c3 0 1 6 4 6',
    view3d: 'M8 2 13.5 5v6L8 14 2.5 11V5zM8 8v6M8 8l5.5-3M8 8 2.5 5',
    text: 'M3 3h10M3 6h7M3 9h10M3 12h6',
    info: 'M8 2.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11zM8 7v4M8 5v.5',
  };
  return (
    <svg viewBox="0 0 16 16" className="size-[15px]" aria-hidden>
      <path d={paths[kind]} fill="none" stroke="currentColor" strokeWidth="1.3" />
    </svg>
  );
}

function MouseIcon() {
  return (
    <svg viewBox="0 0 12 16" className="h-3.5 w-2.5" aria-hidden>
      <rect x="1" y="1" width="10" height="14" rx="5" fill="none" stroke="currentColor" />
      <path d="M1.5 7V6a4.5 4.5 0 0 1 4.5-4.5V7z" fill="currentColor" />
    </svg>
  );
}

function Highlight({ code }: { code: string }) {
  // strings and a few keywords, enough to read it at a glance
  const parts = code.split(/('(?:[^'\\]|\\.)*')/g);
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith("'") ? (
          <span key={i} className="text-[var(--sn-code-string)]">
            {part}
          </span>
        ) : (
          part.split(/\b(class|def|from|import|return)\b/g).map((word, j) =>
            ['class', 'def', 'from', 'import', 'return'].includes(word) ? (
              <span key={`${i}-${j}`} className="text-[var(--sn-code-keyword)]">
                {word}
              </span>
            ) : (
              word
            ),
          )
        ),
      )}
    </>
  );
}

/*
 * The viewport: an isometric floor grid with the red X and green Y axes, and
 * the cubes the Add Cube button adds. Drawn at a fixed size from the center.
 */
const ISO = { w: 21, d: 12, h: 24 };
const SCENE = 640;
/** where Add Cube puts the next cubes (grid cells, the first is the default cube) */
const CUBE_SPOTS: Point[] = [
  { x: 0, y: 0 },
  { x: 2, y: 0 },
  { x: 0, y: 2 },
  { x: -2, y: 0 },
  { x: 0, y: -2 },
  { x: 2, y: -2 },
  { x: -2, y: 2 },
];
const MAX_CUBES = CUBE_SPOTS.length;

function cellCenter({ x, y }: Point): Point {
  // cell vectors a = (w, d) along X, b = (w, -d) along Y
  return {
    x: SCENE / 2 + (x + y) * ISO.w,
    y: SCENE / 2 + 20 + (x - y) * ISO.d,
  };
}

function SceneCube({ at, selected }: { at: Point; selected: boolean }) {
  const { w, d, h } = ISO;
  const { x, y } = cellCenter(at);
  const pts = (list: number[][]) => list.map(([px, py]) => `${px},${py}`).join(' ');
  return (
    <g className="sn-cube">
      <polygon
        points={pts([
          [x - w, y - h],
          [x, y + d - h],
          [x, y + d],
          [x - w, y],
        ])}
        style={{ fill: 'var(--sn-cube-left)' }}
      />
      <polygon
        points={pts([
          [x, y + d - h],
          [x + w, y - h],
          [x + w, y],
          [x, y + d],
        ])}
        style={{ fill: 'var(--sn-cube-right)' }}
      />
      <polygon
        points={pts([
          [x - w, y - h],
          [x, y - d - h],
          [x + w, y - h],
          [x, y + d - h],
        ])}
        style={{ fill: 'var(--sn-cube-top)' }}
      />
      <polygon
        points={pts([
          [x - w, y - h],
          [x, y - d - h],
          [x + w, y - h],
          [x + w, y],
          [x, y + d],
          [x - w, y],
        ])}
        fill="none"
        stroke={selected ? '#f2a60d' : 'rgba(0,0,0,0.35)'}
        strokeWidth={selected ? 1.6 : 0.8}
        strokeLinejoin="round"
      />
    </g>
  );
}

function Viewport({ cubes }: { cubes: number }) {
  const { w, d } = ISO;
  const o = { x: SCENE / 2, y: SCENE / 2 + 20 };
  const lines: string[] = [];
  const reach = 14;
  for (let i = -reach; i <= reach; i++) {
    // lines along X (direction a) and along Y (direction b), between cells
    const k = i + 0.5;
    lines.push(
      `M${o.x + k * w - reach * w} ${o.y - k * d - reach * d}L${o.x + k * w + reach * w} ${o.y - k * d + reach * d}`,
      `M${o.x + k * w - reach * w} ${o.y + k * d + reach * d}L${o.x + k * w + reach * w} ${o.y + k * d - reach * d}`,
    );
  }
  const spots = CUBE_SPOTS.slice(0, cubes).map((spot, i) => ({ spot, i }));
  // back to front
  spots.sort((p, q) => cellCenter(p.spot).y - cellCenter(q.spot).y);
  return (
    <svg
      viewBox={`0 0 ${SCENE} ${SCENE}`}
      width={SCENE}
      height={SCENE}
      className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
      aria-label={`3D viewport with ${cubes} ${cubes === 1 ? 'cube' : 'cubes'}`}
      role="img"
    >
      <path d={lines.join('')} style={{ stroke: 'var(--sn-floor)' }} strokeWidth="1" />
      <path
        d={`M${o.x - reach * w} ${o.y - reach * d}L${o.x + reach * w} ${o.y + reach * d}`}
        stroke="#b4555b"
        strokeWidth="1.4"
      />
      <path
        d={`M${o.x - reach * w} ${o.y + reach * d}L${o.x + reach * w} ${o.y - reach * d}`}
        stroke="#6f9440"
        strokeWidth="1.4"
      />
      {spots.map(({ spot, i }) => (
        <SceneCube key={i} at={spot} selected={i === cubes - 1} />
      ))}
    </svg>
  );
}

// -- the demo -----------------------------------------------------------------

type Phase = 'typing' | 'building' | 'done';

export function NodeDemo() {
  const [index, setIndex] = useState(0);
  const [values, setValues] = useState<Values[]>(() => SCENARIOS.map((s) => ({ ...s.defaults })));
  const [typed, setTyped] = useState('');
  const [built, setBuilt] = useState(0);
  const [phase, setPhase] = useState<Phase>('typing');
  const [view, setView] = useState<'result' | 'python'>('result');
  const [saves, setSaves] = useState(0);
  const [cubes, setCubes] = useState(1);
  const [info, setInfo] = useState('');
  const [fit, setFit] = useState({ scale: 1, x: 0, y: 0 });
  const [pan, setPan] = useState<Point>({ x: 0, y: 0 });
  const [moved, setMoved] = useState<Record<string, Point>>({});
  const canvas = useRef<HTMLDivElement>(null);
  const timers = useRef<number[]>([]);
  const drag = useRef<{ kind: 'pan' | 'node'; id?: string; start: Point; from: Point } | null>(
    null,
  );

  const scenario = SCENARIOS[index];
  const v = values[index];

  const run = useCallback((next: number) => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
    const target = SCENARIOS[next];
    setIndex(next);
    setSaves(0);
    setCubes(1);
    setInfo('');
    setPan({ x: 0, y: 0 });
    setMoved({});
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) {
      setTyped(target.prompt);
      setBuilt(target.nodes.length);
      setPhase('done');
      return;
    }
    setTyped('');
    setBuilt(0);
    setPhase('typing');
    const later = (ms: number, fn: () => void) => timers.current.push(window.setTimeout(fn, ms));
    const typing = 26;
    for (let i = 1; i <= target.prompt.length; i++) {
      later(i * typing, () => setTyped(target.prompt.slice(0, i)));
    }
    const start = target.prompt.length * typing + 250;
    later(start, () => setPhase('building'));
    target.nodes.forEach((_, i) => later(start + 120 + i * 260, () => setBuilt(i + 1)));
    later(start + 120 + target.nodes.length * 260 + 250, () => setPhase('done'));
  }, []);

  useEffect(() => {
    run(0);
    const pending = timers.current;
    return () => pending.forEach(clearTimeout);
  }, [run]);

  useLayoutEffect(() => {
    const el = canvas.current;
    if (!el) return;
    // fit the graph into the canvas, at most a bit larger than 1:1, centered
    const measure = (width: number, height: number) => {
      const scale = Math.min(1.15, width / WIDTH, height / HEIGHT);
      setFit({ scale, x: (width - WIDTH * scale) / 2, y: (height - HEIGHT * scale) / 2 });
    };
    const rect = el.getBoundingClientRect();
    measure(rect.width, rect.height);
    const observer = new ResizeObserver(([entry]) =>
      measure(entry.contentRect.width, entry.contentRect.height),
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // -- dragging: nodes by their header, the view by the background ----------

  const startDrag = (e: ReactPointerEvent, kind: 'pan' | 'node', id?: string) => {
    if (e.button !== 0 && !(kind === 'pan' && e.button === 1)) return;
    // touch only moves nodes, so the page still scrolls
    if (kind === 'pan' && e.pointerType === 'touch') return;
    e.stopPropagation();
    e.currentTarget.setPointerCapture(e.pointerId);
    const node = id ? scenario.nodes.find((n) => n.id === id) : undefined;
    drag.current = {
      kind,
      id,
      start: { x: e.clientX, y: e.clientY },
      from: kind === 'pan' ? pan : (moved[id!] ?? { x: node!.x, y: node!.y }),
    };
  };

  const moveDrag = (e: ReactPointerEvent) => {
    const d = drag.current;
    if (!d) return;
    const dx = e.clientX - d.start.x;
    const dy = e.clientY - d.start.y;
    if (d.kind === 'pan') {
      setPan({ x: d.from.x + dx, y: d.from.y + dy });
    } else {
      setMoved((all) => ({
        ...all,
        [d.id!]: { x: d.from.x + dx / fit.scale, y: d.from.y + dy / fit.scale },
      }));
    }
  };

  const endDrag = () => {
    drag.current = null;
  };

  const dragHandlers = { onPointerMove: moveDrag, onPointerUp: endDrag, onPointerCancel: endDrag };

  const visible = new Set(scenario.nodes.slice(0, built).map((n) => n.id));
  const linkedInputs = new Set(scenario.links.map(([, , to, input]) => `${to}:${input}`));
  const byId = Object.fromEntries(scenario.nodes.map((n) => [n.id, n]));
  const at = (node: NodeDef) => moved[node.id] ?? { x: node.x, y: node.y };
  const setValue = (key: string, value: string) =>
    setValues((all) => all.map((vals, i) => (i === index ? { ...vals, [key]: value } : vals)));

  const addCube = () => {
    setCubes((n) => Math.min(MAX_CUBES, n + 1));
    setInfo(cubes >= MAX_CUBES ? 'No room for more cubes' : 'Added Cube');
  };

  const status =
    info ||
    (phase === 'done'
      ? `Added ${scenario.nodes.length} nodes and ${scenario.links.length} ${scenario.links.length === 1 ? 'link' : 'links'}`
      : phase === 'building'
        ? 'Adding nodes…'
        : 'Thinking…');
  const code = scenario.code(v);
  const resultName = scenario.result === 'log' ? 'Info' : '3D Viewport';

  return (
    <div className="not-prose">
      <div className="mb-6 flex justify-center">
        <div className="inline-flex max-w-full gap-1 overflow-x-auto rounded-full bg-black/[0.05] p-1 text-[13px] dark:bg-white/[0.06]">
          {SCENARIOS.map((s, i) => (
            <button
              key={s.prompt}
              type="button"
              onClick={() => run(i)}
              aria-pressed={i === index}
              className="shrink-0 rounded-full px-3.5 py-1.5 text-fd-muted-foreground transition-colors hover:text-fd-foreground focus-visible:outline-2 focus-visible:outline-fd-ring aria-pressed:bg-white aria-pressed:text-fd-foreground aria-pressed:shadow-sm dark:aria-pressed:bg-white/[0.12]"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* the Blender window */}
      <div className="sn-window overflow-hidden rounded-[9px] bg-[var(--sn-gap)] text-[12px] text-[var(--sn-text)] shadow-[0_0_0_1px_rgba(0,0,0,0.08)] select-none dark:shadow-[0_0_0_1px_rgba(255,255,255,0.08)]">
        <div className="grid gap-[3px] px-[3px] pt-[3px] md:grid-cols-[minmax(0,1.65fr)_minmax(0,1fr)]">
          {/* node editor */}
          <div className="flex h-[400px] flex-col overflow-hidden rounded-[6px] md:h-[540px]">
            <AreaHeader>
              <span
                className="grid h-[20px] w-[26px] place-items-center text-[var(--sn-text)]"
                aria-hidden
              >
                <EditorIcon kind="node" />
              </span>
              <Menus items={['View', 'Select', 'Add', 'Node']} />
              <span className="ml-auto rounded-[4px] bg-[var(--sn-widget)] px-2.5 py-0.5 text-[var(--sn-strong)]">
                Main
              </span>
            </AreaHeader>
            <div
              ref={canvas}
              className="sn-grid relative flex-1 cursor-grab overflow-hidden active:cursor-grabbing"
              style={{ backgroundPosition: `${pan.x}px ${pan.y}px` }}
              onPointerDown={(e) => startDrag(e, 'pan')}
              {...dragHandlers}
            >
              <div
                className="absolute top-0 left-0 origin-top-left"
                style={{
                  width: WIDTH,
                  height: HEIGHT,
                  transform: `translate(${fit.x + pan.x}px, ${fit.y + pan.y}px) scale(${fit.scale})`,
                }}
              >
                <svg
                  className="absolute inset-0 overflow-visible"
                  width={WIDTH}
                  height={HEIGHT}
                  aria-hidden
                >
                  {scenario.links.map(([from, out, to, input]) => {
                    if (!visible.has(from) || !visible.has(to)) return null;
                    const a = socketPoint(byId[from], at(byId[from]), out, 'out');
                    const b = socketPoint(byId[to], at(byId[to]), input, 'in');
                    const color = SOCKET[byId[from].rows.find((r) => r.id === out)!.kind];
                    const d = linkPath(a, b);
                    // a dark outline under the colored link, like Blender draws them
                    return (
                      <g key={`${index}-${from}-${out}-${to}-${input}`} className="sn-link">
                        <path d={d} fill="none" style={{ stroke: 'var(--sn-link-outline)' }} strokeWidth={4} />
                        <path d={d} fill="none" stroke={color} strokeWidth={2} />
                      </g>
                    );
                  })}
                </svg>
                {scenario.nodes.map((node) => {
                  if (!visible.has(node.id)) return null;
                  const pos = at(node);
                  return (
                    <div
                      key={`${index}-${node.id}`}
                      className="sn-node absolute rounded-[6px] bg-[var(--sn-node)] shadow-[0_4px_14px_rgba(0,0,0,0.18)] ring-1 ring-black/5 dark:shadow-[0_6px_16px_rgba(0,0,0,0.35)] dark:ring-0"
                      style={{ left: pos.x, top: pos.y, width: node.w }}
                    >
                      <div
                        className="flex cursor-move touch-none items-center gap-1.5 rounded-t-[6px] px-2 text-[12px] text-white"
                        style={{ height: HEADER, background: 'var(--sn-node-header)' }}
                        onPointerDown={(e) => startDrag(e, 'node', node.id)}
                        {...dragHandlers}
                      >
                        <Chevron />
                        {node.title}
                      </div>
                      <div
                        className="cursor-default py-1"
                        onPointerDown={(e) => e.stopPropagation()}
                      >
                        {node.rows.map((row) => {
                          const linked =
                            row.side === 'in' && linkedInputs.has(`${node.id}:${row.id}`);
                          return (
                            <div
                              key={`${row.side}-${row.id}`}
                              className={`relative flex items-center gap-2 px-2.5 text-[12px] ${row.side === 'out' ? 'justify-end' : ''}`}
                              style={{ height: ROW }}
                            >
                              <SocketDot kind={row.kind} side={row.side} />
                              {row.field && !linked ? (
                                <label className="flex min-w-0 flex-1 items-center gap-1.5">
                                  <span className="shrink-0 text-[var(--sn-dim)]">{row.label}</span>
                                  <input
                                    value={v[row.field]}
                                    onChange={(e) => setValue(row.field!, e.target.value)}
                                    spellCheck={false}
                                    className="h-[19px] min-w-0 flex-1 rounded-[4px] bg-[var(--sn-field)] px-1.5 ring-1 ring-black/10 dark:ring-0 text-[var(--sn-strong)] outline-none select-text focus-visible:ring-1 focus-visible:ring-[#f2a60d]"
                                  />
                                </label>
                              ) : row.fixed ? (
                                <span className="flex min-w-0 flex-1 items-center gap-1.5">
                                  <span className="shrink-0 text-[var(--sn-dim)]">{row.label}</span>
                                  <span className="h-[19px] min-w-0 flex-1 truncate rounded-[4px] bg-[var(--sn-field)] px-1.5 ring-1 ring-black/10 dark:ring-0 leading-[19px] text-[var(--sn-strong)]">
                                    {row.fixed}
                                  </span>
                                </span>
                              ) : (
                                <span className="text-[var(--sn-dim)]">{row.label}</span>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* the request to the assistant, floating in the editor */}
              <div
                className="pointer-events-none absolute top-3 left-1/2 flex w-max max-w-[calc(100%-24px)] -translate-x-1/2 items-center gap-2 rounded-full border border-[var(--sn-border)] bg-[var(--sn-pill)] px-3.5 py-1.5 text-[12px] text-[var(--sn-strong)] shadow-[0_8px_24px_rgba(0,0,0,0.35)]"
                aria-live="polite"
              >
                <span aria-hidden className="text-[#f2a60d]">
                  ✦
                </span>
                <span className="truncate">
                  {typed}
                  {phase === 'typing' && <span className="sn-caret" aria-hidden />}
                </span>
              </div>
            </div>
          </div>

          {/* 3D viewport / Info log, or the Text Editor with the Python */}
          <div className="flex h-[320px] flex-col overflow-hidden rounded-[6px] md:h-[540px]">
            <AreaHeader>
              <div className="flex rounded-[4px] bg-[var(--sn-widget)] p-0.5" role="tablist">
                {(['result', 'python'] as const).map((tab) => (
                  <button
                    key={tab}
                    type="button"
                    role="tab"
                    aria-selected={view === tab}
                    aria-label={
                      tab === 'python' ? 'Text Editor with the generated Python' : resultName
                    }
                    title={tab === 'python' ? 'Text Editor' : resultName}
                    onClick={() => setView(tab)}
                    className="grid h-[20px] w-[26px] place-items-center rounded-[3px] text-[var(--sn-dim)] hover:text-[var(--sn-strong)] focus-visible:outline-1 focus-visible:outline-[#f2a60d] aria-selected:bg-[var(--sn-widget-active)] aria-selected:text-[var(--sn-strong)]"
                  >
                    <EditorIcon
                      kind={
                        tab === 'python' ? 'text' : scenario.result === 'log' ? 'info' : 'view3d'
                      }
                    />
                  </button>
                ))}
              </div>
              {view === 'python' ? (
                <span className="ml-2 text-[var(--sn-dim)]">main.py</span>
              ) : scenario.result === 'log' ? (
                <button
                  type="button"
                  onClick={() => setSaves((n) => n + 1)}
                  className="ml-auto rounded-[4px] bg-[var(--sn-button)] px-2.5 py-0.5 ring-1 ring-black/10 dark:ring-0 text-[var(--sn-strong)] hover:bg-[var(--sn-button-hover)] focus-visible:outline-1 focus-visible:outline-[#f2a60d]"
                >
                  Save file
                </button>
              ) : (
                <Menus items={['View', 'Object']} />
              )}
            </AreaHeader>

            <div
              className={`relative flex min-h-0 flex-1 transition-opacity duration-300 ${phase === 'done' ? 'opacity-100' : 'opacity-40'}`}
              role="tabpanel"
            >
              {view === 'python' ? (
                <pre className="flex min-w-0 flex-1 overflow-auto bg-[var(--sn-field)] py-2 font-[family-name:var(--font-code)] text-[11.5px] leading-[18px] text-[var(--sn-text)] select-text">
                  <span aria-hidden className="shrink-0 px-2.5 text-right text-[var(--sn-faint)]">
                    {code.split('\n').map((_, i) => (
                      <span key={i} className="block">
                        {i + 1}
                      </span>
                    ))}
                  </span>
                  <code className="pr-3">
                    <Highlight code={code} />
                  </code>
                </pre>
              ) : scenario.result === 'log' ? (
                <div
                  className="flex-1 overflow-auto bg-[var(--sn-field)] p-2.5 font-[family-name:var(--font-code)] text-[11.5px] leading-5 text-[var(--sn-text)]"
                  aria-live="polite"
                >
                  {saves === 0 ? (
                    <span className="text-[var(--sn-faint)]">
                      Click Save file to run the event.
                    </span>
                  ) : (
                    Array.from({ length: Math.min(saves, 12) }, (_, i) => (
                      <div key={i}>{v.message}</div>
                    ))
                  )}
                </div>
              ) : (
                <div className="flex flex-1 bg-[var(--sn-viewport)]">
                  <div className="relative flex-1 overflow-hidden">
                    <Viewport cubes={cubes} />
                  </div>
                  <div className="flex w-[clamp(150px,52%,210px)] shrink-0 bg-[var(--sn-region)]">
                    <div className="flex-1 p-1.5">{scenario.panel?.(v, { addCube, objects: cubes + 2 })}</div>
                    <div
                      className="flex w-[20px] flex-col items-center gap-[2px] pt-1.5"
                      aria-hidden
                    >
                      {['Item', 'Tool', 'Scripting Nodes'].map((tab) => (
                        <span
                          key={tab}
                          className={`rounded-l-[4px] px-[3px] py-2 text-[10px] [writing-mode:vertical-rl] ${tab === 'Scripting Nodes' ? 'bg-[var(--sn-panel)] text-[var(--sn-strong)]' : 'text-[var(--sn-dim)]'}`}
                        >
                          {tab}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* status bar */}
        <div className="flex h-[26px] items-center gap-4 px-3 text-[11px] text-[var(--sn-dim)]">
          <span className="hidden items-center gap-1.5 sm:flex">
            <MouseIcon /> Move node
          </span>
          <span className="hidden items-center gap-1.5 sm:flex">
            <MouseIcon /> Pan view
          </span>
          <span className="ml-auto truncate">{status}</span>
        </div>
      </div>
    </div>
  );
}
