# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "matplotlib==3.10.8",
#     "pandas==3.0.0",
#     "pymde>=0.3.0",
#     "numpy",
#     "pillow",
#     "plotly",
# ]
# ///

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="full")

@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np
    import os
    from PIL import Image
    return Image, go, mo, np, os, pd, plt, px

@app.cell
def _(mo):
    csv_path_input = mo.ui.text(
        label="CSV file",
        value="/workspaces/dev_container_template/data/boss_chip_features_clusters_chip_bmr_merged.csv",
        full_width=True,
    )
    image_dir_input = mo.ui.text(
        label="Image directory",
        value="/workspaces/dev_container_template/data/images_boss",
        full_width=True,
    )
    mo.sidebar(
        mo.vstack([
            csv_path_input,
            image_dir_input,
        ])
    )
    return csv_path_input, image_dir_input


@app.cell
def _(csv_path_input, image_dir_input, mo, os, pd):
    mo.stop(
        not csv_path_input.value or not os.path.isfile(csv_path_input.value),
        mo.md(f"**CSV file not found:** `{csv_path_input.value}`"),
    )
    mo.stop(
        not image_dir_input.value or not os.path.isdir(image_dir_input.value),
        mo.md(f"**Directory not found:** `{image_dir_input.value}`"),
    )

    df = pd.read_csv(csv_path_input.value)
    image_base_path = image_dir_input.value
    return df, image_base_path


@app.cell
def _(df, mo, pd):
    mo.stop(
        "image_name" not in df.columns,
        mo.md("**CSV must contain a `image_name` column.**"),
    )

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    mo.stop(
        len(numeric_cols) < 2,
        mo.md("**CSV must contain at least two numeric columns for the scatter plot.**"),
    )

    _default_x = "umap_0" if "umap_0" in numeric_cols else numeric_cols[0]
    _default_y = "umap_1" if "umap_1" in numeric_cols else numeric_cols[1]

    x_col_dropdown = mo.ui.dropdown(options=numeric_cols, value=_default_x, label="X axis")
    y_col_dropdown = mo.ui.dropdown(options=numeric_cols, value=_default_y, label="Y axis")
    z_col_dropdown = mo.ui.dropdown(options=["None"] + numeric_cols, value="None", label="Z axis")

    color_options = [c for c in df.columns if c != "image_name"]
    _default_color = "Alt1_Code" if "Alt1_Code" in color_options else "None"
    color_dropdown = mo.ui.dropdown(
        options=["None"] + color_options,
        value=_default_color,
        label="Colour by",
    )
    filter_col_dropdown = mo.ui.dropdown(
        options=["None"] + numeric_cols,
        value="None",
        label="Filter by",
    )
    _table_col_options = [c for c in df.columns if not c.startswith("feat_") and c != "image_name"]
    _default_table_cols = [c for c in ["holeid", "Au_ppm", "cluster", "Lith1_Code", "Alt1_Code"] if c in _table_col_options]
    table_cols_multiselect = mo.ui.multiselect(
        options=_table_col_options,
        value=_default_table_cols or _table_col_options,
        label="Table columns",
    )
    import re as _re
    _hex_pat = _re.compile(r'^#[0-9a-fA-F]{6}$')
    hex_cols = [c for c in df.columns if df[c].dropna().astype(str).str.match(_hex_pat).all() and df[c].notna().any()]
    hex_col_dropdown = mo.ui.dropdown(options=hex_cols, value=hex_cols[0] if hex_cols else None, label="Hex colour column")
    use_hex_toggle = mo.ui.switch(label="Use actual hex colour", value=False)
    return color_dropdown, filter_col_dropdown, hex_col_dropdown, hex_cols, table_cols_multiselect, use_hex_toggle, x_col_dropdown, y_col_dropdown, z_col_dropdown


@app.cell
def _(color_dropdown, filter_col_dropdown, filter_max, filter_min, filter_slider, hex_col_dropdown, hex_cols, mo, table_cols_multiselect, use_hex_toggle, x_col_dropdown, y_col_dropdown, z_col_dropdown):
    _sidebar_items = [
        x_col_dropdown, y_col_dropdown, z_col_dropdown,
        color_dropdown,
    ]
    if hex_cols:
        _sidebar_items.append(use_hex_toggle)
        _sidebar_items.append(hex_col_dropdown)
    _sidebar_items.append(filter_col_dropdown)
    if filter_slider is not None:
        _sidebar_items.append(filter_slider)
        _sidebar_items.append(mo.hstack([filter_min, filter_max], gap=1))
    _sidebar_items.append(table_cols_multiselect)
    mo.sidebar(mo.vstack(_sidebar_items))
    return


@app.cell
def _(df, filter_col_dropdown, mo, pd):
    if filter_col_dropdown.value != "None":
        _col = df[filter_col_dropdown.value].dropna()
        _min_v = float(_col.min())
        _max_v = float(_col.max())
        _is_int_col = pd.api.types.is_integer_dtype(_col) or bool((_col == _col.round()).all())
        _step_r = 1 if _is_int_col else max(round((_max_v - _min_v) / 1000, 6), 1e-6)
        filter_slider = mo.ui.range_slider(
            start=_min_v, stop=_max_v,
            step=_step_r,
            value=[_min_v, _max_v],
            label=filter_col_dropdown.value,
            full_width=True,
        )
        filter_min = mo.ui.number(
            start=_min_v, stop=_max_v, step=_step_r,
            value=_min_v, label="Min",
        )
        filter_max = mo.ui.number(
            start=_min_v, stop=_max_v, step=_step_r,
            value=_max_v, label="Max",
        )
    else:
        filter_slider = None
        filter_min = None
        filter_max = None
    return filter_max, filter_min, filter_slider


@app.cell
def _(mo):
    get_selection, set_selection = mo.state([])
    get_nav_pos, set_nav_pos = mo.state(0)  # tracks current page index
    return get_nav_pos, get_selection, set_nav_pos, set_selection


@app.cell
def _(color_dropdown, df, filter_col_dropdown, filter_max, filter_min, filter_slider, go, hex_col_dropdown, mo, np, pd, use_hex_toggle, x_col_dropdown, y_col_dropdown, z_col_dropdown):
    _x_col = x_col_dropdown.value
    _y_col = y_col_dropdown.value
    _z_col = z_col_dropdown.value
    _color_col = color_dropdown.value
    _fig = go.Figure()

    # ── Filter mask ───────────────────────────────────────────────────────────
    # Points excluded by the filter are simply not rendered; customdata on every
    # plotted point stores its original df row index so lasso selections always
    # map back to the right rows regardless of filtering or multi-trace colour.
    _filter_mask = np.ones(len(df), dtype=bool)
    if filter_col_dropdown.value != "None" and filter_slider is not None:
        _fc = df[filter_col_dropdown.value].values.astype(float)
        # Intersection of slider range and typed min/max — either control can
        # restrict independently; both at defaults means no restriction.
        _lo = max(filter_slider.value[0], filter_min.value)
        _hi = min(filter_slider.value[1], filter_max.value)
        _filter_mask = np.isfinite(_fc) & (_fc >= _lo) & (_fc <= _hi)

    _orig_idx = np.where(_filter_mask)[0]   # plot position → original df row index
    _x = df[_x_col].values[_filter_mask]
    _y = df[_y_col].values[_filter_mask]

    # ── Color pre-computation (from full dataset for a consistent scale) ──────
    _is_cat = False
    _cats = []
    _color_vals = None      # full-length array; sliced with filter mask below
    _cb = dict(title=_color_col)
    _colorscale = "viridis"
    _col = None
    _col_filt = None        # filtered category column for per-trace masking

    if _color_col != "None":
        _col = df[_color_col]
        _col_nn = _col.dropna()
        _is_cat = _col.dtype.kind not in ('f', 'i', 'u') or _col.nunique() < 20

        if _is_cat:
            _cats = [
                int(c) if isinstance(c, float) and c.is_integer() else c
                for c in sorted(_col_nn.unique())
            ]
            _col_filt = _col.values[_filter_mask]
            _nan_m = pd.isna(_col_filt)
        else:
            _raw = _col.values.astype(float)
            _nonneg = bool((_col_nn >= 0).all())
            _max_v = float(_col_nn.max())
            _p90 = float(_col_nn.quantile(0.9))
            if _nonneg and _p90 > 0 and _max_v / _p90 > 10:
                _color_vals = np.where(
                    np.isnan(_raw), np.nan, np.log1p(np.maximum(_raw, 0))
                )
                _pos = _col_nn[_col_nn > 0]
                _min_p = float(_pos.min()) if len(_pos) else 1.0
                _tick_orig = sorted(set(
                    float(f"{t:.3g}")
                    for t in [0.0] + list(np.geomspace(_min_p, _max_v, 5))
                ))
                _cb = dict(
                    title=f"{_color_col} (log scale)",
                    tickvals=list(np.log1p(_tick_orig)),
                    ticktext=[str(t) for t in _tick_orig],
                )
            else:
                _color_vals = _raw
            _cv_filt = _color_vals[_filter_mask]
            _nan_m = np.isnan(_cv_filt)

    # ── Hex colour override ───────────────────────────────────────────────────
    # When enabled, all points are drawn in a single trace using the per-row hex
    # colour values directly, bypassing the legend colour scheme entirely.
    _use_hex = use_hex_toggle.value and hex_col_dropdown.value is not None
    if _use_hex:
        _hex_vals = df[hex_col_dropdown.value].values[_filter_mask]
        # Fall back to grey for any missing hex values
        _hex_vals = np.where(pd.isna(_hex_vals), "#bbbbbb", _hex_vals)

    # ── 2D / 3D branch ───────────────────────────────────────────────────────
    # idx_map[i] = 1-D array of original df row indices for trace i.
    # Used downstream to map (curveNumber, pointIndex) → df row without
    # relying on customdata, which Marimo may strip when re-extracting points.
    _sel_m = dict(opacity=1.0, size=10)
    _unsel_m = dict(opacity=0.15, size=5)
    idx_map = []

    if _z_col != "None":
        # 3D — lasso selection not available in Plotly 3D.
        _z = df[_z_col].values[_filter_mask]
        if _color_col == "None":
            _c = list(_hex_vals) if _use_hex else "steelblue"
            _fig.add_trace(go.Scatter3d(
                x=_x, y=_y, z=_z, mode="markers",
                marker=dict(size=3, opacity=0.7, color=_c),
                customdata=_orig_idx, showlegend=False,
            ))
            idx_map.append(_orig_idx)
        elif _is_cat:
            for _cat in _cats:
                _m = _col_filt == _cat
                if not _m.any():
                    continue
                _mk = dict(size=3, opacity=0.7)
                if _use_hex:
                    _mk["color"] = list(_hex_vals[_m])
                _fig.add_trace(go.Scatter3d(
                    x=_x[_m], y=_y[_m], z=_z[_m], mode="markers",
                    marker=_mk, customdata=_orig_idx[_m], name=str(_cat),
                ))
                idx_map.append(_orig_idx[_m])
            if _nan_m.any():
                _nan_c = list(_hex_vals[_nan_m]) if _use_hex else "#bbbbbb"
                _fig.add_trace(go.Scatter3d(
                    x=_x[_nan_m], y=_y[_nan_m], z=_z[_nan_m], mode="markers",
                    marker=dict(size=3, opacity=0.5, color=_nan_c),
                    customdata=_orig_idx[_nan_m], name="NaN",
                ))
                idx_map.append(_orig_idx[_nan_m])
        else:
            _main_mk = dict(size=3, opacity=0.7,
                            color=list(_hex_vals[~_nan_m]) if _use_hex else _cv_filt[~_nan_m])
            if not _use_hex:
                _main_mk.update(colorscale=_colorscale, colorbar=_cb)
            _fig.add_trace(go.Scatter3d(
                x=_x[~_nan_m], y=_y[~_nan_m], z=_z[~_nan_m], mode="markers",
                marker=_main_mk, customdata=_orig_idx[~_nan_m], showlegend=False,
            ))
            idx_map.append(_orig_idx[~_nan_m])
            if _nan_m.any():
                _nan_c = list(_hex_vals[_nan_m]) if _use_hex else "#bbbbbb"
                _fig.add_trace(go.Scatter3d(
                    x=_x[_nan_m], y=_y[_nan_m], z=_z[_nan_m], mode="markers",
                    marker=dict(size=3, opacity=0.5, color=_nan_c),
                    customdata=_orig_idx[_nan_m], name="NaN",
                ))
                idx_map.append(_orig_idx[_nan_m])
        _fig.update_layout(
            scene=dict(xaxis_title=_x_col, yaxis_title=_y_col, zaxis_title=_z_col),
            uirevision=f"{_x_col}|{_y_col}|{_z_col}|{_color_col}",
            height=600, margin=dict(l=0, r=0, t=20, b=0),
        )
    else:
        # 2D — same trace structure whether hex mode is on or off so that
        # uirevision stays constant and Plotly legend state is preserved.
        if _color_col == "None":
            _c = list(_hex_vals) if _use_hex else "steelblue"
            _fig.add_trace(go.Scattergl(
                x=_x, y=_y, mode="markers",
                marker=dict(size=6, opacity=0.7, color=_c),
                selected=dict(marker=_sel_m), unselected=dict(marker=_unsel_m),
                customdata=_orig_idx, showlegend=False,
            ))
            idx_map.append(_orig_idx)
        elif _is_cat:
            for _cat in _cats:
                _m = _col_filt == _cat
                if not _m.any():
                    continue
                _mk = dict(size=6, opacity=0.7)
                if _use_hex:
                    _mk["color"] = list(_hex_vals[_m])
                _fig.add_trace(go.Scattergl(
                    x=_x[_m], y=_y[_m], mode="markers",
                    marker=_mk,
                    selected=dict(marker=_sel_m), unselected=dict(marker=_unsel_m),
                    customdata=_orig_idx[_m], name=str(_cat),
                ))
                idx_map.append(_orig_idx[_m])
            if _nan_m.any():
                _nan_c = list(_hex_vals[_nan_m]) if _use_hex else "#bbbbbb"
                _nan_sel = dict(marker=_sel_m) if _use_hex else dict(marker=dict(opacity=1.0, size=10, color="#bbbbbb"))
                _nan_unsel = dict(marker=_unsel_m) if _use_hex else dict(marker=dict(opacity=0.15, size=5, color="#bbbbbb"))
                _fig.add_trace(go.Scattergl(
                    x=_x[_nan_m], y=_y[_nan_m], mode="markers",
                    marker=dict(size=6, opacity=0.5, color=_nan_c),
                    selected=_nan_sel, unselected=_nan_unsel,
                    customdata=_orig_idx[_nan_m], name="NaN",
                ))
                idx_map.append(_orig_idx[_nan_m])
        else:
            _main_mk = dict(size=6, opacity=0.7,
                            color=list(_hex_vals[~_nan_m]) if _use_hex else _cv_filt[~_nan_m])
            if not _use_hex:
                _main_mk.update(colorscale=_colorscale, colorbar=_cb)
            _fig.add_trace(go.Scattergl(
                x=_x[~_nan_m], y=_y[~_nan_m], mode="markers",
                marker=_main_mk,
                selected=dict(marker=_sel_m), unselected=dict(marker=_unsel_m),
                customdata=_orig_idx[~_nan_m], showlegend=False,
            ))
            idx_map.append(_orig_idx[~_nan_m])
            if _nan_m.any():
                _nan_c = list(_hex_vals[_nan_m]) if _use_hex else "#bbbbbb"
                _nan_sel = dict(marker=_sel_m) if _use_hex else dict(marker=dict(opacity=1.0, size=10, color="#bbbbbb"))
                _nan_unsel = dict(marker=_unsel_m) if _use_hex else dict(marker=dict(opacity=0.15, size=5, color="#bbbbbb"))
                _fig.add_trace(go.Scattergl(
                    x=_x[_nan_m], y=_y[_nan_m], mode="markers",
                    marker=dict(size=6, opacity=0.5, color=_nan_c),
                    selected=_nan_sel, unselected=_nan_unsel,
                    customdata=_orig_idx[_nan_m], name="NaN",
                ))
                idx_map.append(_orig_idx[_nan_m])
        # Axis ranges from the full dataset so they don't shift as filter moves.
        _x_full = df[_x_col].values
        _y_full = df[_y_col].values
        _x_pad = (_x_full.max() - _x_full.min()) * 0.05 or 1.0
        _y_pad = (_y_full.max() - _y_full.min()) * 0.05 or 1.0
        _fig.update_layout(
            dragmode="lasso",
            xaxis=dict(title=_x_col, range=[_x_full.min() - _x_pad, _x_full.max() + _x_pad], autorange=False),
            yaxis=dict(title=_y_col, range=[_y_full.min() - _y_pad, _y_full.max() + _y_pad], autorange=False),
            uirevision=f"{_x_col}|{_y_col}|{_color_col}",
            height=600, margin=dict(l=40, r=20, t=20, b=40),
        )

    plot = mo.ui.plotly(_fig)
    return idx_map, plot


@app.cell
def _(df, idx_map, np, pd, plot, set_nav_pos, set_selection, x_col_dropdown, y_col_dropdown):
    indices = np.arange(len(df))

    df_plot = pd.DataFrame(
        {
            "index": indices,
            "x": df[x_col_dropdown.value].values,
            "y": df[y_col_dropdown.value].values,
            "image_name": df["image_name"],
        }
    )

    # Use idx_map[curveNumber][pointIndex] to resolve original df row indices.
    # This is robust: Marimo strips customdata when re-extracting points from
    # a range selection, but curveNumber/pointIndex are always present.
    if len(plot.indices):
        _use_indices = list(plot.indices)  # last-resort fallback (trace-local, wrong after filter)
        _points = plot.value              # list[dict] from Marimo
        if isinstance(_points, list) and _points:
            try:
                _from_map = []
                for _p in _points:
                    _curve = _p.get("curveNumber", 0)
                    _pt    = _p.get("pointIndex")
                    if _pt is not None and isinstance(_curve, int) and 0 <= _curve < len(idx_map):
                        _arr = idx_map[_curve]
                        if 0 <= _pt < len(_arr):
                            _from_map.append(int(_arr[_pt]))
                if _from_map:
                    _use_indices = _from_map
            except (KeyError, TypeError, ValueError, IndexError):
                pass
        set_selection(_use_indices)
        set_nav_pos(0)
    return (df_plot,)


@app.cell
def _(get_nav_pos, get_selection, mo, set_nav_pos, set_selection):
    _IMAGES_PER_PAGE = 8
    selected_indices = get_selection()
    if len(selected_indices):
        _total_pages = (len(selected_indices) - 1) // _IMAGES_PER_PAGE + 1
        def _go_prev(v):
            set_nav_pos((get_nav_pos() - 1) % _total_pages)
            return v + 1
        def _go_next(v):
            set_nav_pos((get_nav_pos() + 1) % _total_pages)
            return v + 1
        def _clear(v):
            set_selection([])
            set_nav_pos(0)
            return v + 1
        prev_btn = mo.ui.button(label="◀ Prev", value=0, on_click=_go_prev)
        next_btn = mo.ui.button(label="Next ▶", value=0, on_click=_go_next)
        clear_btn = mo.ui.button(label="✕ Clear", value=0, on_click=_clear)
        nav_controls = mo.hstack([prev_btn, next_btn, clear_btn], justify="center")
    else:
        nav_controls = mo.md("")
    return nav_controls, selected_indices


@app.cell
def _(Image, df_plot, get_nav_pos, get_selection, image_base_path, mo, os, selected_indices):
    _IMAGES_PER_PAGE = 8

    if not get_selection():
        image_output = mo.md("**Select points on the scatter plot to browse images.**")
    elif len(selected_indices):
        _total_pages = (len(selected_indices) - 1) // _IMAGES_PER_PAGE + 1
        _page = get_nav_pos() % _total_pages
        _page_start = _page * _IMAGES_PER_PAGE
        _page_end = min(_page_start + _IMAGES_PER_PAGE, len(selected_indices))
        _page_indices = selected_indices[_page_start:_page_end]

        _image_cells = []
        for _pi in _page_indices:
            _row = df_plot.iloc[_pi]
            _img = Image.open(os.path.join(image_base_path, _row["image_name"]))
            _image_cells.append(
                mo.vstack([mo.image(_img, width=160), mo.md(f"`{_row['image_name']}`")], align="center")
            )

        image_output = mo.vstack([
            mo.md(f"**Images {_page_start + 1}–{_page_end} of {len(selected_indices)}** (page {_page + 1} of {_total_pages})"),
            mo.hstack(_image_cells, gap=1),
        ])
    else:
        image_output = mo.md("**Select points on the scatter plot to browse images.**")
    return (image_output,)


@app.cell
def _(df, get_nav_pos, get_selection, mo, pd, table_cols_multiselect):
    _IMAGES_PER_PAGE = 8
    _sel = get_selection()
    if len(_sel):
        _show_cols = table_cols_multiselect.value or [c for c in df.columns if not c.startswith("feat_") and c != "image_name"]
        _all_selected = df.iloc[_sel][_show_cols].reset_index(drop=True)
        _page_start = get_nav_pos() * _IMAGES_PER_PAGE
        _page_end = _page_start + _IMAGES_PER_PAGE

        def _highlight(row: str, col: str, value):
            try:
                if _page_start <= int(row) < _page_end:
                    return {"background-color": "#fff3cd"}
            except (ValueError, TypeError):
                pass
            return {}

        data_table = mo.ui.table(
            _all_selected, style_cell=_highlight, selection="single",
            pagination=False,
        )
    else:
        data_table = mo.ui.table(pd.DataFrame(), selection="single", pagination=False)
    return (data_table,)


@app.cell
def _(data_table, set_nav_pos):
    _IMAGES_PER_PAGE = 8
    _selected = data_table.value
    if len(_selected):
        set_nav_pos(int(_selected.index[0]) // _IMAGES_PER_PAGE)
    return


@app.cell
def _(data_table, image_output, mo, nav_controls, plot):
    mo.vstack([
        plot,
        nav_controls,
        image_output,
        data_table
    ], gap=0.5)
    return


if __name__ == "__main__":
    app.run()
