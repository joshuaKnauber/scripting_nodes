'use client';

import { useCallback, useEffect, useLayoutEffect, useRef, useState, type ReactNode } from 'react';

/*
 * A tiny node editor in Blender's colors: pick a request, the graph builds
 * itself, the result shows the panel (or console) it makes and the Python it
 * generates. Fields in the nodes are editable and update both live.
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

interface Scenario {
  /** tab label */
  label: string;
  prompt: string;
  nodes: NodeDef[];
  links: Link[];
  defaults: Values;
  result: (v: Values, extra: ResultExtras) => ReactNode;
  code: (v: Values) => string;
}

interface ResultExtras {
  saves: number;
  save: () => void;
}

const snake = (text: string, fallback: string) =>
  text.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '') || fallback;

const py = (text: string) => `'${text.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}'`;

const SCENARIOS: Scenario[] = [
  {
    label: 'A button',
    prompt: 'Add a button to the sidebar that adds a cube',
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
    result: (v) => (
      <BlenderPanel title={v.panel}>
        <BlenderButton>{v.button || 'Add Cube'}</BlenderButton>
      </BlenderPanel>
    ),
    code: (v) => `class MY_ADDON_PT_${snake(v.panel, 'panel')}(bpy.types.Panel):
    bl_label = ${py(v.panel)}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        self.layout.operator('mesh.primitive_cube_add', text=${py(v.button)})`,
  },
  {
    label: 'A live label',
    prompt: 'Show how many objects are selected',
    nodes: [
      {
        id: 'panel',
        title: 'Panel',
        x: 15,
        y: 30,
        w: 155,
        rows: [
          { id: 'body', label: 'Interface', kind: 'interface', side: 'out' },
          { id: 'label', label: 'Label', kind: 'string', side: 'in', field: 'panel' },
        ],
      },
      {
        id: 'selected',
        title: 'Selected Objects',
        x: 10,
        y: 205,
        w: 130,
        rows: [{ id: 'objects', label: 'Objects', kind: 'data', side: 'out' }],
      },
      {
        id: 'length',
        title: 'Length',
        x: 175,
        y: 215,
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
        y: 190,
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
        y: 34,
        w: 140,
        rows: [
          { id: 'next', label: 'Interface', kind: 'interface', side: 'out' },
          { id: 'in', label: 'Interface', kind: 'interface', side: 'in' },
          { id: 'text', label: 'Text', kind: 'string', side: 'in' },
        ],
      },
    ],
    links: [
      ['panel', 'body', 'label', 'in'],
      ['selected', 'objects', 'length', 'list'],
      ['length', 'length', 'join', 'b'],
      ['join', 'text', 'label', 'text'],
    ],
    defaults: { panel: 'Selection', prefix: 'Selected: ' },
    result: (v) => (
      <BlenderPanel title={v.panel}>
        <p className="px-1 py-1.5">{v.prefix}3</p>
      </BlenderPanel>
    ),
    code: (v) => `class MY_ADDON_PT_${snake(v.panel, 'panel')}(bpy.types.Panel):
    bl_label = ${py(v.panel)}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        count = len(context.selected_objects)
        self.layout.label(text=${py(v.prefix)} + str(count))`,
  },
  {
    label: 'An event',
    prompt: 'Print a message every time the file is saved',
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
    result: (v, { saves, save }) => (
      <div className="flex h-full flex-col gap-3">
        <button
          type="button"
          onClick={save}
          className="self-start rounded-[5px] bg-[#545454] px-3 py-1 text-[#e6e6e6] hover:bg-[#656565] focus-visible:outline-2 focus-visible:outline-[#f2a60d]"
        >
          Save file
        </button>
        <div
          className="min-h-24 flex-1 rounded-[5px] bg-[#181818] p-2.5 font-[family-name:var(--font-code)] text-[12px] leading-5 text-[#cfcfcf]"
          aria-live="polite"
        >
          {saves === 0 ? (
            <span className="text-[#7a7a7a]">Click Save file to run it.</span>
          ) : (
            Array.from({ length: Math.min(saves, 5) }, (_, i) => <div key={i}>{v.message}</div>)
          )}
        </div>
      </div>
    ),
    code: (v) => `from bpy.app.handlers import persistent


@persistent
def on_save_post(*args):
    print(${py(v.message)})


def register():
    bpy.app.handlers.save_post.append(on_save_post)`,
  },
];

// -- geometry ----------------------------------------------------------------

const WIDTH = 620;
const HEIGHT = 330;
const HEADER = 26;
const ROW = 24;

function socketPoint(node: NodeDef, rowId: string, side: 'in' | 'out') {
  const index = node.rows.findIndex((r) => r.id === rowId && r.side === side);
  return {
    x: side === 'out' ? node.x + node.w : node.x,
    y: node.y + HEADER + 4 + index * ROW + ROW / 2,
  };
}

function linkPath(a: { x: number; y: number }, b: { x: number; y: number }) {
  const dx = Math.max(40, Math.abs(b.x - a.x) / 2);
  return `M ${a.x} ${a.y} C ${a.x + dx} ${a.y}, ${b.x - dx} ${b.y}, ${b.x} ${b.y}`;
}

// -- pieces of Blender UI ----------------------------------------------------

function BlenderPanel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-[6px] bg-[#303030] p-2 text-[13px] text-[#e6e6e6]">
      <div className="flex items-center gap-1.5 px-1 pb-2">
        <span aria-hidden className="text-[10px] text-[#9a9a9a]">
          ▼
        </span>
        {title || 'Panel'}
      </div>
      {children}
    </div>
  );
}

function BlenderButton({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-[5px] bg-[#545454] py-1 text-center text-[#e6e6e6]">{children}</div>
  );
}

function SocketDot({ kind, side }: { kind: Kind; side: 'in' | 'out' }) {
  const diamond = kind === 'flow' || kind === 'logic' || kind === 'interface';
  return (
    <span
      aria-hidden
      className="absolute top-1/2 size-[10px] -translate-y-1/2 border border-black/60"
      style={{
        background: SOCKET[kind],
        [side === 'in' ? 'left' : 'right']: -5,
        borderRadius: diamond ? 1 : '50%',
        transform: `translateY(-50%)${diamond ? ' rotate(45deg) scale(0.85)' : ''}`,
      }}
    />
  );
}

function Highlight({ code }: { code: string }) {
  // strings and a few keywords, enough to read it at a glance
  const parts = code.split(/('(?:[^'\\]|\\.)*')/g);
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith("'") ? (
          <span key={i} className="text-[#9ecbff]">
            {part}
          </span>
        ) : (
          part.split(/\b(class|def|from|import|return)\b/g).map((word, j) =>
            ['class', 'def', 'from', 'import', 'return'].includes(word) ? (
              <span key={`${i}-${j}`} className="text-[#f2a60d]">
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

// -- the demo -----------------------------------------------------------------

type Phase = 'typing' | 'building' | 'done';

export function NodeDemo() {
  const [index, setIndex] = useState(0);
  const [values, setValues] = useState<Values[]>(() => SCENARIOS.map((s) => ({ ...s.defaults })));
  const [typed, setTyped] = useState('');
  const [built, setBuilt] = useState(0);
  const [phase, setPhase] = useState<Phase>('typing');
  const [view, setView] = useState<'blender' | 'python'>('blender');
  const [saves, setSaves] = useState(0);
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState(0);
  const frame = useRef<HTMLDivElement>(null);
  const timers = useRef<number[]>([]);

  const scenario = SCENARIOS[index];
  const v = values[index];

  const run = useCallback((next: number) => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
    const target = SCENARIOS[next];
    setIndex(next);
    setSaves(0);
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
    const el = frame.current;
    if (!el) return;
    // fit the graph's width, up to a bit larger than 1:1, centered
    const fit = (width: number) => {
      const next = Math.min(1.2, width / WIDTH);
      setScale(next);
      setOffset(Math.max(0, (width - WIDTH * next) / 2));
    };
    fit(el.getBoundingClientRect().width);
    const observer = new ResizeObserver(([entry]) => fit(entry.contentRect.width));
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const visible = new Set(scenario.nodes.slice(0, built).map((n) => n.id));
  const linkedInputs = new Set(scenario.links.map(([, , to, input]) => `${to}:${input}`));
  const byId = Object.fromEntries(scenario.nodes.map((n) => [n.id, n]));
  const setValue = (key: string, value: string) =>
    setValues((all) => all.map((vals, i) => (i === index ? { ...vals, [key]: value } : vals)));

  const status =
    phase === 'typing'
      ? ''
      : phase === 'building'
        ? 'Adding nodes…'
        : `Added ${scenario.nodes.length} nodes and ${scenario.links.length} ${scenario.links.length === 1 ? 'link' : 'links'}`;

  return (
    <div className="not-prose">
      <div className="mb-6 flex justify-center">
        <div className="inline-flex max-w-full gap-1 overflow-x-auto rounded-full bg-fd-muted p-1 text-[13px]">
          {SCENARIOS.map((s, i) => (
            <button
              key={s.prompt}
              type="button"
              onClick={() => run(i)}
              aria-pressed={i === index}
              className="shrink-0 rounded-full px-3.5 py-1.5 text-fd-muted-foreground transition-colors hover:text-fd-foreground focus-visible:outline-2 focus-visible:outline-fd-ring aria-pressed:bg-fd-background aria-pressed:text-fd-foreground aria-pressed:shadow-sm"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-[#2c2c2c] bg-[#1d1d1d] text-[13px] text-[#d6d6d6] shadow-[0_40px_100px_-40px_rgba(0,0,0,0.45),0_12px_30px_-20px_rgba(0,0,0,0.3)]">
        <div className="flex items-center gap-3 border-b border-[#2c2c2c] bg-[#242424] px-4 py-2.5">
          <span aria-hidden className="text-[#f2a60d]">
            ✦
          </span>
          <p className="min-w-0 flex-1 truncate" aria-live="polite">
            {typed}
            {phase === 'typing' && <span className="sn-caret" aria-hidden />}
          </p>
          <span className="hidden shrink-0 text-[12px] text-[#8a8a8a] sm:block">{status}</span>
        </div>

        <div className="grid md:grid-cols-[minmax(0,1fr)_300px]">
          <div
            ref={frame}
            className="sn-grid relative border-b border-[#2c2c2c] md:border-r md:border-b-0"
            style={{ height: HEIGHT * scale }}
          >
            <div
              className="absolute top-0 left-0 origin-top-left"
              style={{
                width: WIDTH,
                height: HEIGHT,
                transform: `translateX(${offset}px) scale(${scale})`,
              }}
            >
              <svg className="absolute inset-0" width={WIDTH} height={HEIGHT} aria-hidden>
                {scenario.links.map(([from, out, to, input]) => {
                  if (!visible.has(from) || !visible.has(to)) return null;
                  const a = socketPoint(byId[from], out, 'out');
                  const b = socketPoint(byId[to], input, 'in');
                  const color = SOCKET[byId[from].rows.find((r) => r.id === out)!.kind];
                  return (
                    <path
                      key={`${index}-${from}-${out}-${to}-${input}`}
                      d={linkPath(a, b)}
                      fill="none"
                      stroke={color}
                      strokeWidth={2}
                      className="sn-link"
                    />
                  );
                })}
              </svg>
              {scenario.nodes.map((node) =>
                visible.has(node.id) ? (
                  <div
                    key={`${index}-${node.id}`}
                    className="sn-node absolute rounded-[6px] bg-[#303030] shadow-[0_6px_16px_rgba(0,0,0,0.35)]"
                    style={{ left: node.x, top: node.y, width: node.w }}
                  >
                    <div
                      className="flex items-center gap-1.5 rounded-t-[6px] px-2 text-[12px] text-[#f0f0f0]"
                      style={{ height: HEADER, background: '#7a3542' }}
                    >
                      <span aria-hidden className="text-[9px] text-[#d9b3ba]">
                        ▼
                      </span>
                      {node.title}
                    </div>
                    <div className="py-1">
                      {node.rows.map((row) => {
                        const linked = row.side === 'in' && linkedInputs.has(`${node.id}:${row.id}`);
                        return (
                          <div
                            key={`${row.side}-${row.id}`}
                            className={`relative flex items-center gap-2 px-2.5 text-[12px] ${row.side === 'out' ? 'justify-end' : ''}`}
                            style={{ height: ROW }}
                          >
                            <SocketDot kind={row.kind} side={row.side} />
                            {row.field && !linked ? (
                              <label className="flex min-w-0 flex-1 items-center gap-1.5">
                                <span className="shrink-0 text-[#b8b8b8]">{row.label}</span>
                                <input
                                  value={v[row.field]}
                                  onChange={(e) => setValue(row.field!, e.target.value)}
                                  spellCheck={false}
                                  className="h-[19px] min-w-0 flex-1 rounded-[4px] bg-[#1d1d1d] px-1.5 text-[#ececec] outline-none focus-visible:ring-1 focus-visible:ring-[#f2a60d]"
                                />
                              </label>
                            ) : row.fixed ? (
                              <span className="flex min-w-0 flex-1 items-center gap-1.5">
                                <span className="shrink-0 text-[#b8b8b8]">{row.label}</span>
                                <span className="h-[19px] min-w-0 flex-1 truncate rounded-[4px] bg-[#1d1d1d] px-1.5 leading-[19px] text-[#ececec]">
                                  {row.fixed}
                                </span>
                              </span>
                            ) : (
                              <span className="text-[#b8b8b8]">{row.label}</span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : null,
              )}
            </div>
          </div>

          <div className="flex min-h-[180px] flex-col md:min-h-[260px]">
            <div className="flex gap-1 border-b border-[#2c2c2c] px-3 pt-2" role="tablist">
              {(['blender', 'python'] as const).map((tab) => (
                <button
                  key={tab}
                  type="button"
                  role="tab"
                  aria-selected={view === tab}
                  onClick={() => setView(tab)}
                  className="-mb-px border-b-2 border-transparent px-2 pb-2 text-[12px] text-[#8a8a8a] hover:text-[#d6d6d6] focus-visible:outline-2 focus-visible:outline-[#f2a60d] aria-selected:border-[#f2a60d] aria-selected:text-[#ececec]"
                >
                  {tab === 'blender' ? 'In Blender' : 'Generated Python'}
                </button>
              ))}
            </div>
            <div
              className={`flex-1 p-3 transition-opacity duration-300 ${phase === 'done' ? 'opacity-100' : 'opacity-0'}`}
              role="tabpanel"
            >
              {view === 'blender' ? (
                scenario.result(v, { saves, save: () => setSaves((n) => n + 1) })
              ) : (
                <pre className="overflow-x-auto font-[family-name:var(--font-code)] text-[11.5px] leading-[18px] text-[#d4d4d4]">
                  <Highlight code={scenario.code(v)} />
                </pre>
              )}
            </div>
          </div>
        </div>
      </div>
      <p className="mt-4 text-center text-[13px] text-fd-muted-foreground">
        Type in the nodes' text fields. The panel and the code update as you type.
      </p>
    </div>
  );
}
