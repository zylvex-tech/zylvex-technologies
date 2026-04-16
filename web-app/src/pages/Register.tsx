import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { register as apiRegister, login as apiLogin } from '../api/auth';
import { ApiError } from '../api/client';
import { useAuth } from '../store/auth';
import PageTransition from '../components/PageTransition';

export default function Register() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await apiRegister(email, fullName, password);
      const tokens = await apiLogin(email, password);
      await login(tokens.access_token, tokens.refresh_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageTransition>
      <div className="min-h-screen gradient-bg flex items-center justify-center px-4">
        <div className="absolute top-20 right-1/3 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-indigo-500/8 rounded-full blur-3xl pointer-events-none" />

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
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-slate-100 mb-2">Create your account</h1>
              <p className="text-slate-400 text-sm">Join the future of spatial intelligence</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2">Full name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  placeholder="Jane Doe"
                  className="w-full px-4 py-3 bg-white/6 border border-white/10 rounded-xl text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/60 transition-colors text-sm"
                />
              </div>

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

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  placeholder="Min. 8 characters"
                  className="w-full px-4 py-3 bg-white/6 border border-white/10 rounded-xl text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/60 transition-colors text-sm"
                />
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-xl"
                >
                  <svg className="w-4 h-4 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm text-red-400">{error}</span>
                </motion.div>
              )}

              <motion.button
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white rounded-xl font-semibold transition-all duration-200 glow-primary-hover flex items-center justify-center gap-2 mt-2"
              >
                {isLoading ? (
                  <span className="w-5 h-5 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                ) : 'Create account'}
              </motion.button>
            </form>

            <p className="text-center text-sm text-slate-500 mt-6">
              Already have an account?{' '}
              <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
                Sign in
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </PageTransition>
  );
}
