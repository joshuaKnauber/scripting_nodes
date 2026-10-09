import { Card as BaseCard, type CardProps } from 'fumadocs-ui/components/card';

/** Fumadocs' Card with a plain icon: no box, border or shadow behind it. */
export function Card({ icon, title, ...props }: CardProps) {
  return (
    <BaseCard
      {...props}
      title={
        <>
          {icon && (
            <span className="mb-3 block text-fd-muted-foreground [&_svg]:size-4">{icon}</span>
          )}
          {title}
        </>
      }
    />
  );
}
