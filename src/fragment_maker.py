# this file will convert a given ttl file with the config.yml file to a series of small editable yml files
import pathlib
import argparse
from pyrdfj2 import J2RDFSyntaxBuilder
import re
import json
import yaml

parser = argparse.ArgumentParser(description="Fragment Maker Script")
parser.add_argument(
    "--branch", type=str, required=True, help="Branch name for the merge"
)
args = parser.parse_args()

print(f"Branch name is: {args.branch}")

QUERYBUILDER = J2RDFSyntaxBuilder(
    templates_folder=pathlib.Path(__file__).parent / "templates"
)

# Load objects from the objects.json file
with open(
    pathlib.Path(__file__).parent / f"../objects.json",
    "r",
    encoding="utf-8",
) as f:
    objects_file = json.load(f)

with open(
    pathlib.Path(__file__).parent / f"../objects.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(objects_file, f, indent=4)
