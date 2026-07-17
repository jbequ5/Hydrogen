"""PDEBench Data Loader for Hydrogen.

Properly loads high-quality benchmark data from PDEBench HDF5 files.
This is critical for scoring miners against real numerical reference solutions.

Supported PDEs (priority):
- darcy (2D Darcy flow)
- ns_incom (2D incompressible Navier-Stokes)
- burgers (1D Burgers)
"""

import os
import glob
import h5py
import numpy as np
import torch
from typing import Dict, Any, Optional, Tuple, List


class PDEBenchLoader:
    """
    Loads PDEBench datasets into Hydrogen's Challenge format.

    Example:
        loader = PDEBenchLoader(pde_name="darcy", data_root="./data/pdebench")
        data = loader.load(split="train", max_samples=100)
    """

    def __init__(self, pde_name: str, data_root: str = "./data/pdebench"):
        self.pde_name = pde_name.lower()
        self.data_root = data_root
        os.makedirs(data_root, exist_ok=True)

        self.file_paths: List[str] = []
        self._discover_files()

    def _discover_files(self):
        """Find relevant HDF5 files for this PDE."""
        patterns = {
            "darcy": ["*Darcy*.h5", "*darcy*.hdf5", "*DarcyFlow*.h5"],
            "ns_incom": ["*ns_incom*.h5", "*NS*.h5", "*incompressible*.h5"],
            "burgers": ["*Burgers*.h5", "*burgers*.hdf5"],
            "heat": ["*diffusion*.h5", "*Heat*.h5"],
        }

        search_patterns = patterns.get(self.pde_name, ["*.h5", "*.hdf5"])

        for pattern in search_patterns:
            self.file_paths.extend(glob.glob(os.path.join(self.data_root, "**", pattern), recursive=True))

        if not self.file_paths:
            print(f"[PDEBench] Warning: No files found for '{self.pde_name}' in {self.data_root}")

    def load(
        self,
        split: str = "train",
        max_samples: Optional[int] = None,
        resolution: Optional[Tuple[int, int]] = None,
    ) -> Dict[str, torch.Tensor]:
        """
        Load data from PDEBench files and return in a standardized format.

        Returns a dict with keys like:
            'u_true', 'a' (permeability for Darcy), 'velocity', etc.
        """
        if not self.file_paths:
            raise FileNotFoundError(
                f"No PDEBench files found for '{self.pde_name}'. "
                f"Please download using the official script first."
            )

        # Use the first matching file (in production, support multiple + parameter filtering)
        file_path = self.file_paths[0]
        print(f"[PDEBench] Loading from: {file_path}")

        with h5py.File(file_path, "r") as f:
            data = self._parse_file(f, self.pde_name)

        # Convert to torch and optionally subsample
        data = {k: torch.from_numpy(v).float() for k, v in data.items()}

        if max_samples is not None:
            for k in data:
                if data[k].dim() > 0:
                    data[k] = data[k][:max_samples]

        return data

    def _parse_file(self, f: h5py.File, pde_name: str) -> Dict[str, np.ndarray]:
        """Parse different PDEBench file structures."""
        data = {}

        if pde_name in ["darcy", "darcy_2d"]:
            # Typical Darcy structure in PDEBench
            if "tensor" in f:
                tensor = f["tensor"][...]
                # Often shape: (N, 2, H, W) or (N, H, W) with a and u
                if tensor.shape[1] == 2:
                    data["a"] = tensor[:, 0]      # permeability
                    data["u_true"] = tensor[:, 1] # solution
                else:
                    data["u_true"] = tensor
            elif "a" in f and "u" in f:
                data["a"] = f["a"][...]
                data["u_true"] = f["u"][...]
            else:
                # Fallback: take first two datasets
                keys = list(f.keys())
                if len(keys) >= 2:
                    data["a"] = f[keys[0]][...]
                    data["u_true"] = f[keys[1]][...]

        elif pde_name in ["ns_incom", "navier_stokes", "ns_2d"]:
            # Incompressible NS - usually has velocity and pressure
            if "velocity" in f:
                data["velocity_true"] = f["velocity"][...]
            if "pressure" in f:
                data["pressure_true"] = f["pressure"][...]
            # Sometimes stored as 'tensor' or 'fields'
            if not data and "tensor" in f:
                tensor = f["tensor"][...]
                if tensor.shape[1] >= 2:
                    data["velocity_true"] = tensor[:, :2]
                    if tensor.shape[1] > 2:
                        data["pressure_true"] = tensor[:, 2]

        elif pde_name == "burgers":
            if "tensor" in f:
                data["u_true"] = f["tensor"][...]
            elif "u" in f:
                data["u_true"] = f["u"][...]

        else:
            # Generic fallback
            for key in f.keys():
                if isinstance(f[key], h5py.Dataset):
                    data[key] = f[key][...]

        if not data:
            raise ValueError(f"Could not parse PDEBench file for {pde_name}. Check file structure.")

        return data

    def get_baseline_error(self) -> float:
        """Return a reasonable baseline error for this PDE (can be refined)."""
        baselines = {
            "darcy": 0.095,
            "ns_incom": 0.18,
            "burgers": 0.12,
            "heat": 0.09,
        }
        return baselines.get(self.pde_name, 0.15)
