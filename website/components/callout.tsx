import { CircleCheck, CircleX, Info, Lightbulb, TriangleAlert } from 'lucide-react';
import type { ReactNode } from 'react';

const types = {
  info: { icon: Info, color: 'text-fd-muted-foreground' },
  tip: { icon: Lightbulb, color: 'text-amber-500' },
  warn: { icon: TriangleAlert, color: 'text-amber-500' },
  error: { icon: CircleX, color: 'text-red-500' },
  success: { icon: CircleCheck, color: 'text-emerald-500' },
};

// Fumadocs' type names, so existing `type` values keep working
const aliases: Record<string, keyof typeof types> = { warning: 'warn', idea: 'tip' };

export type CalloutProps = {
  type?: keyof typeof types | 'warning' | 'idea';
  title?: ReactNode;
  children?: ReactNode;
};

/** Quiet boxed note: small icon on the first line, no accent bar. */
export function Callout({ type = 'info', title, children }: CalloutProps) {
  const { icon: Icon, color } = types[aliases[type] ?? (type as keyof typeof types)];
  return (
    <div className="sn-callout flex gap-3 rounded-lg border bg-fd-card px-4 py-3 text-sm/[22px] text-fd-muted-foreground">
      <Icon className={`mt-[3px] size-4 shrink-0 ${color}`} aria-hidden />
      <div className="sn-callout-body min-w-0 flex-1">
        {title && <p className="font-medium text-fd-foreground">{title}</p>}
        {children}
      </div>
    </div>
  );
}
