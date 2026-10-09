import Link from 'next/link';
import { JetBrains_Mono } from 'next/font/google';
import {
  Braces,
  CalendarClock,
  Check,
  Code2,
  MousePointerClick,
  PanelsTopLeft,
  SlidersHorizontal,
  type LucideIcon,
} from 'lucide-react';
import { NodeDemo } from '@/components/home/node-demo';
import { githubUrl } from '@/lib/shared';

const mono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-code' });

/*
 * One system for the whole page:
 *   type     h1 56 / h2 36, both medium with tight tracking; lead 17/28; body 15/24
 *   spacing  sections 160 apart; heading > lead 16; lead > content 56
 *   radius   frames 16, inner panels 12, buttons and tabs fully round
 */
const container = 'mx-auto w-full max-w-[1120px] px-6';
const section = `${container} pt-40`;
const h2 = 'text-[30px] leading-[1.1] font-medium tracking-[-0.03em] text-balance sm:text-[36px]';
const lead = 'mt-4 text-[17px] leading-7 text-balance';
const button =
  'inline-flex h-10 items-center rounded-full px-5 text-[15px] font-medium transition-opacity hover:opacity-85 focus-visible:outline-2 focus-visible:outline-offset-2';
const primary = `${button} bg-fd-primary text-fd-primary-foreground focus-visible:outline-fd-ring`;
const secondary = `${button} text-fd-muted-foreground hover:text-fd-foreground focus-visible:outline-fd-ring`;

const BUILDS: [LucideIcon, string, string][] = [
  [PanelsTopLeft, 'Panels and menus', 'Sidebar panels, menus and popups with buttons and fields.'],
  [MousePointerClick, 'Operators', 'Actions people run from a button or the search, with undo.'],
  [SlidersHorizontal, 'Properties', 'Settings saved in the file or in the preferences.'],
  [CalendarClock, 'Events', 'Run nodes when a file loads or saves, or the frame changes.'],
  [Braces, 'Functions', 'Turn part of a graph into one node you can reuse.'],
  [Code2, 'Python', 'Run your own script when there is no node for the job.'],
];

// what an assistant does over the MCP server for "add a button that adds a cube"
const TOOL_CALLS = [
  ['create_node', 'Panel'],
  ['create_node', 'Button'],
  ['set_node_prop', 'Button.operator = Add Cube'],
  ['connect_sockets', 'Panel.Interface to Button.Interface'],
  ['get_tree_code', 'Main'],
];

export default function HomePage() {
  return (
    <div className={`${mono.variable} overflow-x-clip pb-40`}>
      <section className={`${container} pt-24 text-center sm:pt-32`}>
        {/* non-breaking hyphen: "add-" / "ons" never splits */}
        <h1 className="mx-auto max-w-[20ch] text-[40px] leading-[1.05] font-medium tracking-[-0.04em] text-balance sm:text-[56px]">
          Build Blender add‑ons with nodes
        </h1>
        <p className={`${lead} mx-auto mt-6 max-w-[58ch] text-fd-muted-foreground`}>
          Connect nodes and Scripting Nodes writes the Python. Your add‑on runs in Blender while you
          build it, so every change shows up right away. You can also ask an AI assistant to place
          the nodes for you.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-2">
          <Link href="/docs/download" className={primary}>
            Download
          </Link>
          <Link href="/docs" className={secondary}>
            Read the docs
          </Link>
        </div>
        <div className="mt-20 text-left">
          <NodeDemo />
        </div>
      </section>

      <section className={section}>
        <div className="mx-auto max-w-[620px] text-center">
          <h2 className={h2}>What you can build</h2>
          <p className={`${lead} text-fd-muted-foreground`}>
            The same parts of Blender that Python add‑ons use, as nodes. When you're done, export a
            zip of plain Python files and install it like any other add‑on.
          </p>
        </div>
        <ul className="mx-auto mt-14 grid max-w-[960px] gap-x-12 gap-y-10 sm:grid-cols-2 lg:grid-cols-3">
          {BUILDS.map(([Icon, title, text]) => (
            <li key={title}>
              <Icon aria-hidden className="size-5 text-fd-muted-foreground" strokeWidth={1.75} />
              <p className="mt-4 text-[15px] font-medium">{title}</p>
              <p className="mt-1 text-[15px] leading-6 text-fd-muted-foreground">{text}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className={section}>
        <div className="grid grid-cols-[minmax(0,1fr)] items-center gap-14 rounded-2xl bg-[#161616] p-8 text-[#ededed] sm:p-14 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] dark:border dark:border-white/10">
          <div>
            <h2 className={h2}>Works with your AI assistant</h2>
            <p className={`${lead} max-w-[44ch] text-[#a1a1a1]`}>
              Start the MCP server from the sidebar and connect Claude Code, Codex or another MCP
              client. Ask for a tool and the assistant creates and connects nodes in the open file,
              then reads the generated code to check it. What it builds is a node graph, so you can
              see every step and change it yourself.
            </p>
            <Link
              href="/docs/ai/mcp-server"
              className={`${button} mt-8 bg-[#ededed] text-[#161616] focus-visible:outline-[#f2a60d]`}
            >
              Set up the MCP server
            </Link>
          </div>
          <figure className="rounded-xl bg-white/[0.05] p-5 text-[15px] leading-6">
            <figcaption className="sr-only">
              An assistant building a button with the MCP server
            </figcaption>
            <p className="ml-auto w-fit max-w-[85%] rounded-xl bg-white/10 px-4 py-2.5">
              Add a button to the sidebar that adds a cube
            </p>
            <ul className="mt-5 space-y-2 font-[family-name:var(--font-code)] text-[12.5px] leading-5 text-[#a1a1a1]">
              {TOOL_CALLS.map(([tool, args]) => (
                <li key={tool + args} className="flex items-center gap-2.5">
                  <Check aria-hidden className="size-3.5 shrink-0 text-[#f2a60d]" />
                  <span className="text-[#ededed]">{tool}</span>
                  <span className="truncate">{args}</span>
                </li>
              ))}
            </ul>
            <p className="mt-5 text-[#d4d4d4]">
              I added a My Tools panel with an Add Cube button to the Main tree. You'll find it in
              the 3D viewport sidebar.
            </p>
          </figure>
        </div>
      </section>

      <section className={`${section} text-center`}>
        <h2 className={h2}>Free and open source</h2>
        <p className={`${lead} text-fd-muted-foreground`}>For Blender 5.0 and later.</p>
        <div className="mt-8 flex flex-wrap justify-center gap-2">
          <Link href="/docs/download" className={primary}>
            Download
          </Link>
          <a href={githubUrl} className={secondary}>
            View on GitHub
          </a>
        </div>
      </section>
    </div>
  );
}
