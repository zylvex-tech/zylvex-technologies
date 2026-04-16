import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  Handle,
  Position,
  NodeProps,
  EdgeProps,
  getBezierPath,
  useReactFlow,
  ReactFlowProvider,
  NodeTypes,
  EdgeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { toPng } from 'html-to-image';
import { motion, AnimatePresence } from 'framer-motion';
import { listNodes, createNode, updateNode } from '../api/mindmaps';
import { ApiError } from '../api/client';
import type { NodeResponse } from '../api/types';
import { useTheme } from '../hooks/useTheme';
import { useToast } from '../components/Toast';

// ─────────────────────────── helpers ──────────────────────────────

function focusColor(level: number): { ring: string; badge: string; hex: string } {
  if (level >= 0.67) return { ring: '#10b981', badge: 'bg-emerald-500/20 text-emerald-400', hex: '#10b981' };
  if (level >= 0.34) return { ring: '#f59e0b', badge: 'bg-yellow-500/20 text-yellow-400', hex: '#f59e0b' };
  return { ring: '#ef4444', badge: 'bg-red-500/20 text-red-400', hex: '#ef4444' };
}

// ─────────────────────────── custom node ──────────────────────────

type GlassNodeData = {
  text: string;
  focus_level: number;
  color: string;
  nodeId: string;
  mindmapId: string;
  focusOverlay: boolean;
  onEdit: (nodeId: string, newText: string) => void;
};

function GlassNode({ data, selected }: NodeProps<GlassNodeData>) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(data.text);
  const inputRef = useRef<HTMLInputElement>(null);
  const fc = focusColor(data.focus_level);

  const scale = data.focusOverlay ? Math.max(0.65, Math.min(1.4, 0.65 + data.focus_level * 0.75)) : 1;

  const handleDoubleClick = () => {
    setEditing(true);
    setDraft(data.text);
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const commitEdit = () => {
    setEditing(false);
    if (draft.trim() && draft.trim() !== data.text) {
      data.onEdit(data.nodeId, draft.trim());
    }
  };

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        transformOrigin: 'center',
        background: 'rgba(255,255,255,0.07)',
        backdropFilter: 'blur(14px)',
        WebkitBackdropFilter: 'blur(14px)',
        border: `2px solid ${selected ? '#6366f1' : fc.ring}`,
        borderRadius: '12px',
        padding: '10px 14px',
        minWidth: '140px',
        maxWidth: '220px',
        boxShadow: selected
          ? `0 0 0 2px rgba(99,102,241,0.4), 0 4px 24px rgba(0,0,0,0.3)`
          : `0 4px 24px rgba(0,0,0,0.25)`,
        cursor: 'default',
        userSelect: 'none',
      }}
      onDoubleClick={handleDoubleClick}
    >
      <Handle type="target" position={Position.Top} style={{ background: fc.hex, border: 'none', width: 8, height: 8 }} />

      {editing ? (
        <input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={commitEdit}
          onKeyDown={(e) => { if (e.key === 'Enter') commitEdit(); if (e.key === 'Escape') setEditing(false); }}
          style={{
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: '#f8fafc',
            fontSize: '13px',
            fontWeight: 500,
            width: '100%',
            fontFamily: 'Inter, system-ui, sans-serif',
          }}
        />
      ) : (
        <p style={{ color: '#f8fafc', fontSize: '13px', fontWeight: 500, margin: 0, wordBreak: 'break-word' }}>
          {data.text}
        </p>
      )}

      <div style={{ marginTop: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
        <span
          style={{
            fontSize: '10px',
            fontWeight: 600,
            padding: '2px 6px',
            borderRadius: '999px',
            background: `${fc.hex}22`,
            color: fc.hex,
            fontFamily: 'Inter, system-ui, sans-serif',
          }}
        >
          {Math.round(data.focus_level * 100)}%
        </span>
        <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', fontFamily: 'Inter, system-ui, sans-serif' }}>focus</span>
      </div>

      <Handle type="source" position={Position.Bottom} style={{ background: fc.hex, border: 'none', width: 8, height: 8 }} />
    </div>
  );
}

// ─────────────────────── custom animated edge ─────────────────────

function AnimatedGradientEdge({
  id,
  sourceX, sourceY,
  targetX, targetY,
  sourcePosition, targetPosition,
}: EdgeProps) {
  const [edgePath] = getBezierPath({ sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition });
  const gradId = `eg-${id}`;

  return (
    <>
      <defs>
        <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#6366f1" stopOpacity="0.9" />
          <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.7" />
        </linearGradient>
      </defs>
      <path
        d={edgePath}
        fill="none"
        stroke={`url(#${gradId})`}
        strokeWidth={2}
        strokeDasharray="6 3"
        style={{ animation: 'edgeDash 1.2s linear infinite' }}
      />
    </>
  );
}

// ──────────────────────── converter helpers ────────────────────────

function backendNodesToFlow(
  nodes: NodeResponse[],
  mindmapId: string,
  focusOverlay: boolean,
  onEdit: (nodeId: string, newText: string) => void,
): Node<GlassNodeData>[] {
  return nodes.map((n) => ({
    id: n.id,
    type: 'glassNode',
    position: { x: n.x ?? 0, y: n.y ?? 0 },
    data: {
      text: n.text,
      focus_level: n.focus_level ?? 0.5,
      color: n.color ?? '#6366f1',
      nodeId: n.id,
      mindmapId,
      focusOverlay,
      onEdit,
    },
    draggable: true,
  }));
}

function backendNodesToEdges(nodes: NodeResponse[]): Edge[] {
  return nodes
    .filter((n) => n.parent_id)
    .map((n) => ({
      id: `e-${n.parent_id}-${n.id}`,
      source: n.parent_id as string,
      target: n.id,
      type: 'animatedGradient',
      animated: false,
    }));
}

// ──────────────────────────── inner canvas ───────────────────────

const nodeTypes: NodeTypes = { glassNode: GlassNode };
const edgeTypes: EdgeTypes = { animatedGradient: AnimatedGradientEdge };

interface CanvasProps {
  mapId: string;
}

function MindMapCanvas({ mapId }: CanvasProps) {
  const { showToast } = useToast();
  const { isDark } = useTheme();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();
  const navigate = useNavigate();

  const [rawNodes, setRawNodes] = useState<NodeResponse[]>([]);
  const [nodes, setNodes, onNodesChange] = useNodesState<GlassNodeData>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [focusOverlay, setFocusOverlay] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [newNodeTitle, setNewNodeTitle] = useState('');
  const [newNodeParent, setNewNodeParent] = useState<string>('');
  const [creating, setCreating] = useState(false);

  const onEdit = useCallback(
    (nodeId: string, newText: string) => {
      updateNode(mapId, nodeId, { text: newText })
        .then(() => {
          setRawNodes((prev) => prev.map((n) => (n.id === nodeId ? { ...n, text: newText } : n)));
          setNodes((prev) =>
            prev.map((n) =>
              n.id === nodeId ? { ...n, data: { ...n.data, text: newText } } : n,
            ),
          );
        })
        .catch(() => showToast('Failed to save node text', 'error'));
    },
    [mapId, setNodes, showToast],
  );

  const buildFlow = useCallback(
    (backendNodes: NodeResponse[], overlay: boolean) => {
      const flowNodes = backendNodesToFlow(backendNodes, mapId, overlay, onEdit);
      const flowEdges = backendNodesToEdges(backendNodes);
      setNodes(flowNodes);
      setEdges(flowEdges);
    },
    [mapId, onEdit, setNodes, setEdges],
  );

  useEffect(() => {
    setIsLoading(true);
    listNodes(mapId)
      .then((backendNodes) => {
        setRawNodes(backendNodes);
        buildFlow(backendNodes, false);
      })
      .catch((err) => {
        showToast(err instanceof ApiError ? err.message : 'Failed to load nodes', 'error');
      })
      .finally(() => setIsLoading(false));
  }, [mapId, buildFlow, showToast]);

  // Re-apply focusOverlay changes to existing nodes
  useEffect(() => {
    setNodes((prev) =>
      prev.map((n) => ({ ...n, data: { ...n.data, focusOverlay, onEdit } })),
    );
  }, [focusOverlay, onEdit, setNodes]);

  const onNodeDragStop = useCallback(
    (_: React.MouseEvent, node: Node<GlassNodeData>) => {
      updateNode(mapId, node.data.nodeId, { x: node.position.x, y: node.position.y }).catch(() =>
        showToast('Failed to save node position', 'error'),
      );
    },
    [mapId, showToast],
  );

  const handleAddNode = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!newNodeTitle.trim()) return;
      setCreating(true);
      try {
        // Position: center-ish with offset
        const pos = screenToFlowPosition({ x: 400, y: 300 });
        const created = await createNode(mapId, {
          text: newNodeTitle.trim(),
          focus_level: 0.5,
          color: '#6366f1',
          x: pos.x + Math.random() * 100 - 50,
          y: pos.y + Math.random() * 100 - 50,
          parent_id: newNodeParent || null,
        });
        setRawNodes((prev) => [...prev, created]);
        const newFlowNode: Node<GlassNodeData> = {
          id: created.id,
          type: 'glassNode',
          position: { x: created.x, y: created.y },
          data: {
            text: created.text,
            focus_level: created.focus_level,
            color: created.color,
            nodeId: created.id,
            mindmapId: mapId,
            focusOverlay,
            onEdit,
          },
          draggable: true,
        };
        setNodes((prev) => [...prev, newFlowNode]);
        if (created.parent_id) {
          setEdges((prev) => [
            ...prev,
            {
              id: `e-${created.parent_id}-${created.id}`,
              source: created.parent_id as string,
              target: created.id,
              type: 'animatedGradient',
            },
          ]);
        }
        setDrawerOpen(false);
        setNewNodeTitle('');
        setNewNodeParent('');
        showToast('Node added', 'success');
      } catch (err) {
        showToast(err instanceof ApiError ? err.message : 'Failed to create node', 'error');
      } finally {
        setCreating(false);
      }
    },
    [mapId, newNodeTitle, newNodeParent, focusOverlay, onEdit, screenToFlowPosition, setNodes, setEdges, showToast],
  );

  const handleExportPng = useCallback(() => {
    const el = reactFlowWrapper.current;
    if (!el) return;
    toPng(el, { backgroundColor: isDark ? '#0a0a0f' : '#f8fafc', pixelRatio: 2 })
      .then((dataUrl) => {
        const a = document.createElement('a');
        a.href = dataUrl;
        a.download = `mind-map-${mapId}.png`;
        a.click();
        showToast('PNG exported', 'success');
      })
      .catch(() => showToast('PNG export failed', 'error'));
  }, [mapId, isDark, showToast]);

  const handleExportJson = useCallback(() => {
    const json = JSON.stringify(
      {
        mindmap_id: mapId,
        nodes: rawNodes,
        edges: edges.map((e) => ({ id: e.id, source: e.source, target: e.target })),
      },
      null,
      2,
    );
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mind-map-${mapId}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('JSON exported', 'success');
  }, [mapId, rawNodes, edges, showToast]);

  const bgColor = isDark ? '#0a0a0f' : '#f8fafc';
  const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.07)';

  const minimapNodeColor = useMemo(() => (n: Node<GlassNodeData>) => {
    return focusColor(n.data?.focus_level ?? 0.5).hex;
  }, []);

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0a0a0f]">
        <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col relative overflow-hidden" style={{ background: bgColor }}>
      {/* Top toolbar */}
      <div
        className="absolute top-4 left-1/2 -translate-x-1/2 z-10 flex items-center gap-2 px-3 py-2 rounded-2xl"
        style={{ background: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)', backdropFilter: 'blur(12px)', border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}` }}
      >
        {/* Back */}
        <button
          onClick={() => navigate('/mind-mapper')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-colors hover:bg-white/10"
          style={{ color: isDark ? '#94a3b8' : '#475569' }}
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Maps
        </button>

        <div className="w-px h-4" style={{ background: isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)' }} />

        {/* Focus overlay toggle */}
        <button
          onClick={() => setFocusOverlay((v) => !v)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all"
          style={{
            background: focusOverlay ? 'rgba(99,102,241,0.25)' : 'transparent',
            color: focusOverlay ? '#818cf8' : isDark ? '#94a3b8' : '#475569',
            border: focusOverlay ? '1px solid rgba(99,102,241,0.3)' : '1px solid transparent',
          }}
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <circle cx="12" cy="12" r="3" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
          </svg>
          Focus Overlay
        </button>

        <div className="w-px h-4" style={{ background: isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)' }} />

        {/* Export PNG */}
        <button
          onClick={handleExportPng}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-colors hover:bg-white/10"
          style={{ color: isDark ? '#94a3b8' : '#475569' }}
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          PNG
        </button>

        {/* Export JSON */}
        <button
          onClick={handleExportJson}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-colors hover:bg-white/10"
          style={{ color: isDark ? '#94a3b8' : '#475569' }}
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          JSON
        </button>
      </div>

      {/* Empty state */}
      {nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
          <div className="text-center">
            <p className="text-slate-500 text-sm mb-2">No nodes yet</p>
            <p className="text-slate-600 text-xs">Click the + button to add your first node</p>
          </div>
        </div>
      )}

      {/* ReactFlow canvas */}
      <div ref={reactFlowWrapper} className="flex-1 w-full h-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeDragStop={onNodeDragStop}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          proOptions={{ hideAttribution: true }}
          style={{ background: bgColor }}
        >
          <Background
            variant={BackgroundVariant.Dots}
            gap={24}
            size={1.5}
            color={gridColor}
          />
          <Controls
            style={{
              background: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(255,255,255,0.9)',
              border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
              borderRadius: '12px',
            }}
          />
          <MiniMap
            position="bottom-right"
            nodeColor={minimapNodeColor}
            maskColor={isDark ? 'rgba(10,10,15,0.8)' : 'rgba(248,250,252,0.8)'}
            style={{
              background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.9)',
              border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
              borderRadius: '12px',
            }}
          />
        </ReactFlow>
      </div>

      {/* FAB */}
      <motion.button
        whileHover={{ scale: 1.07 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setDrawerOpen(true)}
        className="absolute bottom-8 right-8 w-14 h-14 rounded-full bg-indigo-600 hover:bg-indigo-500 shadow-2xl flex items-center justify-center z-20 transition-colors"
        style={{ boxShadow: '0 4px 20px rgba(99,102,241,0.5)' }}
      >
        <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
        </svg>
      </motion.button>

      {/* Slide-in drawer */}
      <AnimatePresence>
        {drawerOpen && (
          <>
            <motion.div
              className="absolute inset-0 z-30"
              style={{ background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(2px)' }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setDrawerOpen(false)}
            />
            <motion.div
              className="absolute right-0 top-0 bottom-0 w-80 z-40 flex flex-col"
              style={{
                background: isDark ? 'rgba(15,15,26,0.97)' : 'rgba(255,255,255,0.97)',
                backdropFilter: 'blur(20px)',
                borderLeft: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
              }}
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 350 }}
            >
              <div className="flex items-center justify-between p-5 border-b" style={{ borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)' }}>
                <h3 className="font-semibold" style={{ color: isDark ? '#f8fafc' : '#0f172a' }}>Add Node</h3>
                <button
                  onClick={() => setDrawerOpen(false)}
                  className="w-8 h-8 flex items-center justify-center rounded-lg transition-colors hover:bg-white/10"
                >
                  <svg className="w-4 h-4" style={{ color: isDark ? '#94a3b8' : '#64748b' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={handleAddNode} className="flex-1 flex flex-col p-5 gap-4">
                <div>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: isDark ? '#94a3b8' : '#64748b' }}>
                    Node title
                  </label>
                  <input
                    type="text"
                    value={newNodeTitle}
                    onChange={(e) => setNewNodeTitle(e.target.value)}
                    placeholder="Enter node title…"
                    autoFocus
                    required
                    className="w-full px-3 py-2.5 rounded-xl text-sm transition-colors"
                    style={{
                      background: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)',
                      border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                      color: isDark ? '#f8fafc' : '#0f172a',
                      outline: 'none',
                    }}
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: isDark ? '#94a3b8' : '#64748b' }}>
                    Parent node (optional)
                  </label>
                  <select
                    value={newNodeParent}
                    onChange={(e) => setNewNodeParent(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-xl text-sm transition-colors"
                    style={{
                      background: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)',
                      border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                      color: isDark ? '#f8fafc' : '#0f172a',
                      outline: 'none',
                    }}
                  >
                    <option value="">No parent (root node)</option>
                    {rawNodes.map((n) => (
                      <option key={n.id} value={n.id}>{n.text}</option>
                    ))}
                  </select>
                </div>

                <div className="mt-auto">
                  <motion.button
                    whileTap={{ scale: 0.97 }}
                    type="submit"
                    disabled={creating || !newNodeTitle.trim()}
                    className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl font-semibold text-sm transition-colors flex items-center justify-center gap-2"
                  >
                    {creating ? (
                      <span className="w-4 h-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                        </svg>
                        Add Node
                      </>
                    )}
                  </motion.button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

// ───────────────────── page wrapper (provides ReactFlow context) ────

export default function MindMap() {
  const { mapId } = useParams<{ mapId: string }>();
  const navigate = useNavigate();

  useEffect(() => {
    if (!mapId) navigate('/mind-mapper');
  }, [mapId, navigate]);

  if (!mapId) return null;

  return (
    <>
      <style>{`
        @keyframes edgeDash {
          from { stroke-dashoffset: 18; }
          to   { stroke-dashoffset: 0; }
        }
        .react-flow__controls button {
          background: transparent !important;
          border-bottom: 1px solid rgba(255,255,255,0.08) !important;
          color: #94a3b8;
        }
        .react-flow__controls button:hover {
          background: rgba(255,255,255,0.08) !important;
        }
        .react-flow__controls button svg {
          fill: #94a3b8;
        }
      `}</style>
      <div className="flex h-screen overflow-hidden">
        <ReactFlowProvider>
          <MindMapCanvas mapId={mapId} />
        </ReactFlowProvider>
      </div>
    </>
  );
}
