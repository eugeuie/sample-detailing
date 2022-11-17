import os
from pathlib import Path
import numpy as np
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
