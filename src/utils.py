import os
from pathlib import Path
import numpy as np
import rasterio as rio
from rasterio.merge import merge
from . import config  # TODO


def get_classes_33_to_23_dict(classes_33_to_23_legend_path: str) -> dict:
    classes_33_to_23_dict = {}
    with open(classes_33_to_23_legend_path, encoding="UTF-8") as f:
        for line in f:
            line = line.strip().split()
            classes_33_to_23_dict[int(line[0])] = int(line[2])
    return classes_33_to_23_dict


def get_classes_23_dict(classes_23_legend_path: str) -> dict:
    classes_23_dict = {}
    with open(classes_23_legend_path, encoding="UTF-8") as f:
        for line in f:
            line = line.strip().split(". ")
            classes_23_dict[int(line[0])] = line[1]
    return classes_23_dict


def replace_2d_ndarray_values(array: np.ndarray, values_dict: dict) -> np.ndarray:
    n_rows, n_cols = array.shape
    for row in range(n_rows):
        for col in range(n_cols):
            old_value = array[row][col]
            new_value = values_dict[old_value]
            array[row][col] = new_value
    return array


def make_experiment_dirs(
    experiment_name: str,
    interim: bool = True,
    processed: bool = True,
    models: bool = True,
) -> tuple[str, ...]:
    dirs = []
    if interim:
        interim_dir = os.path.join(config.INTERIM_DATA_DIR, experiment_name)
        Path(interim_dir).mkdir(parents=True, exist_ok=True)
        dirs.append(interim_dir)

    if processed:
        processed_dir = os.path.join(config.PROCESSED_DATA_DIR, experiment_name)
        Path(processed_dir).mkdir(parents=True, exist_ok=True)
        dirs.append(processed_dir)

    if models:
        models_dir = os.path.join(config.MODELS_DIR, experiment_name)
        Path(models_dir).mkdir(parents=True, exist_ok=True)
        dirs.append(models_dir)

    return tuple(dirs)


def combine_bands(bands_paths: list[str], dst_path: str) -> None:
    with rio.open(bands_paths[0]) as src_img:
        meta = src_img.meta

    meta.update(count=len(bands_paths))

    with rio.open(dst_path, "w", **meta) as dst_img:
        for id, band in enumerate(bands_paths, start=1):
            with rio.open(band) as src_img:
                dst_img.write_band(id, src_img.read(1))


def merge_fragments(fragments_paths: list[str], dst_path: str) -> None:
    fragments_imgs = []
    for path in fragments_paths:
        src_img = rio.open(path)
        fragments_imgs.append(src_img)
    mosaic, mosaic_transform = merge(fragments_imgs)
    mosaic_meta = fragments_imgs[0].meta.copy()
    mosaic_meta.update(
        {
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": mosaic_transform,
        }
    )
    with rio.open(dst_path, "w", **mosaic_meta) as dst_img:
        dst_img.write(mosaic)


def crop_by_window(src_path: str, dst_path: str, window: rio.windows.Window) -> None:
    with rio.open(src_path) as src_img:
        meta = src_img.meta.copy()
        meta.update(
            {
                "height": window.height,
                "width": window.width,
                "transform": rio.windows.transform(window, src_img.transform),
            }
        )

        with rio.open(dst_path, "w", **meta) as dst_img:
            dst_img.write(src_img.read(window=window))
