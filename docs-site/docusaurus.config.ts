import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Zylvex Technologies',
  tagline: 'Spatial-Social Computing Platform — Developer & User Documentation',
  favicon: 'img/favicon.ico',
  url: 'https://docs.zylvex.io',
  baseUrl: '/',
  organizationName: 'zylvex-tech',
  projectName: 'zylvex-technologies',
  onBrokenLinks: 'warn',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/zylvex-tech/zylvex-technologies/tree/main/docs-site/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    image: 'img/zylvex-social-card.png',
    navbar: {
      title: 'Zylvex Docs',
      logo: {
        alt: 'Zylvex Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'gettingStartedSidebar',
          position: 'left',
          label: 'Getting Started',
        },
        {
          type: 'docSidebar',
          sidebarId: 'apiReferenceSidebar',
          position: 'left',
          label: 'API Reference',
        },
        {
          type: 'docSidebar',
          sidebarId: 'guidesSidebar',
          position: 'left',
          label: 'Guides',
        },
        {
          type: 'docSidebar',
          sidebarId: 'businessSidebar',
          position: 'left',
          label: 'Business',
        },
        {
          href: 'https://github.com/zylvex-tech/zylvex-technologies',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {label: 'Getting Started', to: '/docs/getting-started/introduction'},
            {label: 'API Reference', to: '/docs/api-reference/auth-api'},
            {label: 'Guides', to: '/docs/guides/mobile-setup'},
          ],
        },
        {
          title: 'Community',
          items: [
            {label: 'GitHub', href: 'https://github.com/zylvex-tech/zylvex-technologies'},
          ],
        },
        {
          title: 'Company',
          items: [
            {label: 'Product Vision', to: '/docs/business/product-vision'},
            {label: 'Roadmap', to: '/docs/business/roadmap'},
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Zylvex Technologies, Inc. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'typescript', 'json', 'yaml', 'sql'],
    },
    // Algolia DocSearch — replace with real credentials when approved at https://docsearch.algolia.com/
    algolia: {
      appId: 'ZYLVEX_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'zylvex_docs',
      contextualSearch: true,
      searchParameters: {},
      searchPagePath: 'search',
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
