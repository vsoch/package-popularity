#!/usr/bin/env python

# Given export json files of contributions, one file per package, generate
# summary counts for each package for:
# 1. total contributions over time
# 2. contributions per year
# And then we combine packages to compare by year.

#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import argparse
import sys
import os
import operator
import json
from jinja2 import Template
import spack.spec


def get_parser():
    parser = argparse.ArgumentParser(description="Parse commits.")

    parser.add_argument(
        "data_dir",
        help="path to dump of contributor json flies",
    )

    return parser


def read_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def write_json(obj, filename):
    with open(filename, "w") as fd:
        fd.write(json.dumps(obj, indent=4))


def main():
    """run_shpc is the entrypoint to the singularity-hpc client."""

    parser = get_parser()
    args, extra = parser.parse_known_args()

    # Total contributions per package
    totals = {}

    # Package authors
    authors = {}

    # By year
    year_totals = {}
    years = [str(x) for x in range(2013, 2022)]
    for year in years:
        year_totals[year] = {}

    for package_file in os.listdir(args.data_dir):
        filename = os.path.join(args.data_dir, package_file)

        try:
            content = read_json(filename)
            package = package_file.replace(".json", "")
            print("parsing package %s" % package)

            # Number of contributors
            totals[package] = len(content["authors"])
            authors[package] = list(set(x["author"] for x in content["authors"]))
        except:
            pass

    # Sort based on total contributors
    totals = dict(sorted(totals.items(), key=operator.itemgetter(1), reverse=True))

    # For each package, look up the build system, and count
    systems = {}
    uniques = set()
    breakdown = {}
    for name in totals:

        # The spack I derived from has some newer packages, oops
        try:
            spec = spack.spec.Spec(name)
            buildsys = spec.package.build_system_class
        except:
            if name.startswith("r-"):
                buildsys = "RPackage"
            elif name.startswith("py-"):
                buildsys = "PythonPackage"
            else:
                buildsys = "Package"
        uniques.add(buildsys)
        systems[name] = buildsys
        if buildsys not in breakdown:
            breakdown[buildsys] = 0
        breakdown[buildsys] += 1

    # calculate breakdown as percentages
    percents = {}
    for buildsys, count in breakdown.items():
        percents[buildsys] = round(count / len(totals) * 100, 3)

    # Put them all together!
    data = {}
    for name in totals:
        data[name] = {
            "authors": sorted(authors[name]),
            "count": totals[name],
            "build_system": systems[name],
        }

    # Save data to file
    write_json(totals, os.path.join("data", "total-contributions.json"))
    write_json(authors, os.path.join("data", "authors.json"))

    # Write to template
    with open("template.html", "r") as fd:
        template = Template(fd.read())

    # Render and write the result to index.html
    result = template.render(packages=data, build_systems=uniques, percents=percents)
    with open("index.html", "w") as fd:
        fd.write(result)

    # Second visualization - reversed! Authors are bubbles, and packages count
    with open("template-reversed.html", "r") as fd:
        template = Template(fd.read())

    authordata = {}
    for package, metadata in data.items():
        for author in metadata["authors"]:
            if author not in authordata:
                authordata[author] = {"count": 0, "packages": []}
            authordata[author]["count"] += 1
            authordata[author]["packages"].append(package)

    # Calculate percent of packages contributed to
    maxnum = 0
    for author, meta in authordata.items():
        meta["percent"] = round(meta["count"] / len(totals) * 100, 3)
        if len(meta["packages"]) > maxnum:
            maxnum = len(meta["packages"])
        meta['packages'] = sorted(meta['packages'])

    result = template.render(
        authors=authordata, max=maxnum, total_contributors=len(authordata)
    )
    with open(os.path.join("authors", "index.html"), "w") as fd:
        fd.write(result)


if __name__ == "__main__":
    main()
