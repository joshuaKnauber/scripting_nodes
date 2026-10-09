'use client';

import { RotateCcw } from 'lucide-react';
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';

/*
 * An assistant building a graph over the MCP server: the session on the left
 * (request, tool calls, reply), the node canvas on the right changing with
 * each tool call. Plays when scrolled into view, can be replayed.
 */

const PROMPT = 'Add a sidebar panel with a button that adds a cube';

// [tool, arguments, what it changes in the graph]
const CALLS: [string, string, Partial<Graph>][] = [
  ['list_node_types', 'button', {}],
  ['create_node', 'Panel', { panel: true }],
  ['create_node', 'Button', { button: true }],
  ['set_node_prop', 'Button.operator = Add Cube', { operator: true }],
  ['connect_sockets', 'Panel.Interface to Button.Interface', { link: true }],
  ['get_tree_code', 'Main', {}],
];

const REPLY =
  'Added a My Tools panel with an Add Cube button to the Main tree. It is in the 3D viewport sidebar now.';

interface Graph {
  panel: boolean;
  button: boolean;
  operator: boolean;
  link: boolean;
}

const EMPTY: Graph = { panel: false, button: false, operator: false, link: false };
const FULL: Graph = { panel: true, button: true, operator: true, link: true };

const AMBER = '#f2a60d';
const PINK = '#d36f9e';

type Point = { x: number; y: number };

function Spinner() {
  return (
    <span
      aria-hidden
      className="inline-block size-3 animate-spin rounded-full border-[1.5px] border-[#6e6e6e] border-t-transparent"
    />
  );
}

function Check() {
  return (
    <svg viewBox="0 0 12 12" className="size-3 text-[#3fc1a3]" aria-hidden>
      <path d="M2 6.5 4.8 9 10 3" fill="none" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}

function Node({
  title,
  color,
  rows,
  refFn,
  className,
}: {
  title: string;
  color: string;
  rows: [string, string][];
  refFn: (el: HTMLDivElement | null) => void;
  className: string;
}) {
  return (
    <div
      ref={refFn}
      className={`sn-node absolute w-[160px] rounded-xl md:w-[204px] border bg-white text-[13px] dark:bg-fd-card ${className}`}
    >
      <div
        className="flex h-9 items-center rounded-t-xl border-b px-3.5 font-medium"
        style={{ background: `color-mix(in srgb, ${color} var(--sn-tint), transparent)` }}
      >
        {title}
      </div>
      <div className="space-y-1.5 px-3.5 py-3">
        {rows.map(([label, value]) => (
          <div key={label} className="sn-node flex items-center gap-2">
            <span className="shrink-0 text-fd-muted-foreground">{label}</span>
            <span className="min-w-0 flex-1 truncate rounded-md bg-fd-muted px-2 py-0.5">
              {value}
            </span>
          </div>
        ))}
      </div>
      <span
        aria-hidden
        className="absolute top-[18px] -left-[5px] size-2.5 -translate-y-1/2 rounded-full ring-2 ring-fd-background"
        style={{ background: color }}
      />
      <span
        aria-hidden
        className="absolute top-[18px] -right-[5px] size-2.5 -translate-y-1/2 rounded-full ring-2 ring-fd-background"
        style={{ background: color }}
      />
    </div>
  );
}

export function AssistantDemo() {
  const root = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLDivElement>(null);
  const nodes = useRef<Record<string, HTMLDivElement | null>>({});
  const timers = useRef<number[]>([]);
  const [typed, setTyped] = useState('');
  // how many calls have started, and how many finished
  const [started, setStarted] = useState(0);
  const [done, setDone] = useState(0);
  const [reply, setReply] = useState(false);
  const [graph, setGraph] = useState<Graph>(EMPTY);
  const [link, setLink] = useState<{ from: Point; to: Point } | null>(null);
  const [played, setPlayed] = useState(false);

  const play = useCallback(() => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
    setPlayed(true);
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setTyped(PROMPT);
      setStarted(CALLS.length);
      setDone(CALLS.length);
      setGraph(FULL);
      setReply(true);
      return;
    }
    setTyped('');
    setStarted(0);
    setDone(0);
    setGraph(EMPTY);
    setReply(false);
    const later = (ms: number, fn: () => void) => timers.current.push(window.setTimeout(fn, ms));
    const typing = 28;
    for (let i = 1; i <= PROMPT.length; i++) later(i * typing, () => setTyped(PROMPT.slice(0, i)));
    let t = PROMPT.length * typing + 450;
    CALLS.forEach(([, , change], i) => {
      later(t, () => setStarted(i + 1));
      t += 520;
      later(t, () => {
        setDone(i + 1);
        setGraph((g) => ({ ...g, ...change }));
      });
      t += 160;
    });
    later(t + 300, () => setReply(true));
  }, []);

  // play once when it comes into view
  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          play();
          observer.disconnect();
        }
      },
      { threshold: 0.4 },
    );
    observer.observe(el);
    const pending = timers.current;
    return () => {
      observer.disconnect();
      pending.forEach(clearTimeout);
    };
  }, [play]);

  // the link between the two nodes, measured from where they are drawn
  useLayoutEffect(() => {
    const measure = () => {
      const box = canvas.current?.getBoundingClientRect();
      const a = nodes.current.panel?.getBoundingClientRect();
      const b = nodes.current.button?.getBoundingClientRect();
      if (!box || !a || !b || !graph.link) {
        setLink(null);
        return;
      }
      setLink({
        from: { x: a.right - box.left, y: a.top - box.top + 18 },
        to: { x: b.left - box.left, y: b.top - box.top + 18 },
      });
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, [graph]);

  const linkPath =
    link &&
    (() => {
      const dx = Math.max(40, (link.to.x - link.from.x) / 2);
      return `M ${link.from.x} ${link.from.y} C ${link.from.x + dx} ${link.from.y}, ${link.to.x - dx} ${link.to.y}, ${link.to.x} ${link.to.y}`;
    })();

  return (
    <div
      ref={root}
      className="mx-auto mt-14 grid max-w-[1000px] grid-cols-[minmax(0,1fr)] overflow-hidden rounded-2xl border bg-white md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] dark:bg-fd-card"
    >
      {/* the assistant session */}
      <div
        className="flex min-h-[380px] flex-col border-b bg-[#161616] p-5 md:border-r md:border-b-0 font-[family-name:var(--font-code)] text-[12.5px] leading-6 text-[#d4d4d4]"
        aria-live="polite"
      >
        <p className="flex gap-2.5 text-[#ececec]">
          <span aria-hidden className="text-[#f2a60d]">
            {'>'}
          </span>
          <span>
            {typed}
            {played && typed.length < PROMPT.length && <span className="sn-caret" aria-hidden />}
          </span>
        </p>
        <ul className="mt-4 space-y-1.5">
          {CALLS.slice(0, started).map(([tool, args], i) => (
            <li key={tool + args} className="sn-node flex items-center gap-2.5">
              <span className="grid w-3 place-items-center">
                {i < done ? <Check /> : <Spinner />}
              </span>
              <span className="text-[#ececec]">{tool}</span>
              <span className="truncate text-[#8a8a8a]">{args}</span>
            </li>
          ))}
        </ul>
        {reply && (
          <p className="sn-node mt-5 font-sans text-[14px] leading-6 text-[#ececec]">{REPLY}</p>
        )}
        <button
          type="button"
          onClick={play}
          className="mt-auto flex w-fit items-center gap-1.5 self-end pt-4 font-sans text-[12px] text-[#8a8a8a] transition-colors hover:text-[#ececec] focus-visible:outline-2 focus-visible:outline-[#f2a60d]"
        >
          <RotateCcw aria-hidden className="size-3.5" />
          Replay
        </button>
      </div>

      {/* the graph it builds */}
      <div
        ref={canvas}
        className="relative min-h-[300px] bg-[radial-gradient(var(--color-fd-border)_1px,transparent_1px)] [background-size:20px_20px]"
        role="img"
        aria-label={
          graph.link
            ? 'A Panel node connected to a Button node that runs Add Cube'
            : 'The node tree the assistant is building'
        }
      >
        <svg
          className="pointer-events-none absolute inset-0 size-full overflow-visible"
          aria-hidden
        >
          {linkPath && (
            <path
              d={linkPath}
              fill="none"
              stroke={AMBER}
              strokeWidth={2}
              strokeOpacity={0.7}
              className="sn-link-draw"
            />
          )}
        </svg>
        {graph.panel && (
          <Node
            title="Panel"
            color={AMBER}
            rows={[['Label', 'My Tools']]}
            refFn={(el) => {
              nodes.current.panel = el;
            }}
            className="top-[16%] left-[4%]"
          />
        )}
        {graph.button && (
          <Node
            title="Button"
            color={PINK}
            rows={[
              ...(graph.operator ? ([['Operator', 'Add Cube']] as [string, string][]) : []),
              ['Label', 'Add Cube'],
            ]}
            refFn={(el) => {
              nodes.current.button = el;
            }}
            className="right-[4%] bottom-[16%]"
          />
        )}
        {!graph.panel && (
          <p className="absolute inset-0 grid place-items-center text-[13px] text-fd-muted-foreground">
            Main
          </p>
        )}
      </div>
    </div>
  );
}
