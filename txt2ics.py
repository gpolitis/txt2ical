#!/usr/bin/env python3

import os
import argparse
from dotenv import load_dotenv
import lib

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

lib.make_calendar(parser.parse_args())
