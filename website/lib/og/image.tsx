import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { ImageResponse } from 'next/og';
import { logoPath } from '@/components/logo';

export const ogSize = { width: 1200, height: 630 };

const font = join(process.cwd(), 'lib/og/inter-500.ttf');

/* Dark canvas, the snake large on the left, one title beside it. */
export async function ogImage({
  title,
  label,
}: {
  title: string;
  /** Small muted line above the title, e.g. "Scripting Nodes Docs" */
  label?: string;
}) {
  return new ImageResponse(
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        width: '100%',
        height: '100%',
        padding: '0 96px',
        backgroundColor: '#0a0a0a',
        color: '#fafafa',
        fontFamily: 'Inter',
        fontWeight: 500,
      }}
    >
      <svg width="320" height="320" viewBox="-16 0 642 642" fill="#fafafa">
        <path fillRule="evenodd" clipRule="evenodd" d={logoPath} />
      </svg>
      <div style={{ display: 'flex', flexDirection: 'column', marginLeft: 72, flex: 1 }}>
        {label && <div style={{ fontSize: 30, color: '#71717a', marginBottom: 16 }}>{label}</div>}
        <div
          style={{
            fontSize: 76,
            lineHeight: 1.05,
            letterSpacing: '-0.04em',
            textWrap: 'balance',
          }}
        >
          {title}
        </div>
      </div>
    </div>,
    {
      ...ogSize,
      fonts: [{ name: 'Inter', data: await readFile(font), weight: 500, style: 'normal' }],
    },
  );
}
