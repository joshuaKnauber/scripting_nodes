import defaultMdxComponents from 'fumadocs-ui/mdx';
import { ImageZoom, type ImageZoomProps } from 'fumadocs-ui/components/image-zoom';
import { Step, Steps } from 'fumadocs-ui/components/steps';
import { Tab, Tabs } from 'fumadocs-ui/components/tabs';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents) {
  return {
    ...defaultMdxComponents,
    // Click-to-zoom on every image, so Blender screenshots stay readable
    img: (props) => <ImageZoom {...(props as ImageZoomProps)} />,
    Step,
    Steps,
    Tab,
    Tabs,
    ...components,
  } satisfies MDXComponents;
}

export const useMDXComponents = getMDXComponents;

declare global {
  type MDXProvidedComponents = ReturnType<typeof getMDXComponents>;
}
