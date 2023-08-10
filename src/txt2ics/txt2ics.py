#!/usr/bin/env python3

import os
import argparse
from dotenv import load_dotenv
import lib
import logging

logging.basicConfig(level=logging.INFO)

def main_cli():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Converts TODOs in a text file into an iCal file."
    )
    parser.add_argument(
        "infile",
        nargs="?",
        type=argparse.FileType("r", encoding="utf-8"),
        default=os.getenv("infile"),
    )
    parser.add_argument(
        "--outfile", type=argparse.FileType("wb"), default=os.getenv("outfile") or "-"
    )

    args = parser.parse_args()
    cal = lib.make_calendar(args.infile)

    try:
        # line endings are part of the iCal standard, so if we're writing to a file
        # we need to write the bytes.
        args.outfile.write(cal.to_ical())
    except TypeError:
        # Writing to stdout is a bit different, as it requires an str on Linux. On
        # Windows stdout accepts a byte.
        args.outfile.write(cal.to_ical().decode("utf-8"))

if __name__ == '__main__':
    main_cli()