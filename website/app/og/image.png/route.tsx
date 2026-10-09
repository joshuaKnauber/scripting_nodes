import { ogImage } from '@/lib/og/image';
import { appName } from '@/lib/shared';

export const revalidate = false;

// Default image for every page without its own (the homepage, 404)
export function GET() {
  return ogImage({ title: appName });
}
