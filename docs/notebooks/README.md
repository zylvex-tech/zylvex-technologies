# Zylvex Technologies — Analytics & Visualization Notebooks

Production-quality interactive Jupyter notebooks for visualizing Spatial Canvas anchor data, Mind Mapper knowledge graphs, and BCI focus sessions. All notebooks use dark-themed Plotly charts (`plotly_dark`), generate their own synthetic data, and include interactive sandbox sections powered by `ipywidgets`.

---

## Notebooks

| Notebook | Description | Export |
|----------|-------------|--------|
| [`spatial_canvas_3d.ipynb`](spatial_canvas_3d.ipynb) | 200 anchors across Lagos, Nairobi, London, São Paulo — 2D Folium clustered map, 3D Plotly scatter, animated timeline, analytics bar/pie/time-series, interactive sandbox | `exports/spatial_canvas_3d.html` |
| [`mind_map_3d.ipynb`](mind_map_3d.ipynb) | 25-node hierarchical mind map — NetworkX graph, 3D spring layout, focus-colored network visualization, session timeline, BCI heatmap, layout/color sandbox | `exports/mind_map_3d.html` |
| [`bci_focus_analysis.ipynb`](bci_focus_analysis.ipynb) | 5 synthetic BCI sessions (600 pts each) — multi-session overlay, rolling average + peak detection, 3D focus surface, violin distributions, focus-vs-creation correlation | `exports/bci_focus_analysis.html` |

### Legacy Notebooks

| Notebook | Description |
|----------|-------------|
| [`mind_map_3d_visualization.ipynb`](mind_map_3d_visualization.ipynb) | Original 3D mind map visualization (superseded by `mind_map_3d.ipynb`) |
| [`spatial_canvas_analytics.ipynb`](spatial_canvas_analytics.ipynb) | Original spatial analytics notebook (superseded by `spatial_canvas_3d.ipynb`) |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch & run

```bash
jupyter notebook
```

Then open any `.ipynb` file and select **Kernel → Restart & Run All**. All data is generated inline — no external files or APIs required.

---

## Exports

Each notebook exports its primary 3D visualization as a standalone HTML file to the `exports/` directory:

| File | Source Notebook |
|------|---------------|
| `exports/spatial_canvas_3d.html` | Spatial Canvas 3D scatter |
| `exports/mind_map_3d.html` | Mind Map 3D network graph |
| `exports/bci_focus_analysis.html` | BCI 3D focus surface |

These HTML files are fully self-contained and can be opened in any browser or embedded in other pages.

---

## Requirements

```
networkx>=3.0
plotly>=5.0
numpy>=1.24
scipy>=1.10
folium>=0.14
pandas>=2.0
ipywidgets>=8.0
jupyter>=1.0
```

---

## Sandbox Sections

Each notebook ends with a **🎛️ Sandbox** section that uses `ipywidgets` sliders and dropdowns:

- **Spatial Canvas**: radius_km (1–50), min_reactions (0–100), city filter dropdown — re-renders 3D scatter and category chart
- **Mind Map**: focus_threshold (0–100), layout algorithm (spring/circular/kamada_kawai), color scheme (focus/depth/recency) — re-renders 3D network graph
- **BCI Focus**: smoothing_window (5–60), peak_threshold (1–20), session selector — re-renders rolling average chart with peaks

> **Note:** ipywidgets interactive controls require Jupyter Notebook or JupyterLab. They will not render in static HTML exports or GitHub's notebook preview.
