import { motion } from 'framer-motion';
import AppShell from '../components/AppShell';
import PageTransition from '../components/PageTransition';

const stagger = {
  visible: { transition: { staggerChildren: 0.06 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
};

function FeedSkeleton() {
  return (
    <div className="glass p-5 space-y-4">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full shimmer flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-3 shimmer rounded-md w-1/3" />
          <div className="h-2.5 shimmer rounded-md w-1/4" />
        </div>
      </div>
      <div className="space-y-2">
        <div className="h-3 shimmer rounded-md w-full" />
        <div className="h-3 shimmer rounded-md w-5/6" />
        <div className="h-3 shimmer rounded-md w-3/4" />
      </div>
      <div className="flex gap-4 pt-1">
        <div className="h-7 shimmer rounded-lg w-16" />
        <div className="h-7 shimmer rounded-lg w-16" />
        <div className="h-7 shimmer rounded-lg w-16" />
      </div>
    </div>
  );
}

export default function Feed() {
  return (
    <PageTransition>
      <AppShell>
        <div className="p-8 max-w-2xl mx-auto">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="space-y-6"
          >
            {/* Header */}
            <motion.div variants={fadeUp} className="text-center py-8">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-slate-100 mb-2">Community Feed</h1>
              <p className="text-slate-400 text-sm leading-relaxed max-w-md mx-auto">
                See what the community is anchoring and mapping in real time.
                Social features are in active development — launching soon.
              </p>
              <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 glass-sm text-xs text-amber-400 rounded-full">
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Coming Q1 2025
              </div>
            </motion.div>

            {/* Skeleton feed items */}
            {Array.from({ length: 6 }).map((_, i) => (
              <motion.div key={i} variants={fadeUp}>
                <FeedSkeleton />
              </motion.div>
            ))}
          </motion.div>
        </div>
      </AppShell>
    </PageTransition>
  );
}
