
import argparse
import pathlib
import zipfile
import json
import datetime
import dateutil.parser

class Date():
    def __init__(self, datestr):
        self.string = datestr
        self.date = dateutil.parser.parse(datestr)

    @property
    def isoDate(self):
        return self.date.strftime("%Y-%m-%d")

    @property
    def isoDateTime(self):
        return self.date.strftime("%Y-%m-%d %H:%M:%S")
    
        
def journalList(zip):
    """
    Print all the journals in the zip file. These those that are json file.
    """
    for name in zip.namelist():
        if name.endswith(".json"):
            print(name)

def extract(journal):
    """
    Extract journal into a set of files
    """
    entries = journal['entries']
    for entry in entries:
        creation = Date(entry['creationDate'])
        print(creation.isoDateTime)


if __name__ == "__main__":
    print("Converting from dayone to jekyll\n")

    parser = argparse.ArgumentParser(
        description="Convert from dayone to jekyll")

    parser.add_argument("dayone", type=pathlib.Path,
                        help="Zip file containing DayOne entries")
    parser.add_argument("--list", action="store_true", default=False,
                        help="List available journals")
    parser.add_argument("--extract", type=str, default=None,
                        help="Extract named journal")

    args = parser.parse_args()

    zip = zipfile.ZipFile(args.dayone)


    if args.list:
        journalList(zip)

    if args.extract:
        journal = json.loads(zip.read(args.extract + ".json"))
        extract(journal)

    daily = json.loads(zip.read("Daily Journal.json"))
    entry = daily['entries'][0]

    date = dateutil.parser.parse(entry['creationDate'])
