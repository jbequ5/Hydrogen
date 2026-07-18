"""Validator Configuration

Central place for validator-specific config defaults.
"""

import bittensor as bt


def add_args(parser):
    parser.add_argument("--evaluation_interval", type=int, default=360, help="Seconds between evaluations")
    parser.add_argument("--version_key", type=int, default=1, help="Validator version key")
    parser.add_argument("--active_challenges", type=str, nargs="+", default=["poisson_2d_v1"],
                        help="List of active challenges")


def config():
    parser = bt.argparse(add_args)
    return bt.config(parser)
