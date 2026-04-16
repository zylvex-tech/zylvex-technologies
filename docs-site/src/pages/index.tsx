import type {FC} from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

const HomepageHero: FC = () => (
  <header className={styles.heroBanner}>
    <div className="container">
      <div className={styles.heroContent}>
        <div className={styles.heroBadge}>Spatial-Social Computing Platform</div>
        <h1 className={styles.heroTitle}>Zylvex Technologies</h1>
        <p className={styles.heroSubtitle}>
          Developer and user documentation for{' '}
          <strong>Spatial Canvas</strong> (AR anchor platform) and{' '}
          <strong>Mind Mapper</strong> (BCI-driven mind mapping).
        </p>
        <div className={styles.heroButtons}>
          <Link className="button button--primary button--lg" to="/docs/getting-started/introduction">
            Get Started →
          </Link>
          <Link className="button button--secondary button--lg" to="/docs/api-reference/auth-api">
            API Reference
          </Link>
        </div>
      </div>
    </div>
  </header>
);

interface FeatureItem {
  title: string;
  emoji: string;
  description: string;
  link: string;
}

const features: FeatureItem[] = [
  {
    title: 'Getting Started',
    emoji: '🚀',
    description: 'Introduction, 5-minute quickstart with Docker Compose, and full architecture overview with Mermaid diagrams.',
    link: '/docs/getting-started/introduction',
  },
  {
    title: 'API Reference',
    emoji: '📡',
    description: 'Complete API docs for Auth, Spatial Canvas, Mind Mapper, and Social services — with request/response examples.',
    link: '/docs/api-reference/auth-api',
  },
  {
    title: 'Guides',
    emoji: '📖',
    description: 'Mobile setup for iOS/Android, Alembic database migrations, test suites, and contribution workflow.',
    link: '/docs/guides/mobile-setup',
  },
  {
    title: 'Business',
    emoji: '📊',
    description: 'Product vision, visual roadmap, pricing tiers, and competitive analysis vs Pokémon GO, Notion, Miro, LinkedIn.',
    link: '/docs/business/product-vision',
  },
];

const HomepageFeatures: FC = () => (
  <section className={styles.features}>
    <div className="container">
      <div className={styles.featureGrid}>
        {features.map((item) => (
          <Link key={item.title} to={item.link} className={styles.featureCard}>
            <div className={styles.featureEmoji}>{item.emoji}</div>
            <h3 className={styles.featureTitle}>{item.title}</h3>
            <p className={styles.featureDescription}>{item.description}</p>
          </Link>
        ))}
      </div>
    </div>
  </section>
);

const Home: FC = () => {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout title={siteConfig.title} description={siteConfig.tagline}>
      <HomepageHero />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
};

export default Home;
