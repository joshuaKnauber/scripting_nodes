'use client';

import {
  useCallback,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
} from 'react';

/*
 * "What you can build" as a small node graph: each feature is an abstract
 * node, linked into a plausible chain. Cards can be dragged by their header
 * (mouse or pen), the links follow. Below md it's a plain stack, no links.
 */

const FEATURES = [
  {
    id: 'ui',
    title: 'Panels and menus',
    text: 'Sidebar panels, menus and popups with buttons and fields.',
    color: '#f2a60d',
  },
  {
    id: 'ops',
    title: 'Operators',
    text: 'Actions people run from a button or the search, with undo.',
    color: '#d36f9e',
  },
  {
    id: 'props',
    title: 'Properties',
    text: 'Settings saved in the file or in the preferences.',
    color: '#6f9cff',
  },
  {
    id: 'events',
    title: 'Events',
    text: 'Run nodes when a file loads or saves, or the frame changes.',
    color: '#3fc1a3',
  },
  {
    id: 'functions',
    title: 'Functions',
    text: 'Turn part of a graph into one node you can reuse.',
    color: '#8b7cf0',
  },
  {
    id: 'python',
    title: 'Python',
    text: 'Run your own script when there is no node for the job.',
    color: '#a3a3a3',
  },
];

const LINKS: [string, string][] = [
  ['ui', 'ops'],
  ['ops', 'props'],
  ['events', 'ops'],
  ['events', 'functions'],
  ['functions', 'python'],
];

/** header height; sockets sit at its middle */
const HEADER = 44;

type Point = { x: number; y: number };
type Path = { key: string; d: string; color: string; from: Point; to: Point };

export function FeatureGraph() {
  const box = useRef<HTMLDivElement>(null);
  const nodes = useRef<Record<string, HTMLLIElement | null>>({});
  const [offsets, setOffsets] = useState<Record<string, Point>>({});
  const [paths, setPaths] = useState<Path[]>([]);
  const drag = useRef<{ id: string; start: Point; from: Point } | null>(null);

  const measure = useCallback(() => {
    const container = box.current;
    if (!container) return;
    // links only in the multi-column layout
    if (window.matchMedia('(max-width: 767px)').matches) {
      setPaths([]);
      return;
    }
    const origin = container.getBoundingClientRect();
    const rect = (id: string) => nodes.current[id]!.getBoundingClientRect();
    setPaths(
      LINKS.map(([a, b]) => {
        const ra = rect(a);
        const rb = rect(b);
        const from = { x: ra.right - origin.left, y: ra.top - origin.top + HEADER / 2 };
        const to = { x: rb.left - origin.left, y: rb.top - origin.top + HEADER / 2 };
        const dx = Math.max(48, Math.abs(to.x - from.x) / 2);
        return {
          key: `${a}-${b}`,
          d: `M ${from.x} ${from.y} C ${from.x + dx} ${from.y}, ${to.x - dx} ${to.y}, ${to.x} ${to.y}`,
          color: FEATURES.find((f) => f.id === a)!.color,
          from,
          to,
        };
      }),
    );
  }, []);

  useLayoutEffect(() => {
    measure();
  }, [measure, offsets]);

  useLayoutEffect(() => {
    const container = box.current;
    if (!container) return;
    const observer = new ResizeObserver(() => {
      setOffsets({}); // a new layout: back to the grid
      measure();
    });
    observer.observe(container);
    return () => observer.disconnect();
  }, [measure]);

  const start = (e: ReactPointerEvent, id: string) => {
    if (e.pointerType === 'touch' || e.button !== 0) return;
    if (window.matchMedia('(max-width: 767px)').matches) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    drag.current = {
      id,
      start: { x: e.clientX, y: e.clientY },
      from: offsets[id] ?? { x: 0, y: 0 },
    };
  };

  const move = (e: ReactPointerEvent) => {
    const d = drag.current;
    if (!d) return;
    setOffsets((all) => ({
      ...all,
      [d.id]: { x: d.from.x + e.clientX - d.start.x, y: d.from.y + e.clientY - d.start.y },
    }));
  };

  const end = () => {
    drag.current = null;
  };

  return (
    <div ref={box} className="relative mx-auto mt-14 max-w-[1000px]">
      <svg className="pointer-events-none absolute inset-0 size-full overflow-visible" aria-hidden>
        {paths.map((p) => (
          <path
            key={p.key}
            d={p.d}
            fill="none"
            stroke={p.color}
            strokeWidth={2}
            strokeOpacity={0.55}
          />
        ))}
      </svg>
      <ul className="grid gap-4 md:grid-cols-3 md:gap-x-20 md:gap-y-14">
        {FEATURES.map((f, i) => {
          const offset = offsets[f.id] ?? { x: 0, y: 0 };
          return (
            <li
              key={f.id}
              ref={(el) => {
                nodes.current[f.id] = el;
              }}
              // the middle column sits lower, so it reads as a graph
              className={`relative rounded-xl border bg-white dark:bg-fd-card [translate:var(--dx)_calc(var(--dy)+var(--stagger,0px))] ${i % 3 === 1 ? 'md:[--stagger:40px]' : ''}`}
              style={{ '--dx': `${offset.x}px`, '--dy': `${offset.y}px` } as CSSProperties}
            >
              <div
                className="flex cursor-default items-center gap-2.5 rounded-t-xl border-b px-4 select-none md:cursor-grab md:active:cursor-grabbing md:touch-none"
                style={{
                  height: HEADER,
                  background: `color-mix(in srgb, ${f.color} var(--sn-tint), transparent)`,
                }}
                onPointerDown={(e) => start(e, f.id)}
                onPointerMove={move}
                onPointerUp={end}
                onPointerCancel={end}
              >
                <span className="text-[15px] font-medium">{f.title}</span>
              </div>
              <p className="px-4 py-3.5 text-[15px] leading-6 text-fd-muted-foreground">{f.text}</p>
              {/* sockets */}
              <span
                aria-hidden
                className="absolute top-[22px] -left-[5px] hidden size-2.5 -translate-y-1/2 rounded-full ring-2 ring-fd-background md:block"
                style={{ background: f.color }}
              />
              <span
                aria-hidden
                className="absolute top-[22px] -right-[5px] hidden size-2.5 -translate-y-1/2 rounded-full ring-2 ring-fd-background md:block"
                style={{ background: f.color }}
              />
            </li>
          );
        })}
      </ul>
    </div>
  );
}
