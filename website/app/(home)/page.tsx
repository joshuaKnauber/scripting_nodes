import Link from 'next/link';
import { JetBrains_Mono } from 'next/font/google';
import { AssistantDemo } from '@/components/home/assistant-demo';
import { FeatureGraph } from '@/components/home/feature-graph';
import { NodeDemo } from '@/components/home/node-demo';
import { Logo } from '@/components/logo';
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

export default function HomePage() {
  return (
    <div className={`${mono.variable} overflow-x-clip pb-40`}>
      <section className={`${container} pt-24 text-center sm:pt-32`}>
        {/* non-breaking hyphen: "add-" / "ons" never splits */}
        <h1 className="mx-auto text-[40px] leading-[1.05] font-normal tracking-[-0.04em] text-balance sm:text-[56px]">
          Build Blender add‑ons with nodes
        </h1>
        <p className={`${lead} mx-auto mt-5 max-w-[640px] text-fd-muted-foreground`}>
          Connect nodes and Scripting Nodes writes the Python. Or ask an AI assistant to build the
          graph for you.
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
        <FeatureGraph />
      </section>

      <section className={section}>
        <div className="mx-auto max-w-[620px] text-center">
          <h2 className={h2}>Works with your AI assistant</h2>
          <p className={`${lead} text-fd-muted-foreground`}>
            Start the MCP server from the sidebar and connect Claude Code, Codex or another MCP
            client. The assistant builds the graph in your open file and reads the generated code to
            check it. You see every node it adds and can change it yourself.
          </p>
        </div>
        <AssistantDemo />
        <div className="mt-10 flex justify-center">
          <Link href="/docs/ai/mcp-server" className={`${secondary} border`}>
            Set up the MCP server
          </Link>
        </div>
      </section>

      <section className={section}>
        <div className="flex flex-col items-center gap-8 sm:flex-row sm:justify-center sm:gap-12">
          <Logo className="size-28 shrink-0 sm:size-36" />
          <div className="text-center sm:text-left">
            <h2 className={h2}>Free and open source</h2>
            <p className={`${lead} text-fd-muted-foreground`}>For Blender 5.0 and later.</p>
            <div className="mt-8 flex flex-wrap justify-center gap-2 sm:justify-start">
              <Link href="/docs/download" className={primary}>
                Download
              </Link>
              <a href={githubUrl} className={secondary}>
                View on GitHub
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
