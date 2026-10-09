import defaultMdxComponents from 'fumadocs-ui/mdx';
import { ImageZoom, type ImageZoomProps } from 'fumadocs-ui/components/image-zoom';
import { Step, Steps } from 'fumadocs-ui/components/steps';
import { Tab, Tabs } from 'fumadocs-ui/components/tabs';
import type { MDXComponents } from 'mdx/types';
import { Callout } from '@/components/callout';
import { Card } from '@/components/card';
import { DownloadButton } from '@/components/download-button';
import { Video } from '@/components/video';

export function getMDXComponents(components?: MDXComponents) {
  return {
    ...defaultMdxComponents,
    // Click-to-zoom on every image, so Blender screenshots stay readable
    img: (props) => <ImageZoom {...(props as ImageZoomProps)} />,
    Callout,
    Card,
    DownloadButton,
    Step,
    Steps,
    Tab,
    Tabs,
    Video,
    ...components,
  } satisfies MDXComponents;
}

export const useMDXComponents = getMDXComponents;

declare global {
  type MDXProvidedComponents = ReturnType<typeof getMDXComponents>;
}
