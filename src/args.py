import argparse
import data

parser = argparse.ArgumentParser(prog="main.py")
parser.add_argument("-c", "--cache-disabled", action="store_true", help="Disable cache.")
args = parser.parse_args()

data.CACHE_DISABLED = args.cache_disabled
