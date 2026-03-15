# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "matplotlib==3.10.8",
#     "pandas==3.0.0",
#     "pymde>=0.3.0",
#     "torch==2.10.0",
#     "pillow",
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
    import pymde
    import torch
    import os
    from PIL import Image

    df = pd.read_csv("/workspaces/dev_container_template/data/umap_embedding.csv")

    feature_cols = [f"feat_{i}" for i in range(256)]
    X = df[feature_cols].values

    image_base_path = "/workspaces/dev_container_template/data/SU-671-W1"
    return Image, df, image_base_path, mo, os, pd, plt, torch


@app.cell
def _(mo):
    mo.md("""
    # Visualizing embeddings
    Select points on the embedding to preview the corresponding images.
    """)
    return


@app.cell
def _(df):
    embedding = df[["umap_0", "umap_1"]].values
    return (embedding,)


@app.cell
def _(embedding, mo, plt):
    # ax = pymde.plot(embedding, color_by=df["hole_id"])
    # plot = mo.ui.matplotlib(ax)
    # plot

    fig, ax = plt.subplots()

    ax.scatter(
        embedding[:, 0],
        embedding[:, 1],
        s=10
    )

    plot = mo.ui.matplotlib(ax)
    plot
    return (plot,)


@app.cell
def _(embedding, plot):
    mask = plot.value.get_mask(embedding[:, 0], embedding[:, 1])
    return (mask,)


@app.cell
def _(df, embedding, pd, torch):
    indices = torch.arange(len(df)).numpy()

    df_plot = pd.DataFrame(
        {
            "index": indices,
            "x": embedding[:, 0],
            "y": embedding[:, 1],
            "file_name": df["file_name"],
        }
    )
    return (df_plot,)


@app.cell
def _(df_plot, mask, mo):
    table = mo.ui.table(df_plot[mask])
    return (table,)


@app.function
def show_images(indices, df_plot, image_base_path, plt, Image, os, max_images=10):

    indices = indices[:max_images]
    images = df_plot.iloc[indices]["file_name"].values

    fig, axes = plt.subplots(1, len(images))
    fig.set_size_inches(12.5, 1.5)

    if len(images) > 1:
        for fname, ax in zip(images, axes.flat):

            img = Image.open(os.path.join(image_base_path, fname))
            ax.imshow(img)

            ax.set_xticks([])
            ax.set_yticks([])

    else:
        img = Image.open(os.path.join(image_base_path, images[0]))

        axes.imshow(img)
        axes.set_xticks([])
        axes.set_yticks([])

    plt.tight_layout()
    return fig


@app.cell
def _(Image, df_plot, image_base_path, mask, mo, os, plt, table):

    mo.stop(not mask.any())

    selected_images = (
        show_images(list(mask.nonzero()[0]), df_plot, image_base_path, plt, Image, os)
        if not len(table.value)
        else show_images(list(table.value["index"]), df_plot, image_base_path, plt, Image, os)
    )

    mo.md(
        f"""
    **Preview of selected images**

    {mo.as_html(selected_images)}

    **Selected rows**

    {table}
    """
    )
    return


if __name__ == "__main__":
    app.run()
