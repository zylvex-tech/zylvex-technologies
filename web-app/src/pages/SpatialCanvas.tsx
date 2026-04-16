import { useState, useEffect, useCallback, useRef } from 'react';
import { MapContainer, TileLayer, Marker, useMap } from 'react-leaflet';
import L from 'leaflet';
import { motion, AnimatePresence } from 'framer-motion';
import { getAnchorsNearby, createAnchor } from '../api/anchors';
import { ApiError } from '../api/client';
import type { AnchorResponse, AnchorCreate } from '../api/types';
import { useGeolocation } from '../hooks/useGeolocation';
import AppShell from '../components/AppShell';
import PageTransition from '../components/PageTransition';
import Modal from '../components/Modal';
import { useToast } from '../components/Toast';

const createAnchorIcon = () =>
  L.divIcon({
    html: '<div class="anchor-pin"></div>',
    className: '',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });

function MapController({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lng], 14);
  }, [map, lat, lng]);
  return null;
}

function formatCoords(lat: number, lng: number): string {
  return `${lat.toFixed(5)}°, ${lng.toFixed(5)}°`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

const CONTENT_TYPES = ['text', 'image', 'video', 'audio', 'link'];

export default function SpatialCanvas() {
  const geo = useGeolocation();
  const [anchors, setAnchors] = useState<AnchorResponse[]>([]);
  const [selectedAnchor, setSelectedAnchor] = useState<AnchorResponse | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [anchorsLoading, setAnchorsLoading] = useState(false);
  const [mapCenter, setMapCenter] = useState<[number, number] | null>(null);
  const { showToast } = useToast();
  const anchorIcon = useRef(createAnchorIcon());

  const [form, setForm] = useState<AnchorCreate>({
    title: '',
    content: '',
    content_type: 'text',
    latitude: 0,
    longitude: 0,
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchAnchors = useCallback(
    async (lat: number, lng: number) => {
      setAnchorsLoading(true);
      try {
        const result = await getAnchorsNearby(lat, lng, 5);
        setAnchors(result.anchors);
      } catch (err) {
        showToast(err instanceof ApiError ? err.message : 'Failed to load anchors', 'error');
      } finally {
        setAnchorsLoading(false);
      }
    },
    [showToast],
  );

  useEffect(() => {
    if (!geo.loading && geo.latitude && geo.longitude) {
      const center: [number, number] = [geo.latitude, geo.longitude];
      setMapCenter(center);
      setForm((f) => ({ ...f, latitude: geo.latitude!, longitude: geo.longitude! }));
      fetchAnchors(geo.latitude, geo.longitude);
    }
  }, [geo.loading, geo.latitude, geo.longitude, fetchAnchors]);

  const handleAnchorClick = (anchor: AnchorResponse) => {
    setSelectedAnchor(anchor);
    setDrawerOpen(true);
  };

  const handleCreateAnchor = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const anchor = await createAnchor(form);
      setAnchors((prev) => [anchor, ...prev]);
      setModalOpen(false);
      setForm((f) => ({ ...f, title: '', content: '' }));
      showToast('Anchor placed!', 'success');
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Failed to place anchor', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const defaultCenter: [number, number] = mapCenter ?? [40.7128, -74.006];

  return (
    <PageTransition>
      <AppShell>
        <div className="relative h-full flex flex-col">
          {/* Header */}
          <div className="px-6 py-4 border-b border-white/8 flex items-center justify-between bg-[#0a0a0f]/80 backdrop-blur-sm z-10">
            <div>
              <h1 className="text-lg font-bold text-slate-100">Spatial Canvas</h1>
              <p className="text-xs text-slate-500">
                {anchorsLoading
                  ? 'Loading anchors...'
                  : `${anchors.length} anchors within 5km`}
              </p>
            </div>
            {geo.loading && (
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <span className="w-4 h-4 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
                Locating...
              </div>
            )}
            {geo.error && (
              <p className="text-xs text-red-400">{geo.error}</p>
            )}
          </div>

          {/* Map */}
          <div className="flex-1 relative">
            <MapContainer
              center={defaultCenter}
              zoom={13}
              style={{ width: '100%', height: '100%' }}
              zoomControl={false}
            >
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                subdomains="abcd"
                maxZoom={19}
              />
              {mapCenter && <MapController lat={mapCenter[0]} lng={mapCenter[1]} />}
              {anchors.map((anchor) => (
                <Marker
                  key={anchor.id}
                  position={[anchor.latitude, anchor.longitude]}
                  icon={anchorIcon.current}
                  eventHandlers={{ click: () => handleAnchorClick(anchor) }}
                />
              ))}
            </MapContainer>

            {/* FAB */}
            <motion.button
              whileTap={{ scale: 0.95 }}
              whileHover={{ scale: 1.05 }}
              onClick={() => setModalOpen(true)}
              className="absolute bottom-6 right-6 z-[1000] w-14 h-14 rounded-full bg-indigo-600 hover:bg-indigo-500 flex items-center justify-center shadow-2xl glow-primary transition-colors"
            >
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
            </motion.button>
          </div>

          {/* Anchor detail drawer */}
          <AnimatePresence>
            {drawerOpen && selectedAnchor && (
              <motion.div
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                transition={{ type: 'spring', damping: 28, stiffness: 300 }}
                className="absolute top-0 right-0 h-full w-80 z-[1001] glass-dark border-l border-white/10 flex flex-col"
              >
                <div className="flex items-center justify-between p-5 border-b border-white/8">
                  <h3 className="text-slate-100 font-semibold">Anchor Details</h3>
                  <button
                    onClick={() => setDrawerOpen(false)}
                    className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/10 transition-colors"
                  >
                    <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto p-5 space-y-5">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-0.5 bg-indigo-500/20 border border-indigo-500/30 rounded-full text-xs text-indigo-300 font-medium">
                        {selectedAnchor.content_type}
                      </span>
                    </div>
                    <h2 className="text-xl font-bold text-slate-100">{selectedAnchor.title}</h2>
                  </div>

                  <div className="glass-sm p-4">
                    <p className="text-xs font-medium text-slate-400 mb-2">Content</p>
                    <p className="text-sm text-slate-300 leading-relaxed">{selectedAnchor.content}</p>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <p className="text-xs font-medium text-slate-500 mb-1">Coordinates</p>
                      <p className="text-sm text-slate-300 font-mono">
                        {formatCoords(selectedAnchor.latitude, selectedAnchor.longitude)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-slate-500 mb-1">Placed</p>
                      <p className="text-sm text-slate-300">{formatDate(selectedAnchor.created_at)}</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Create anchor modal */}
        <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Place Anchor">
          <form onSubmit={handleCreateAnchor} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-2">Title</label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                required
                placeholder="Anchor title"
                className="w-full px-4 py-3 bg-white/6 border border-white/10 rounded-xl text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/60 transition-colors text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-2">Content type</label>
              <select
                value={form.content_type}
                onChange={(e) => setForm({ ...form, content_type: e.target.value })}
                className="w-full px-4 py-3 bg-white/6 border border-white/10 rounded-xl text-slate-200 focus:outline-none focus:border-indigo-500/60 transition-colors text-sm"
              >
                {CONTENT_TYPES.map((t) => (
                  <option key={t} value={t} className="bg-[#0f0f1a]">{t}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-2">Content</label>
              <textarea
                value={form.content}
                onChange={(e) => setForm({ ...form, content: e.target.value })}
                required
                rows={3}
                placeholder="What do you want to anchor here?"
                className="w-full px-4 py-3 bg-white/6 border border-white/10 rounded-xl text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/60 transition-colors text-sm resize-none"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2">Latitude</label>
                <input
                  type="number"
                  step="any"
                  value={form.latitude}
                  onChange={(e) => setForm({ ...form, latitude: parseFloat(e.target.value) })}
                  required
                  className="w-full px-4 py-3 bg-white/6 border border-white/10 rounded-xl text-slate-200 focus:outline-none focus:border-indigo-500/60 transition-colors text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2">Longitude</label>
                <input
                  type="number"
                  step="any"
                  value={form.longitude}
                  onChange={(e) => setForm({ ...form, longitude: parseFloat(e.target.value) })}
                  required
                  className="w-full px-4 py-3 bg-white/6 border border-white/10 rounded-xl text-slate-200 focus:outline-none focus:border-indigo-500/60 transition-colors text-sm"
                />
              </div>
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="flex-1 py-2.5 glass-sm hover:bg-white/10 text-slate-300 rounded-xl text-sm font-medium transition-colors"
              >
                Cancel
              </button>
              <motion.button
                whileTap={{ scale: 0.97 }}
                type="submit"
                disabled={submitting}
                className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white rounded-xl text-sm font-semibold transition-colors flex items-center justify-center"
              >
                {submitting ? (
                  <span className="w-4 h-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                ) : 'Place Anchor'}
              </motion.button>
            </div>
          </form>
        </Modal>
      </AppShell>
    </PageTransition>
  );
}
