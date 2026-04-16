import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  gettingStartedSidebar: [
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/introduction',
        'getting-started/quickstart',
        'getting-started/architecture-overview',
      ],
    },
  ],

  apiReferenceSidebar: [
    {
      type: 'category',
      label: 'API Reference',
      collapsed: false,
      items: [
        'api-reference/auth-api',
        'api-reference/spatial-canvas-api',
        'api-reference/mind-mapper-api',
        'api-reference/social-api',
      ],
    },
  ],

  guidesSidebar: [
    {
      type: 'category',
      label: 'Guides',
      collapsed: false,
      items: [
        'guides/mobile-setup',
        'guides/database-migrations',
        'guides/testing-guide',
        'guides/contributing',
      ],
    },
  ],

  businessSidebar: [
    {
      type: 'category',
      label: 'Business',
      collapsed: false,
      items: [
        'business/product-vision',
        'business/roadmap',
        'business/monetization',
        'business/competitive-analysis',
      ],
    },
  ],
};

export default sidebars;
