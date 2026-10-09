import { Play } from 'lucide-react';

export type VideoProps = {
  /** Video file; without it a placeholder is shown */
  src?: string;
  title: string;
  poster?: string;
};

/** 16:9 video, or a placeholder until the video exists. */
export function Video({ src, title, poster }: VideoProps) {
  if (src) {
    return (
      <video
        src={src}
        poster={poster}
        title={title}
        controls
        preload="metadata"
        className="not-prose aspect-video w-full rounded-lg border bg-black"
      />
    );
  }
  return (
    <div className="not-prose relative flex aspect-video w-full flex-col justify-between overflow-hidden rounded-lg border bg-fd-card p-6 md:p-8">
      <span className="text-sm font-medium text-fd-muted-foreground">Video coming soon</span>
      <div className="flex items-end justify-between gap-4">
        <span className="text-2xl font-semibold tracking-[-0.022em] md:text-4xl">{title}</span>
        <span className="flex size-12 shrink-0 items-center justify-center rounded-full border bg-fd-background text-fd-muted-foreground">
          <Play className="size-5 translate-x-px" aria-hidden />
        </span>
      </div>
    </div>
  );
}
