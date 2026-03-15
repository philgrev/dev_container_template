# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "matplotlib==3.10.8",
#     "pandas==3.0.0",
#     "pymde>=0.3.0",
#     "torch==2.10.0",
#     "pillow",
#     "plotly",
# ]
# ///

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import pymde
    import torch
    import os
    from PIL import Image

    return Image, go, mo, os, pd, plt, px, torch


@app.cell
def _(mo):
    mo.md("""
    # Visualizing embeddings
    Provide a CSV file path and image directory, then select points on the embedding to preview the corresponding images.
    """)
    return


@app.cell
def _(mo):
    csv_path_input = mo.ui.text(
        label="CSV file path",
        value="/workspaces/dev_container_template/data/umap_embedding.csv",
        full_width=True,
    )
    image_dir_input = mo.ui.text(
        label="Image directory path",
        value="/workspaces/dev_container_template/data/SU-671-W1",
        full_width=True,
    )
    mo.vstack([csv_path_input, image_dir_input])
    return (csv_path_input, image_dir_input)


@app.cell
def _(csv_path_input, image_dir_input, mo, os, pd):
    mo.stop(
        not csv_path_input.value or not image_dir_input.value,
        mo.md("**Enter a CSV path and image directory above to get started.**"),
    )
    mo.stop(
        not os.path.isfile(csv_path_input.value),
        mo.md(f"**CSV not found:** {csv_path_input.value}"),
    )
    mo.stop(
        not os.path.isdir(image_dir_input.value),
        mo.md(f"**Directory not found:** {image_dir_input.value}"),
    )

    df = pd.read_csv(csv_path_input.value)
    image_base_path = image_dir_input.value
    return df, image_base_path


@app.cell
def _(df, mo):
    mo.stop(
        not {"umap_0", "umap_1", "file_name"}.issubset(df.columns),
        mo.md("**CSV must contain `umap_0`, `umap_1`, and `file_name` columns.**"),
    )
    embedding = df[["umap_0", "umap_1"]].values

    # Offer non-embedding, non-file_name columns for coloring
    color_options = [c for c in df.columns if c not in {"umap_0", "umap_1", "file_name"}]
    color_dropdown = mo.ui.dropdown(
        options=["None"] + color_options,
        value="None",
        label="Colour by",
    )
    return color_dropdown, embedding


@app.cell
def _(mo):
    get_highlight, set_highlight = mo.state(None)
    get_selection, set_selection = mo.state([])
    return get_highlight, get_selection, set_highlight, set_selection


@app.cell
def _(color_dropdown, df, embedding, get_highlight, get_selection, go, mo, px):
    _sel = set(get_selection())
    _has_sel = len(_sel) > 0
    _opacities = [1.0 if i in _sel else 0.15 for i in range(len(embedding))] if _has_sel else [0.5] * len(embedding)
    _sizes = [8 if i in _sel else 5 for i in range(len(embedding))] if _has_sel else [5] * len(embedding)

    _color_col = color_dropdown.value
    _fig = go.Figure()

    if _color_col == "None":
        _fig.add_trace(go.Scattergl(
            x=embedding[:, 0], y=embedding[:, 1],
            mode="markers",
            marker=dict(size=_sizes, opacity=_opacities, color="steelblue"),
            showlegend=False,
        ))
    else:
        _values = df[_color_col]
        if _values.dtype == "object" or _values.nunique() < 20:
            for _cat in _values.unique():
                _mask = _values == _cat
                _idx = [i for i, m in enumerate(_mask) if m]
                _fig.add_trace(go.Scattergl(
                    x=embedding[_mask, 0], y=embedding[_mask, 1],
                    mode="markers",
                    marker=dict(
                        size=[_sizes[i] for i in _idx],
                        opacity=[_opacities[i] for i in _idx],
                    ),
                    name=str(_cat),
                ))
        else:
            _fig.add_trace(go.Scattergl(
                x=embedding[:, 0], y=embedding[:, 1],
                mode="markers",
                marker=dict(
                    size=_sizes, opacity=_opacities,
                    color=_values, colorscale="viridis", colorbar=dict(title=_color_col),
                ),
                showlegend=False,
            ))

    _fig.update_layout(
        dragmode="lasso",
        xaxis_title="umap_0",
        yaxis_title="umap_1",
        height=600,
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
    mo.vstack([color_dropdown, plot])
    return (plot,)


@app.cell
def _(df, embedding, pd, plot, set_selection, torch):
    indices = torch.arange(len(df)).numpy()

    df_plot = pd.DataFrame(
        {
            "index": indices,
            "x": embedding[:, 0],
            "y": embedding[:, 1],
            "file_name": df["file_name"],
        }
    )

    # Only update selection state when the user actually selects new points
    _new_selection = plot.indices
    if len(_new_selection):
        set_selection(list(_new_selection))
    return (df_plot,)


@app.cell
def _(get_selection, mo):
    selected_indices = get_selection()
    mo.stop(not len(selected_indices), mo.md("**Select points on the scatter plot to browse images.**"))

    image_nav = mo.ui.number(
        start=0,
        stop=len(selected_indices) - 1,
        value=0,
        step=1,
        label=f"Image (0–{len(selected_indices) - 1})",
    )
    return image_nav, selected_indices


@app.cell
def _(Image, df, df_plot, embedding, get_highlight, image_base_path, image_nav, mo, os, selected_indices, set_highlight):
    _current_idx = selected_indices[image_nav.value]
    _current_row = df_plot.iloc[_current_idx]
    img = Image.open(os.path.join(image_base_path, _current_row["file_name"]))
    _row_info = df.iloc[_current_idx].drop([c for c in df.columns if c.startswith("feat_")]).to_frame().T

    # Only update highlight if it actually changed to avoid re-render loop
    _new_hl = (float(embedding[_current_idx, 0]), float(embedding[_current_idx, 1]))
    if get_highlight() != _new_hl:
        set_highlight(_new_hl)

    mo.vstack([
        mo.md(f"**Image {image_nav.value + 1} of {len(selected_indices)}** — `{_current_row['file_name']}`"),
        image_nav,
        mo.image(img, width=800),
        mo.ui.table(_row_info),
    ])
    return


if __name__ == "__main__":
    app.run()
