import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { register } from '../api/auth';
import { ApiError } from '../api/client';
import ThemeToggle from '../components/ThemeToggle';
import PageTransition from '../components/PageTransition';

const fadeUp = {
  hidden: { opacity: 0, y: 32 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.5, ease: 'easeOut' },
  }),
};

const stagger = {
  visible: { transition: { staggerChildren: 0.1 } },
};

export default function Landing() {
  const [formData, setFormData] = useState({ email: '', full_name: '', password: '' });
  const [formState, setFormState] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const waitlistRef = useRef<HTMLDivElement>(null);

  const scrollToWaitlist = () => {
    waitlistRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleWaitlist = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormState('loading');
    setErrorMsg('');
    try {
      await register(formData.email, formData.full_name, formData.password);
      setFormState('success');
    } catch (err) {
      setFormState('error');
      setErrorMsg(err instanceof ApiError ? err.message : 'Registration failed');
    }
  };

  return (
    <PageTransition>
      <div className="min-h-screen gradient-bg text-slate-100 overflow-x-hidden">
        {/* Nav */}
        <nav className="fixed top-0 left-0 right-0 z-50 glass-dark border-b border-white/8">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center glow-primary">
                <span className="text-white font-bold">Z</span>
              </div>
              <span className="font-semibold text-lg tracking-tight">Zylvex</span>
            </div>
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <Link
                to="/login"
                className="px-4 py-2 text-sm text-slate-300 hover:text-white transition-colors"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all duration-200 glow-primary-hover font-medium"
              >
                Sign up
              </Link>
            </div>
          </div>
        </nav>

        {/* Hero */}
        <section className="pt-32 pb-24 px-6">
          <div className="max-w-5xl mx-auto text-center">
            <motion.div
              initial="hidden"
              animate="visible"
              variants={stagger}
              className="space-y-6"
            >
              <motion.div variants={fadeUp} custom={0}>
                <span className="inline-flex items-center gap-2 px-3 py-1.5 glass-sm text-xs font-medium text-indigo-300 rounded-full mb-6">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
                  Now in Beta — Spatial AR + BCI Technology
                </span>
              </motion.div>

              <motion.h1
                variants={fadeUp}
                custom={1}
                className="text-6xl md:text-7xl lg:text-8xl font-black leading-none tracking-tighter"
              >
                The Future of{' '}
                <span className="text-gradient">Spatial Intelligence</span>
              </motion.h1>

              <motion.p
                variants={fadeUp}
                custom={2}
                className="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed"
              >
                Bridge the physical and digital worlds with AR-powered spatial anchors, and unlock
                the potential of your mind with brain-computer interface mind mapping.
              </motion.p>

              <motion.div
                variants={fadeUp}
                custom={3}
                className="flex flex-col sm:flex-row gap-4 justify-center pt-4"
              >
                <Link
                  to="/spatial-canvas"
                  className="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl font-semibold text-base transition-all duration-200 glow-primary-hover"
                >
                  Explore Spatial Canvas
                </Link>
                <button
                  onClick={scrollToWaitlist}
                  className="px-8 py-4 glass hover:bg-white/10 text-slate-200 rounded-2xl font-semibold text-base transition-all duration-200"
                >
                  Try Mind Mapper
                </button>
              </motion.div>
            </motion.div>
          </div>

          {/* Floating orbs */}
          <div className="absolute top-40 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute top-60 right-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
        </section>

        {/* Products */}
        <section className="py-24 px-6">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-80px' }}
              variants={stagger}
              className="grid md:grid-cols-2 gap-8"
            >
              {/* Spatial Canvas */}
              <motion.div
                variants={fadeUp}
                className="glass p-8 hover:bg-white/8 transition-all duration-300 group glow-primary-hover"
              >
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-indigo-600/10 border border-indigo-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-7 h-7 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-slate-100 mb-3">Spatial Canvas</h3>
                <p className="text-slate-400 leading-relaxed mb-6">
                  Drop persistent AR anchors in the real world. Share notes, messages, and media
                  at precise geographic locations — visible to anyone with the right access.
                </p>
                <ul className="space-y-2 mb-8">
                  {['GPS-precise AR anchors', 'Rich media content types', 'Proximity-based discovery', 'Real-time collaboration'].map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-slate-400">
                      <svg className="w-4 h-4 text-indigo-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition-all duration-200"
                >
                  Get Started
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </motion.div>

              {/* Mind Mapper */}
              <motion.div
                variants={fadeUp}
                custom={1}
                className="glass p-8 hover:bg-white/8 transition-all duration-300 group"
              >
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-600/10 border border-purple-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-7 h-7 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-slate-100 mb-3">Mind Mapper</h3>
                <p className="text-slate-400 leading-relaxed mb-6">
                  Visualize your thoughts with BCI-powered mind mapping. Track focus levels,
                  capture neural sessions, and build a living graph of your mind's architecture.
                </p>
                <ul className="space-y-2 mb-8">
                  {['BCI focus-level tracking', 'Dynamic node graphs', 'Session recordings', 'Neural timeline playback'].map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-slate-400">
                      <svg className="w-4 h-4 text-purple-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-sm font-medium transition-all duration-200"
                >
                  Get Started
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Waitlist */}
        <section ref={waitlistRef} className="py-24 px-6">
          <div className="max-w-2xl mx-auto">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-80px' }}
              variants={stagger}
              className="glass p-10 text-center"
            >
              {formState === 'success' ? (
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="space-y-4"
                >
                  <div className="w-16 h-16 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center mx-auto">
                    <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-slate-100">You're on the list!</h3>
                  <p className="text-slate-400">We'll be in touch soon. Check your email for confirmation.</p>
                  <Link to="/login" className="inline-block mt-4 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium transition-all duration-200">
                    Sign in to your account
                  </Link>
                </motion.div>
              ) : (
                <>
                  <motion.h2 variants={fadeUp} className="text-3xl font-bold text-slate-100 mb-3">
                    Join the Waitlist
                  </motion.h2>
                  <motion.p variants={fadeUp} custom={1} className="text-slate-400 mb-8">
                    Be among the first to access Zylvex's spatial intelligence platform.
                  </motion.p>
                  <motion.form
                    variants={fadeUp}
                    custom={2}
                    onSubmit={handleWaitlist}
                    className="space-y-4"
                  >
                    <input
                      type="text"
                      placeholder="Full name"
                      required
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      className="w-full px-4 py-3 bg-white/8 border border-white/12 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 transition-colors text-sm"
                    />
                    <input
                      type="email"
                      placeholder="Email address"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-4 py-3 bg-white/8 border border-white/12 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 transition-colors text-sm"
                    />
                    <input
                      type="password"
                      placeholder="Create a password"
                      required
                      minLength={8}
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="w-full px-4 py-3 bg-white/8 border border-white/12 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 transition-colors text-sm"
                    />
                    {formState === 'error' && (
                      <p className="text-red-400 text-sm">{errorMsg}</p>
                    )}
                    <motion.button
                      whileTap={{ scale: 0.98 }}
                      type="submit"
                      disabled={formState === 'loading'}
                      className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white rounded-xl font-semibold transition-all duration-200 glow-primary-hover flex items-center justify-center gap-2"
                    >
                      {formState === 'loading' ? (
                        <span className="w-5 h-5 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                      ) : 'Request Access'}
                    </motion.button>
                  </motion.form>
                </>
              )}
            </motion.div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-8 px-6 border-t border-white/8">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-xs">Z</span>
              </div>
              <span className="text-sm text-slate-500">© 2024 Zylvex Technologies</span>
            </div>
            <div className="flex gap-6">
              <Link to="/login" className="text-sm text-slate-500 hover:text-slate-300 transition-colors">Login</Link>
              <Link to="/register" className="text-sm text-slate-500 hover:text-slate-300 transition-colors">Register</Link>
            </div>
          </div>
        </footer>
      </div>
    </PageTransition>
  );
}
