#!/usr/bin/env python

# Given a spack release, look at the number of downloads

#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import argparse
import sys
import os
import operator
import json
import requests
from jinja2 import Template

import datetime


def get_parser():
    parser = argparse.ArgumentParser(description="Parse commits.")

    parser.add_argument(
        "repo",
        help="name of repository to parse (e.g., spack/spack)",
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

    # Get a list of all releases
    url = "https://api.github.com/repos/%s/releases" % args.repo
    headers = {"Accept": "application/vnd.github.v3+json"}
    params = {"per_page": 100}
    response = requests.get(url, headers=headers, params=params)

    # Sorted newest at top / first to oldest
    result = response.json()
    result.reverse()

    # Group based on extension. We actually only have one .tar.gz per release
    # software with multiple releases would need to do this differently
    downloads = {}
    for res in result:
        if not res["assets"]:
            continue
        downloads[res["tag_name"]] = res["assets"][0]["download_count"]

    # calculate release downloads per month
    months = {}
    first_date = None
    last_name = None
    for res in result:
        second_date = res["published_at"]
        if not first_date:
            first_date = second_date
            last_name = res["tag_name"]
            continue
        first_timestamp = datetime.datetime.strptime(first_date, "%Y-%m-%dT%H:%M:%SZ")
        second_timestamp = datetime.datetime.strptime(second_date, "%Y-%m-%dT%H:%M:%SZ")
        difference = second_timestamp - first_timestamp
        first_date = second_date
        months[last_name] = difference
        last_name = res["tag_name"]

    # Latest release
    second_timestamp = datetime.datetime.now()
    first_timestamp = datetime.datetime.strptime(first_date, "%Y-%m-%dT%H:%M:%SZ")
    difference = second_timestamp - first_timestamp
    months[last_name] = difference

    bymonth = {}
    for res in result:
        if res["tag_name"] not in downloads:
            continue
        version = res["tag_name"]
        timestamp = months[version]
        bymonth[version] = {
            "days": timestamp.days,
            "downloads_per_day": round(downloads[res["tag_name"]] / timestamp.days, 2),
        }

    write_json(downloads, os.path.join("data", "downloads.json"))
    write_json(bymonth, os.path.join("data", "downloads_per_day.json"))

    # Write to template
    with open("template.html", "r") as fd:
        template = Template(fd.read())

    # Render and write the result to index.html
    result = template.render(downloads=downloads, bymonth=bymonth)
    with open("index.html", "w") as fd:
        fd.write(result)


if __name__ == "__main__":
    main()
