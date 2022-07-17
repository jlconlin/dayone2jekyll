from __future__ import annotations

import argparse
import pathlib
import zipfile
import json
import datetime
import dataclasses
import inspect
import functools
import textwrap
import zoneinfo
import re

from pprint import pprint
from dataclass_wizard import JSONWizard

@dataclasses.dataclass
class Location(JSONWizard):
    latitude: float
    longitude: float

    def Jekyll(self):
        """
        Format location as a string suitable for Jekyll frontmatter
        """

        return textwrap.dedent(f"""\
        location: 
          latitude: {self.latitude}
          longitude: {self.longitude}""")

@dataclasses.dataclass
@functools.total_ordering
class Entry(JSONWizard):
    """
    A single DayOne entry
    """
    creation_date: datetime.datetime 
    modified_date: datetime.datetime
    text: str
    time_zone: str
    tags: list[str] = None
    location: Location | None = None

    def __post_init__(self):
        self.time_zone = zoneinfo.ZoneInfo(self.time_zone)
        self.creation_date = self.creation_date.astimezone(self.time_zone)
        self.modified_date = self.modified_date.astimezone(self.time_zone)
        self.title = self.creation_date.strftime("%A %B %d, %Y")

        # Fixing some escape issues. I'm sure there is a better way to do this,
        # but I'm not sure what it is.
        self.text = self.text.replace(r"’"  , "'" )\
                             .replace(r"\-" , "-" )\
                             .replace(r"\]" , "]" )\
                             .replace(r"\^" , "^" )\
                             .replace(r"\$" , "$" )\
                             .replace(r"\*" , "*" )\
                             .replace(r"\." , "." )\
                             .replace(r"\\" , "\\")

    def __eq__(self, other):
        return self.creation_date == other.creation_date
    def __lt__(self, other):
        return self.creation_date < other.creation_date

    def Jekyll(self, dirPath=None):
        """
        Return a string of the Entry contents formatted for inclusing in a
        Jekyll blog.
        """
        jekyll = textwrap.dedent(f"""\
            ---
            title: {self.title}
            date: {self.creation_date}
        """)
        if self.location:
            jekyll += "{}\n".format(self.location.Jekyll())
        if self.tags:
            jekyll += "tags: \n"
            for tag in self.tags:
                jekyll += f"  - {tag}\n"

        jekyll += f"---\n{self.text}"

        if dirPath:
            date = self.creation_date.strftime("%Y-%M-%d-%B%d")
            filename = dirPath.joinpath(f"{date}.md")
            i = 2
            while filename.exists():
                filename = dirPath.joinpath(f"{date}-{i}.md")
                i += 1
            with filename.open('w') as file:
                file.write(jekyll)

        return jekyll

def journalList(zip):
    """
    Print all the journals in the zip file. These those that are json file.
    """
    for name in zip.namelist():
        if name.endswith(".json"):
            print(name)

def extract(journal, name):
    """
    Extract journal into a set of files
    """
    entries = sorted([Entry.from_dict(entry) for entry in journal['entries']])

    return entries

if __name__ == "__main__":
    print("Converting from dayone to jekyll\n")

    parser = argparse.ArgumentParser(
        description="Convert from dayone to jekyll")

    parser.add_argument("dayone", type=pathlib.Path,
                        help="Zip file containing DayOne entries")
    parser.add_argument("--list", action="store_true", default=False,
                        help="List available journals")
    parser.add_argument("--journal", type=str,
                        help="Name of journal to extract")
    parser.add_argument("--jekyll", type=pathlib.Path, default=None,
                        help="Directory where to store Jekyll entries")

    args = parser.parse_args()

    zip = zipfile.ZipFile(args.dayone)

    if args.list:
        journalList(zip)

    if args.journal:
        journal = json.loads(zip.read(args.journal + ".json"))
        extracted = extract(journal, args.journal)

    if args.jekyll:
        jekyllPath = args.jekyll.joinpath("_posts")
        jekyllPath.mkdir(exist_ok=True, parents=True)
        for entry in extracted:
            entry.Jekyll(jekyllPath)

