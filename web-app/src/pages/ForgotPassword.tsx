import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import PageTransition from '../components/PageTransition';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <PageTransition>
      <div className="min-h-screen gradient-bg flex items-center justify-center px-4">
        <div className="absolute top-20 left-1/3 w-80 h-80 bg-indigo-500/8 rounded-full blur-3xl pointer-events-none" />

        <motion.div
          initial={{ opacity: 0, y: 24, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <Link to="/" className="inline-flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center glow-primary">
                <span className="text-white font-bold text-xl">Z</span>
              </div>
              <span className="text-xl font-semibold text-slate-100">Zylvex</span>
            </Link>
          </div>

          <div className="glass p-8">
            {submitted ? (
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="text-center space-y-4"
              >
                <div className="w-16 h-16 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center mx-auto">
                  <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-slate-100">Check your email</h2>
                <p className="text-slate-400 text-sm">
                  We sent a password reset link to <span className="text-slate-200 font-medium">{email}</span>.
                  Check your inbox and follow the instructions.
                </p>
                <Link
                  to="/login"
                  className="inline-block mt-4 px-6 py-2.5 glass-sm text-sm text-slate-300 hover:text-white rounded-xl transition-colors"
                >
                  Back to sign in
                </Link>
              </motion.div>
            ) : (
              <>
                <div className="mb-8">
                  <h1 className="text-2xl font-bold text-slate-100 mb-2">Reset your password</h1>
                  <p className="text-slate-400 text-sm">
                    Enter your email address and we'll send you a link to reset your password.
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-2">Email address</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      placeholder="you@example.com"
                      className="w-full px-4 py-3 bg-white/6 border border-white/10 rounded-xl text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/60 transition-colors text-sm"
                    />
                  </div>

                  <motion.button
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold transition-all duration-200 glow-primary-hover"
                  >
                    Send reset link
                  </motion.button>
                </form>

                <p className="text-center text-sm text-slate-500 mt-6">
                  <Link to="/login" className="text-indigo-400 hover:text-indigo-300 transition-colors">
                    ← Back to sign in
                  </Link>
                </p>
              </>
            )}
          </div>
        </motion.div>
      </div>
    </PageTransition>
  );
}
