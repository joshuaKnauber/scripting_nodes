import type { ReactNode } from 'react';
import { ArrowRight, Heart } from 'lucide-react';
import { supportFormUrl } from '@/lib/shared';

/*
 * The support form as printed orange vinyl: a sticker on the headline and a
 * larger panel at the end of the page. Both share the white die-cut edge, a
 * peeled corner, halftone print and a shadow that follows the outline
 * (drop-shadow, so it traces the peeled corner too).
 */

/* fine vinyl grain */
const grain = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .55 0'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)'/%3E%3C/svg%3E")`;

const shadow =
  '[filter:drop-shadow(0_1px_1px_rgba(0,0,0,0.3))_drop-shadow(0_6px_10px_rgba(0,0,0,0.28))] group-hover:[filter:drop-shadow(0_2px_2px_rgba(0,0,0,0.25))_drop-shadow(0_14px_22px_rgba(0,0,0,0.32))]';
const face = 'bg-[linear-gradient(170deg,#ffbb2e,#f29c06)] text-[#241503]';
/* the lifting layer; the link around it stays put so its hover area doesn't move */
const lift = `block transition-[transform,filter] duration-300 motion-reduce:transition-none ${shadow}`;
const motion = 'transition-transform duration-300 motion-reduce:transition-none';

/* halftone print: a dot grid on a 45° screen, dots swelling toward the bottom right */
function Halftone({ width, height, step = 6 }: { width: number; height: number; step?: number }) {
  const dots: [number, number, number][] = [];
  for (let row = 0; row * step <= height; row++) {
    for (let col = 0; col * step <= width; col++) {
      const x = col * step + (row % 2 ? step / 2 : 0);
      const y = row * step;
      const t = Math.min(1, Math.max(0, (x / width) * 0.75 + (y / height) * 0.35 - 0.3));
      const r = t * step * 0.52;
      if (r > 0.35) dots.push([x, y, Number(r.toFixed(2))]);
    }
  }
  return (
    <svg
      aria-hidden
      className="pointer-events-none absolute inset-0 size-full"
      preserveAspectRatio="xMaxYMax slice"
      viewBox={`0 0 ${width} ${height}`}
    >
      {dots.map(([x, y, r]) => (
        <circle key={`${x}-${y}`} cx={x} cy={y} r={r} fill="#c9560a" fillOpacity={0.4} />
      ))}
    </svg>
  );
}

/* grain, a glossy streak that slides across on hover, light from above */
function Finish({ radius }: { radius: string }) {
  return (
    <>
      <span
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.16] mix-blend-multiply"
        style={{ backgroundImage: grain }}
      />
      <span
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[linear-gradient(115deg,transparent_35%,rgba(255,255,255,0.6)_48%,transparent_60%)] bg-[length:260%_100%] bg-[position:100%_0] mix-blend-soft-light transition-[background-position] duration-700 group-hover:bg-[position:0%_0] motion-reduce:transition-none"
      />
      <span
        aria-hidden
        className={`pointer-events-none absolute inset-0 shadow-[inset_0_1px_0_rgba(255,255,255,0.45),inset_0_-1px_0_rgba(0,0,0,0.12)] ${radius}`}
      />
    </>
  );
}

/*
 * White edge with the corner cut off, plus the corner folded back. `peel` sets
 * --sn-peel (registered in global.css so it animates); the cut and the flap
 * both read it, so they grow together on hover.
 */
function DieCut({ peel, edge, children }: { peel: string; edge: string; children: ReactNode }) {
  return (
    <span
      className={`relative block transition-[--sn-peel] duration-300 motion-reduce:transition-none ${peel}`}
    >
      <span
        className={`block bg-white ${edge}`}
        style={{
          clipPath:
            'polygon(0 0, 100% 0, 100% calc(100% - var(--sn-peel)), calc(100% - var(--sn-peel)) 100%, 0 100%)',
        }}
      >
        {children}
      </span>
      <span
        aria-hidden
        style={{
          width: 'var(--sn-peel)',
          height: 'var(--sn-peel)',
          clipPath: 'polygon(0 0, 100% 0, 0 100%)',
        }}
        className="absolute right-0 bottom-0 bg-[linear-gradient(135deg,#ffffff_20%,#ebeae6_42%,#bdbcb6_50%)]"
      />
    </span>
  );
}

/* heart printed on a cream spot */
function HeartSpot({ className, icon }: { className: string; icon: string }) {
  return (
    <span
      className={`relative flex shrink-0 -rotate-[8deg] items-center justify-center rounded-full bg-[#fff6e3] shadow-[inset_0_-1px_0_rgba(0,0,0,0.12)] group-hover:scale-110 group-hover:-rotate-[14deg] ${motion} ${className}`}
    >
      <Heart aria-hidden className={`fill-[#e2421d] text-[#e2421d] ${icon}`} />
    </span>
  );
}

const arrow = `group-hover:translate-x-0.5 ${motion}`;

/* stuck on the headline's corner */
export function SupportSticker() {
  return (
    <a
      href={supportFormUrl}
      className="group absolute -top-16 right-0 block rotate-[5deg] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-fd-ring sm:-top-11 sm:-right-24"
    >
      <span className={`${lift} group-hover:-translate-y-0.5 group-hover:-rotate-2`}>
        <DieCut peel="[--sn-peel:20px] group-hover:[--sn-peel:28px]" edge="rounded-[14px] p-[3px]">
          <span
            className={`relative flex items-center gap-3 overflow-hidden rounded-[11px] py-3 pr-6 pl-3.5 text-left ${face}`}
          >
            <Halftone width={300} height={80} />
            <HeartSpot className="size-9" icon="size-[18px]" />
            <span className="relative">
              <span className="block text-[10.5px] leading-4 font-bold tracking-[0.12em] uppercase opacity-65">
                Quick survey
              </span>
              <span className="flex items-center gap-1.5 text-[17px] leading-5 font-bold tracking-[-0.015em] whitespace-nowrap">
                Help shape what&apos;s next
                <ArrowRight aria-hidden className={`size-4 ${arrow}`} />
              </span>
            </span>
            <Finish radius="rounded-[11px]" />
          </span>
        </DieCut>
      </span>
    </a>
  );
}

/* the same vinyl as a panel at the end of the page */
export function SupportCard() {
  return (
    <a
      href={supportFormUrl}
      className="group relative mx-auto block max-w-[760px] -rotate-1 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-fd-ring"
    >
      <span className={`${lift} group-hover:-translate-y-1 group-hover:rotate-1`}>
        <DieCut peel="[--sn-peel:36px] group-hover:[--sn-peel:48px]" edge="rounded-[22px] p-1">
          <span
            className={`relative flex flex-col items-center gap-6 overflow-hidden rounded-[18px] px-8 py-9 text-center sm:flex-row sm:gap-7 sm:py-10 sm:pr-14 sm:pl-10 sm:text-left ${face}`}
          >
            <Halftone width={760} height={200} step={8} />
            <HeartSpot className="size-16" icon="size-8" />
            <span className="relative flex-1">
              <span className="block text-[11px] leading-4 font-bold tracking-[0.12em] uppercase opacity-65">
                Quick survey
              </span>
              <span className="mt-1 block text-[26px] leading-tight font-bold tracking-[-0.025em] text-balance">
                Help shape what&apos;s next
              </span>
              <span className="mt-2 block text-[15px] leading-6 text-[#241503]/80">
                Tell me how you work in Blender and what you&apos;d build with it. It only takes a
                few minutes and helps me understand who uses Scripting Nodes.
              </span>
            </span>
            <span className="relative inline-flex h-11 shrink-0 items-center gap-2 rounded-full bg-[#241503] px-5 text-[15px] font-semibold text-[#ffd27a] shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]">
              Take the survey
              <ArrowRight aria-hidden className={`size-4 ${arrow}`} />
            </span>
            <Finish radius="rounded-[18px]" />
          </span>
        </DieCut>
      </span>
    </a>
  );
}
