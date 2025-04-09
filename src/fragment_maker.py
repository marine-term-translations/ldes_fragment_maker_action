# this file will convert a given ttl file with the config.yml file to a series of small editable yml files
import pathlib
import argparse
from pyrdfj2 import J2RDFSyntaxBuilder
import re
import os
import json
import yaml
from datetime import datetime
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

QUERYBUILDER = J2RDFSyntaxBuilder(
    templates_folder=pathlib.Path(__file__).parent / "templates"
)

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
                base_uri_match = re.match(r"(http://vocab\.nerc\.ac\.uk/collection/[^/]+/)[^/]+/([^/]+)/", content_uri)
                if base_uri_match:
                    base_uri = base_uri_match.group(1) + base_uri_match.group(2)
                    content["conceptid"] = f"{base_uri}"
                    print(f"Concept ID: {content['conceptid']}")
                gathered_data.append(
                    {"file_name": obj["file_name"], "content": content}
                )

next_delta_quoted = "tobefilledinhere"

# Write gathered data to gathered.json
with open(
    pathlib.Path(__file__).parent / f"../gathered.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(gathered_data, f, indent=4)

# Get the current datetime in CCYY-MM-DDThh:mm:ss.sss format
date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
date_epoch = int(datetime.now().timestamp())
print(f"Date: {date}")

with open(
    CONFIG_LOCATION,
    "r",
    encoding="utf-8",
) as config_file:
    config = yaml.safe_load(config_file)

languages = config.get("target_languages", [])
print(f"Languages: {languages}")
# make vars dict
vars_dict = {
    "this_fragment_delta": args.branch,
    "next_fragment_delta": next_delta_quoted,
    "next_fragment_time": date,
    "retention_period": 100,
    "languages": languages,
}

output_file = str(date_epoch) + ".ttl"  

# make service and sink
service = JinjaBasedGenerator(pathlib.Path(__file__).parent / "templates")
sink = SinkFactory.make_sink(
    os.path.join(project_root, "LDES", output_file), False
)
inputs = {"qres": SourceFactory.make_source(str(pathlib.Path(__file__).parent / f"../gathered.json"))}
settings = GeneratorSettings()
service.process("fragment.ttl", inputs, settings, sink, vars_dict)


