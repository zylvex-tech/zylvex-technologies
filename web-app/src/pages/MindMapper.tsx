import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { listMindmaps, createMindmap, deleteMindmap } from '../api/mindmaps';
import { ApiError } from '../api/client';
import type { MindMapResponse } from '../api/types';
import AppShell from '../components/AppShell';
import PageTransition from '../components/PageTransition';
import Modal from '../components/Modal';
import SkeletonLoader from '../components/SkeletonLoader';
import { useToast } from '../components/Toast';

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function MindMapper() {
  const [mindmaps, setMindmaps] = useState<MindMapResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selected, setSelected] = useState<MindMapResponse | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [creating, setCreating] = useState(false);
  const { showToast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    listMindmaps()
      .then(setMindmaps)
      .catch((err) => {
        showToast(err instanceof ApiError ? err.message : 'Failed to load mind maps', 'error');
      })
      .finally(() => setIsLoading(false));
  }, [showToast]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      const map = await createMindmap(newTitle.trim());
      setMindmaps((prev) => [map, ...prev]);
      setSelected(map);
      setModalOpen(false);
      setNewTitle('');
      showToast('Mind map created!', 'success');
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Failed to create mind map', 'error');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteMindmap(id);
      setMindmaps((prev) => prev.filter((m) => m.id !== id));
      if (selected?.id === id) setSelected(null);
      showToast('Mind map deleted', 'info');
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Failed to delete', 'error');
    }
  };

  return (
    <PageTransition>
      <AppShell>
        <div className="flex h-full">
          {/* Left panel */}
          <div className="w-72 flex-shrink-0 border-r border-white/8 flex flex-col">
            <div className="p-5 border-b border-white/8 flex items-center justify-between">
              <div>
                <h2 className="text-slate-100 font-semibold">Mind Maps</h2>
                <p className="text-xs text-slate-500 mt-0.5">{mindmaps.length} maps</p>
              </div>
              <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={() => setModalOpen(true)}
                className="w-8 h-8 rounded-lg bg-indigo-600 hover:bg-indigo-500 flex items-center justify-center transition-colors"
              >
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
              </motion.button>
            </div>

            <div className="flex-1 overflow-y-auto p-3">
              {isLoading ? (
                <div className="space-y-2">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="glass-sm p-3">
                      <SkeletonLoader lines={2} />
                    </div>
                  ))}
                </div>
              ) : mindmaps.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-48 text-center px-4">
                  <p className="text-slate-500 text-sm mb-3">No mind maps yet</p>
                  <button
                    onClick={() => setModalOpen(true)}
                    className="text-indigo-400 text-xs hover:text-indigo-300 transition-colors"
                  >
                    Create your first map →
                  </button>
                </div>
              ) : (
                <AnimatePresence>
                  {mindmaps.map((map, i) => (
                    <motion.div
                      key={map.id}
                      initial={{ opacity: 0, x: -16 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -16 }}
                      transition={{ delay: i * 0.04, duration: 0.25 }}
                      onClick={() => setSelected(map)}
                      className={`group relative p-3 rounded-xl cursor-pointer transition-all duration-150 mb-1 ${
                        selected?.id === map.id
                          ? 'bg-indigo-500/15 border border-indigo-500/20'
                          : 'hover:bg-white/6'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <p className="text-sm text-slate-200 font-medium truncate">{map.title}</p>
                          <p className="text-xs text-slate-500 mt-0.5">
                            {map.node_count} nodes · {formatDate(map.created_at)}
                          </p>
                        </div>
                        <button
                          onClick={(e) => handleDelete(map.id, e)}
                          className="opacity-0 group-hover:opacity-100 w-6 h-6 flex items-center justify-center rounded-md hover:bg-red-500/20 transition-all duration-150"
                        >
                          <svg className="w-3.5 h-3.5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              )}
            </div>
          </div>

          {/* Main canvas area */}
          <div className="flex-1 flex flex-col items-center justify-center p-8">
            {selected ? (
              <motion.div
                key={selected.id}
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className="w-full h-full flex flex-col"
              >
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h1 className="text-2xl font-bold text-slate-100">{selected.title}</h1>
                    <p className="text-sm text-slate-500 mt-1">
                      {selected.node_count} nodes · Created {formatDate(selected.created_at)}
                    </p>
                  </div>
                  <button
                    onClick={() => setModalOpen(true)}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition-colors"
                  >
                    + New Map
                  </button>
                </div>

                <div className="flex-1 glass rounded-2xl border-2 border-dashed border-white/10 flex flex-col items-center justify-center text-center p-12">
                  <div className="relative mb-8">
                    <div className="w-16 h-16 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center mx-auto">
                      <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-purple-500 border-2 border-[#0a0a0f]" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-200 mb-2">
                    {selected.node_count === 0 ? 'Empty canvas' : `${selected.node_count} nodes`}
                  </h3>
                  <p className="text-slate-500 text-sm max-w-xs mb-6">
                    Open the interactive canvas to visualize, edit and arrange your mind map nodes.
                  </p>
                  <motion.button
                    whileTap={{ scale: 0.97 }}
                    onClick={() => navigate(`/mind-mapper/${selected.id}`)}
                    className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold text-sm transition-colors flex items-center gap-2 glow-primary-hover"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                    </svg>
                    Open Canvas
                  </motion.button>
                </div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className="flex flex-col items-center justify-center text-center max-w-sm"
              >
                <div className="relative mb-8">
                  <svg className="w-32 h-32 text-slate-700" viewBox="0 0 200 200" fill="none">
                    <circle cx="100" cy="100" r="12" fill="currentColor" opacity="0.6" />
                    <circle cx="50" cy="70" r="8" fill="currentColor" opacity="0.4" />
                    <circle cx="150" cy="70" r="8" fill="currentColor" opacity="0.4" />
                    <circle cx="40" cy="140" r="6" fill="currentColor" opacity="0.3" />
                    <circle cx="160" cy="140" r="6" fill="currentColor" opacity="0.3" />
                    <circle cx="100" cy="160" r="6" fill="currentColor" opacity="0.3" />
                    <line x1="100" y1="100" x2="50" y2="70" stroke="currentColor" strokeWidth="2" opacity="0.3" />
                    <line x1="100" y1="100" x2="150" y2="70" stroke="currentColor" strokeWidth="2" opacity="0.3" />
                    <line x1="50" y1="70" x2="40" y2="140" stroke="currentColor" strokeWidth="2" opacity="0.2" />
                    <line x1="150" y1="70" x2="160" y2="140" stroke="currentColor" strokeWidth="2" opacity="0.2" />
                    <line x1="100" y1="100" x2="100" y2="160" stroke="currentColor" strokeWidth="2" opacity="0.2" />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-slate-200 mb-3">Your Mind, Mapped</h2>
                <p className="text-slate-500 text-sm mb-6 leading-relaxed">
                  Create a mind map to start organizing your thoughts with BCI-powered focus tracking.
                </p>
                <motion.button
                  whileTap={{ scale: 0.97 }}
                  onClick={() => setModalOpen(true)}
                  className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold transition-all duration-200 glow-primary-hover"
                >
                  Create your first mind map
                </motion.button>
              </motion.div>
            )}
          </div>
        </div>

        <Modal
          isOpen={modalOpen}
          onClose={() => { setModalOpen(false); setNewTitle(''); }}
          title="New Mind Map"
        >
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-2">Map title</label>
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="e.g. Project Brainstorm"
                required
                autoFocus
                className="w-full px-4 py-3 bg-white/6 border border-white/10 rounded-xl text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/60 transition-colors text-sm"
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => { setModalOpen(false); setNewTitle(''); }}
                className="flex-1 py-2.5 glass-sm hover:bg-white/10 text-slate-300 rounded-xl text-sm font-medium transition-colors"
              >
                Cancel
              </button>
              <motion.button
                whileTap={{ scale: 0.97 }}
                type="submit"
                disabled={creating}
                className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white rounded-xl text-sm font-semibold transition-colors flex items-center justify-center"
              >
                {creating ? (
                  <span className="w-4 h-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                ) : 'Create'}
              </motion.button>
            </div>
          </form>
        </Modal>
      </AppShell>
    </PageTransition>
  );
}
