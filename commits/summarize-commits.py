#!/usr/bin/env python

# Given export json files of commits, one file per package, generate
# summary counts for each package for:
# 1. total commits over time
# 2. commits per month
# 3. commits per year
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


def get_parser():
    parser = argparse.ArgumentParser(description="Parse commits.")

    parser.add_argument(
        "commits_dir",
        help="path to dump of commit json flies",
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

    parser = get_parser()
    args, extra = parser.parse_known_args()

    # Total commits per package
    totals = {}

    # Package added dates
    added = {}

    # By year
    year_totals = {}
    years = [str(x) for x in range(2013, 2022)]
    for year in years:
        year_totals[year] = {}

    for package_file in os.listdir(args.commits_dir):
        filename = os.path.join(args.commits_dir, package_file)
        content = read_json(filename)
        package = package_file.replace(".json", "")
        print("parsing package %s" % package)

        # Total number of commits for the package
        totals[package] = len(content)

        # Get all year strings
        package_years = [x["date"].split("-")[0] for x in content]
        package_years.sort()
        added[package] = package_years[0]

        # Populate by year (first commit in 2013)
        for year in years:
            year_totals[year][package] = package_years.count(year)

    # Sort based on total commits
    totals = dict(sorted(totals.items(), key=operator.itemgetter(1), reverse=True))

    # Save data to file
    write_json(totals, os.path.join("data", "total-commits.json"))
    write_json(added, os.path.join("data", "package-added-year.json"))
    write_json(year_totals, os.path.join("data", "total-commits-by-year.json"))

    # parse subsets of data for plots. The top 25 packages by total commits
    top25 = dict(sorted(totals.items(), key=operator.itemgetter(1), reverse=True)[:25])

    # For each year, get the 25 top packages
    top25years = {}
    for year, packages in year_totals.items():
        tops = dict(
            sorted(packages.items(), key=operator.itemgetter(1), reverse=True)[:25]
        )
        top25years[year] = tops

    # Write to template
    with open("template.html", "r") as fd:
        template = Template(fd.read())

    # Assemble titles, labels, and counts
    maxval = max(top25.values())
    minval = min(top25.values())
    charts = [
        {
            "divid": "top25",
            "labels": list(top25.keys()),
            "vals": list(top25.values()),
            "title": "Top 25 Packages by Commits over all time",
            "min": minval,
            "max": maxval,
        }
    ]

    for year, packages in top25years.items():
        maxval = max(packages.values())
        minval = min(packages.values())
        charts.append(
            {
                "divid": "top25_%s" % year,
                "labels": list(packages.keys()),
                "vals": list(packages.values()),
                "title": "Top 25 Packages by commits for %s" % year,
                "min": minval,
                "max": maxval,
            }
        )

    # Render and write the result to index.html
    result = template.render(charts=charts)
    with open("index.html", "w") as fd:
        fd.write(result)


if __name__ == "__main__":
    main()
