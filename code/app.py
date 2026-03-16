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
    import io
    csv_upload = mo.ui.file(filetypes=[".csv"], label=".csv")
    image_dir_input = mo.ui.text(
        label="Image directory",
        value="/workspaces/dev_container_template/data/SU-671-W1",
        full_width=True,
    )
    mo.sidebar(
        mo.vstack([
            csv_upload,
            image_dir_input,
        ])
    )
    return csv_upload, image_dir_input, io


@app.cell
def _(csv_upload, image_dir_input, io, mo, os, pd):
    mo.stop(
        not csv_upload.value,
        mo.md("**Upload a CSV file above to get started.**"),
    )
    mo.stop(
        not image_dir_input.value or not os.path.isdir(image_dir_input.value),
        mo.md(f"**Directory not found:** `{image_dir_input.value}`"),
    )

    df = pd.read_csv(io.BytesIO(csv_upload.value[0].contents))
    image_base_path = image_dir_input.value
    return df, image_base_path


@app.cell
def _(df, mo, pd):
    mo.stop(
        "file_name" not in df.columns,
        mo.md("**CSV must contain a `file_name` column.**"),
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

    color_options = [c for c in df.columns if c != "file_name"]
    color_dropdown = mo.ui.dropdown(
        options=["None"] + color_options,
        value="None",
        label="Colour by",
    )
    return color_dropdown, x_col_dropdown, y_col_dropdown


@app.cell
def _(color_dropdown, mo, x_col_dropdown, y_col_dropdown):
    mo.sidebar(
        mo.vstack([
            x_col_dropdown,
            y_col_dropdown,
            color_dropdown,
        ])
    )
    return


@app.cell
def _(mo):
    get_highlight, set_highlight = mo.state(None)
    get_selection, set_selection = mo.state([])
    get_current_idx, set_current_idx = mo.state(None)
    get_nav_pos, set_nav_pos = mo.state(0)
    return get_current_idx, get_highlight, get_nav_pos, get_selection, set_current_idx, set_highlight, set_nav_pos, set_selection


@app.cell
def _(color_dropdown, df, get_highlight, get_selection, go, mo, x_col_dropdown, y_col_dropdown):
    _x_col = x_col_dropdown.value
    _y_col = y_col_dropdown.value
    _x = df[_x_col].values
    _y = df[_y_col].values

    _sel = set(get_selection())
    _has_sel = len(_sel) > 0
    _opacities = [1.0 if i in _sel else 0.15 for i in range(len(_x))] if _has_sel else [0.5] * len(_x)
    _sizes = [8 if i in _sel else 5 for i in range(len(_x))] if _has_sel else [5] * len(_x)

    _color_col = color_dropdown.value
    _fig = go.Figure()

    if _color_col == "None":
        _fig.add_trace(go.Scattergl(
            x=_x, y=_y,
            mode="markers",
            marker=dict(size=_sizes, opacity=_opacities, color="steelblue"),
            showlegend=False,
        ))
    else:
        _values = df[_color_col]
        if _values.dtype == "object" or _values.nunique() < 20:
            for _cat in _values.unique():
                _mask = (_values == _cat).values
                _idx = [i for i, m in enumerate(_mask) if m]
                _fig.add_trace(go.Scattergl(
                    x=_x[_mask], y=_y[_mask],
                    mode="markers",
                    marker=dict(
                        size=[_sizes[i] for i in _idx],
                        opacity=[_opacities[i] for i in _idx],
                    ),
                    name=str(_cat),
                ))
        else:
            _fig.add_trace(go.Scattergl(
                x=_x, y=_y,
                mode="markers",
                marker=dict(
                    size=_sizes, opacity=_opacities,
                    color=_values, colorscale="viridis", colorbar=dict(title=_color_col),
                ),
                showlegend=False,
            ))

    _fig.update_layout(
        dragmode="lasso",
        xaxis_title=_x_col,
        yaxis_title=_y_col,
        height=600,
        margin=dict(l=40, r=20, t=20, b=40),
    )

    # Add highlight point if set
    _hl = get_highlight()
    if _hl is not None:
        _fig.add_trace(go.Scatter(
            x=[_hl[0]], y=[_hl[1]],
            mode="markers",
            marker=dict(size=18, color="rgba(0,0,0,0)", line=dict(color="red", width=3)),
            showlegend=False,
            hoverinfo="skip",
        ))

    plot = mo.ui.plotly(_fig)
    return (plot,)


@app.cell
def _(df, np, pd, plot, set_nav_pos, set_selection, x_col_dropdown, y_col_dropdown):
    indices = np.arange(len(df))

    df_plot = pd.DataFrame(
        {
            "index": indices,
            "x": df[x_col_dropdown.value].values,
            "y": df[y_col_dropdown.value].values,
            "file_name": df["file_name"],
        }
    )

    # Only update selection state when the user actually selects new points
    _new_selection = plot.indices
    if len(_new_selection):
        set_selection(list(_new_selection))
        set_nav_pos(0)
    return (df_plot,)


@app.cell
def _(get_nav_pos, get_selection, mo, set_highlight, set_nav_pos, set_selection):
    selected_indices = get_selection()
    if len(selected_indices):
        def _go_prev(v):
            set_nav_pos((get_nav_pos() - 1) % len(selected_indices))
            return v + 1
        def _go_next(v):
            set_nav_pos((get_nav_pos() + 1) % len(selected_indices))
            return v + 1
        def _clear(v):
            set_selection([])
            set_highlight(None)
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
def _(Image, df_plot, get_current_idx, get_highlight, get_nav_pos, get_selection, image_base_path, mo, os, selected_indices, set_current_idx, set_highlight):
    if not get_selection():
        if get_highlight() is not None:
            set_highlight(None)
        image_output = mo.md("**Select points on the scatter plot to browse images.**")
    elif len(selected_indices):
        _idx = get_nav_pos() % len(selected_indices)
        _current_idx = selected_indices[_idx]
        _current_row = df_plot.iloc[_current_idx]
        img = Image.open(os.path.join(image_base_path, _current_row["file_name"]))

        _new_hl = (float(_current_row["x"]), float(_current_row["y"]))
        if get_highlight() != _new_hl:
            set_highlight(_new_hl)
        if get_current_idx() != _current_idx:
            set_current_idx(_current_idx)

        image_output = mo.vstack([
            mo.md(f"**Image {_idx + 1} of {len(selected_indices)}** — `{_current_row['file_name']}`"),
            mo.image(img),
        ])
    else:
        image_output = mo.md("**Select points on the scatter plot to browse images.**")
    return (image_output,)


@app.cell
def _(df, get_current_idx, get_selection, mo, pd):
    _sel = get_selection()
    if len(_sel):
        _feat_cols = [c for c in df.columns if c.startswith("feat_")]
        _all_selected = df.iloc[_sel].drop(columns=_feat_cols).reset_index(drop=True)
        _current = get_current_idx()
        _current_pos = _sel.index(_current) if _current in _sel else None

        def _highlight(row: str, col: str, value):
            try:
                if _current_pos is not None and int(row) == _current_pos:
                    return {"background-color": "#fff3cd"}
            except (ValueError, TypeError):
                pass
            return {}

        data_table = mo.ui.table(
            _all_selected, style_cell=_highlight, selection="single", page_size=15,
        )
    else:
        data_table = mo.ui.table(pd.DataFrame(), selection="single", page_size=15)
    return (data_table,)


@app.cell
def _(data_table, set_nav_pos):
    _selected = data_table.value
    if len(_selected):
        set_nav_pos(int(_selected.index[0]))
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
