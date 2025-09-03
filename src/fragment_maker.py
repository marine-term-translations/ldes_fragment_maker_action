# this file will convert a given ttl file with the config.yml file to a series of small editable yml files
import pathlib
import argparse
from pyrdfj2 import J2RDFSyntaxBuilder
import re
import os
import json
import yaml
from datetime import datetime, timedelta, timezone
import shutil
from sema.subyt import (
    Generator,
    GeneratorSettings,
    Sink,
    Source,
    SinkFactory,
    SourceFactory,
    JinjaBasedGenerator,
)

parser = argparse.ArgumentParser(description="Fragment Maker Script")
parser.add_argument(
    "--branch", type=str, required=True, help="Branch name for the merge"
)
args = parser.parse_args()

print(f"Branch name is: {args.branch}")
CONFIG_LOCATION = pathlib.Path(__file__).parent / "../config.yml"

# Load objects from the objects.json file
with open(
    pathlib.Path(__file__).parent / f"../objects.json",
    "r",
    encoding="utf-8",
) as f:
    objects_file = json.load(f)

# Filter objects by branch
filtered_objects = [obj for obj in objects_file if obj.get("branch") == args.branch]

# Ensure the LDES folder exists
ldes_folder = pathlib.Path(__file__).parent.parent / "LDES"
ldes_folder.mkdir(exist_ok=True)


largest_numbered_file = None
if ldes_folder.exists() and ldes_folder.is_dir():
    ldes_files = list(ldes_folder.iterdir())
    print(f"LDES files: {ldes_files}")
    if ldes_files and len(ldes_files) > 0:
        other_ldes_fragments = True
        # Extract the largest numbered file
        numbered_files = [
            int(match.group(1))
            for file in ldes_files
            if (match := re.search(r"(\d+)", file.stem))
            for file in ldes_files
            if re.search(r"(\d+)", file.stem)
        ]
        print(f"Numbered files: {numbered_files}")
        if numbered_files:
            largest_numbered_file = max(numbered_files)

next_delta_quoted = str(largest_numbered_file) if largest_numbered_file else None

# Search for matching .yml files across all folders and read their contents
gathered_data = []
project_root = pathlib.Path(__file__).parent.parent
for obj in filtered_objects:
    matching_files = list(project_root.rglob(obj["file_name"]))
    for yml_file in matching_files:
        if yml_file.exists():
            with open(yml_file, "r", encoding="utf-8") as yml:
                content = yaml.safe_load(yml)
                content_uri = content["uri"]
                # Extract the base URI and concept ID from the content URI
                # example http://vocab.nerc.ac.uk/collection/P02/current/EPSV/2/
                # result: http://vocab.nerc.ac.uk/collection/P02/EPSV 2
                base_uri_match = re.match(
                    r"(http://vocab\.nerc\.ac\.uk/collection/[^/]+/)[^/]+/([^/]+)/",
                    content_uri,
                )
                if base_uri_match:
                    base_uri = base_uri_match.group(1) + base_uri_match.group(2)
                    content["conceptid"] = f"{base_uri}"
                    print(f"Concept ID: {content['conceptid']}")
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
    
# Current datetime in UTC with "Z" suffix
now_utc = datetime.now(timezone.utc)
date = now_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
date_epoch = int(now_utc.timestamp())
print(f"Date: {date}")

# Last modified datetime = 1 second earlier
last_modified_utc = now_utc - timedelta(seconds=1)
last_modified_date = last_modified_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
last_modified_epoch = int(last_modified_utc.timestamp())
print(f"Last Modified Date: {last_modified_date}")

with open(
    CONFIG_LOCATION,
    "r",
    encoding="utf-8",
) as config_file:
    config = yaml.safe_load(config_file)

languages = config.get("target_languages", [])
print(f"Languages: {languages}")
print(f"Config: {config}")

paths = []

for item in config["sources"][0]["items"]:
    print(f"Item: {item}")
    paths.append(item["path"])
# make vars dict

# if config["base_uri"] ends with / remove it
if config["base_uri"].endswith("/"):
    config["base_uri"] = config["base_uri"][:-1]

vars_dict = {
    "base_uri": config["base_uri"] + "/LDES/",
    "this_fragment_delta": date_epoch,
    "next_fragment_delta": next_delta_quoted,
    "next_fragment_time": date,
    "last_modified_date": last_modified_date,
    "retention_period": 100,
    "languages": languages,
    "paths": paths,
}

output_file = str(date_epoch) + ".ttl"

# make service and sink
service = JinjaBasedGenerator(pathlib.Path(__file__).parent / "templates")
sink = SinkFactory.make_sink(os.path.join(project_root, "LDES", output_file), False)
inputs = {
    "qres": SourceFactory.make_source(
        str(pathlib.Path(__file__).parent / f"../gathered.json")
    )
}
settings = GeneratorSettings()
service.process("fragment.ttl", inputs, settings, sink, vars_dict)

if os.path.exists(os.path.join(project_root, "LDES", "latest.ttl")):
    os.remove(os.path.join(project_root, "LDES", "latest.ttl"))
shutil.copyfile(os.path.join(project_root, "LDES", str(date_epoch) + ".ttl"), os.path.join(project_root, "LDES", "latest.ttl"))
# make a second file that will be called latest
# this has the same vars but with this_fragment_delta "latest"
# vars_dict["this_fragment_delta"] = "latest"
# output_file = "latest.ttl"
# sink = SinkFactory.make_sink(os.path.join(project_root, "LDES", output_file), False)
# service.process("fragment.ttl", inputs, settings, sink, vars_dict)
