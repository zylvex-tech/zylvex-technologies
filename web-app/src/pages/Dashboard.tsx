import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../store/auth';
import AppShell from '../components/AppShell';
import PageTransition from '../components/PageTransition';

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

const quickActions = [
  {
    title: 'Open Mind Mapper',
    subtitle: 'Visualize your thoughts',
    path: '/mind-mapper',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
    gradient: 'from-purple-500/20 to-pink-500/10',
    border: 'border-purple-500/20',
    iconColor: 'text-purple-400',
  },
  {
    title: 'Explore Anchors',
    subtitle: 'Discover nearby AR content',
    path: '/spatial-canvas',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    gradient: 'from-indigo-500/20 to-blue-500/10',
    border: 'border-indigo-500/20',
    iconColor: 'text-indigo-400',
  },
  {
    title: 'View Feed',
    subtitle: 'See community activity',
    path: '/feed',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
      </svg>
    ),
    gradient: 'from-green-500/20 to-teal-500/10',
    border: 'border-green-500/20',
    iconColor: 'text-green-400',
  },
];

const stagger = {
  visible: { transition: { staggerChildren: 0.08 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
};

export default function Dashboard() {
  const { state } = useAuth();
  const firstName = state.user?.full_name?.split(' ')[0] ?? 'there';

  return (
    <PageTransition>
      <AppShell>
        <div className="p-8 max-w-5xl mx-auto">
          {/* Welcome hero */}
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="mb-10"
          >
            <motion.p variants={fadeUp} className="text-sm text-slate-500 mb-1">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
            </motion.p>
            <motion.h1 variants={fadeUp} className="text-4xl font-bold text-slate-100 mb-2">
              {getGreeting()}, {firstName} 👋
            </motion.h1>
            <motion.p variants={fadeUp} className="text-slate-400">
              Here's what's happening in your spatial workspace today.
            </motion.p>
          </motion.div>

          {/* Quick actions */}
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="mb-10"
          >
            <motion.h2 variants={fadeUp} className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
              Quick Actions
            </motion.h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {quickActions.map((action) => (
                <motion.div key={action.path} variants={fadeUp}>
                  <Link
                    to={action.path}
                    className={`block glass p-5 hover:bg-white/8 transition-all duration-200 group glow-primary-hover`}
                  >
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${action.gradient} border ${action.border} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200`}>
                      <span className={action.iconColor}>{action.icon}</span>
                    </div>
                    <h3 className="text-slate-200 font-semibold mb-1">{action.title}</h3>
                    <p className="text-slate-500 text-xs">{action.subtitle}</p>
                  </Link>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Stats row */}
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="mb-10"
          >
            <motion.h2 variants={fadeUp} className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
              Your Activity
            </motion.h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'Anchors Placed', value: '—' },
                { label: 'Mind Maps', value: '—' },
                { label: 'BCI Sessions', value: '—' },
                { label: 'Nodes Created', value: '—' },
              ].map((stat) => (
                <motion.div
                  key={stat.label}
                  variants={fadeUp}
                  className="glass p-5"
                >
                  <p className="text-2xl font-bold text-slate-100 mb-1">{stat.value}</p>
                  <p className="text-xs text-slate-500">{stat.label}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Recent activity */}
          <motion.div initial="hidden" animate="visible" variants={stagger}>
            <motion.h2 variants={fadeUp} className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
              Recent Activity
            </motion.h2>
            <motion.div variants={fadeUp} className="glass p-8 flex flex-col items-center justify-center text-center">
              <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-4">
                <svg className="w-7 h-7 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p className="text-slate-400 text-sm font-medium mb-1">No activity yet</p>
              <p className="text-slate-600 text-xs mb-4">Start by placing an anchor or creating a mind map</p>
              <div className="flex gap-3">
                <Link
                  to="/spatial-canvas"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors"
                >
                  Place Anchor
                </Link>
                <Link
                  to="/mind-mapper"
                  className="px-4 py-2 glass-sm hover:bg-white/10 text-slate-300 rounded-lg text-xs font-medium transition-colors"
                >
                  Create Mind Map
                </Link>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </AppShell>
    </PageTransition>
  );
}
