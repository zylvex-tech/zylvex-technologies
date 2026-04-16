# Zylvex Technologies — Analytics Notebooks

Interactive Jupyter notebooks for visualizing Mind Mapper and Spatial Canvas data.

---

## Notebooks

| Notebook | Description |
|----------|-------------|
| [`mind_map_3d_visualization.ipynb`](mind_map_3d_visualization.ipynb) | 3D interactive mind map graph using Plotly + NetworkX spring layout |
| [`bci_focus_analysis.ipynb`](bci_focus_analysis.ipynb) | BCI focus session analysis: time-series, peaks, heatmaps, 3D surface |
| [`spatial_canvas_analytics.ipynb`](spatial_canvas_analytics.ipynb) | Spatial anchor analytics: Folium map, heatmap, bar charts, 3D scatter |

---

## Quick Start

### 1. Install dependencies

```bash
pip install networkx plotly numpy scipy folium ipywidgets jupyter
```

Or install from the requirements file:

```bash
pip install -r requirements.txt
```

### 2. Launch Jupyter

```bash
jupyter notebook
```

Then open any of the `.ipynb` files from the browser UI.

### 3. Run all cells

In each notebook, select **Kernel → Restart & Run All** to execute every cell from top to bottom. All sample data is hardcoded — no external files or APIs required.

---

## Requirements

```
networkx>=3.0
plotly>=5.0
numpy>=1.24
scipy>=1.10
folium>=0.14
ipywidgets>=8.0
jupyter>=1.0
```

---

## Sandbox Sections

Each notebook ends with a **🎛️ Sandbox** section that uses `ipywidgets` sliders and dropdowns. These controls let you:

- Adjust focus score thresholds to filter nodes or BCI data
- Change rolling average window sizes
- Select sessions, categories, or date ranges
- Re-render charts live without rerunning the entire notebook

> **Note:** ipywidgets interactive controls require Jupyter Notebook or JupyterLab. They will not render in static HTML exports or GitHub's notebook preview.

---

## Exporting

Each notebook includes cells to export visualizations:

- **Plotly charts** → standalone HTML via `fig.write_html("output.html")`
- **Folium maps** → standalone HTML via `map.save("output.html")`

Exported HTML files are self-contained and can be shared or embedded anywhere.
