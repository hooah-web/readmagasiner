import sitemap from "@astrojs/sitemap";
import { defineConfig } from 'astro/config';

export default defineConfig({
  integrations: [sitemap()],
  site: 'https://readmagasiner.dk',
  trailingSlash: 'always',
  build: { format: 'directory' },
});
