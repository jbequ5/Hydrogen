"""Helper script to download PDEBench datasets.

Usage:
    python -m hydrogen.data.download_pdebench --pde_name darcy
    python -m hydrogen.data.download_pdebench --pde_name ns_incom
"""

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pde_name", type=str, required=True, help="PDEBench PDE name (darcy, ns_incom, burgers, etc.)")
    parser.add_argument("--root_folder", type=str, default="./data/pdebench")
    args = parser.parse_args()

    print(f"Downloading PDEBench data for: {args.pde_name}")
    print("Please use the official PDEBench download script:")
    print("https://github.com/pdebench/PDEBench/blob/main/pdebench/data_download/download_direct.py")
    print(f"Example: python download_direct.py --root_folder {args.root_folder} --pde_name {args.pde_name}")


if __name__ == "__main__":
    main()
