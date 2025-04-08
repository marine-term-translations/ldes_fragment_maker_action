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

# Filter objects by branch
filtered_objects = [obj for obj in objects_file if obj.get("branch") == args.branch]

# Search for matching .yml files across all folders and read their contents
gathered_data = []
project_root = pathlib.Path(__file__).parent.parent
for obj in filtered_objects:
    matching_files = list(project_root.rglob(obj["file_name"]))
    for yml_file in matching_files:
        if yml_file.exists():
            with open(yml_file, "r", encoding="utf-8") as yml:
                content = yaml.safe_load(yml)
                gathered_data.append(
                    {"file_name": obj["file_name"], "content": content}
                )

# Write gathered data to gathered.json
with open(
    pathlib.Path(__file__).parent / f"../gathered.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(gathered_data, f, indent=4)
