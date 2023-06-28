#!/usr/bin/env python3

import os
from icalendar import Calendar, Todo
import dateutil.parser
from datetime import datetime
import argparse
import re
from dotenv import load_dotenv
import hashlib

# import logging
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)

# TODO add support for created & completed dates.
# TODO add support for contexts (words that start with @) and projects (words that start with +).

TAGS_REGEX = r"([^\s]+):([^\s]+)"
DATE_REGEX = r"([0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?)?)"


def parse_date(value):
    rematch = re.match(DATE_REGEX, value)
    return dateutil.parser.isoparse(rematch.group(1))


TAG_PARSE = {
    "due": parse_date,
    "start": parse_date,
    "dtstamp": parse_date,
    "location": lambda value: value,
    "categories": lambda value: value.split(","),
}

STATUS_REGEX = r"^- \[( |x)\]"
KEYWORD_REGEX = r"^- (TODO|DONE|EXPIRED|CANCELLED|NEEDS-ACTION|COMPLETED|IN-PROCESS)"

# Valid VTODO statuses are listed in the RFC https://www.rfc-editor.org/rfc/rfc5545#section-3.8.1.11
# We mark cancelled as completed because Thunderbird shows cancelled tasks https://bugzilla.mozilla.org/show_bug.cgi?id=382363
KEYWORD_MAP = {
    "TODO": "",
    "DONE": "COMPLETED",
    "EXPIRED": "COMPLETED",
    "CANCELLED": "COMPLETED",
}


def make_todo(line):
    rematch = re.match(STATUS_REGEX, line)
    if rematch:
        # matched a Github-style task.
        status = "DONE" if rematch.group(1) == "x" else "TODO"
    else:
        rematch = re.match(KEYWORD_REGEX, line)
        if rematch:
            # matched a keyword-style task.
            status = rematch.group(1)
        else:
            # doesn't look like a task.
            return

    summary = line[len(rematch.group(0)) :].strip()
    if len(summary) == 0:
        # skip tasks without a summary.
        return

    # map keywords -> vtodo status.
    if status in KEYWORD_MAP:
        status = KEYWORD_MAP[status]

    todo = Todo()
    # map todo.txt tags -> vtodo fields.
    for key, value in re.findall(TAGS_REGEX, summary):
        if key in TAG_PARSE:
            parse = TAG_PARSE[key]
            parsed_value = parse(value)
            if value:
                todo.add(key, parsed_value)
                # cleanup the summary (note the space)
                summary = summary.replace(" {}:{}".format(key, value), " ")

    # generate a vtodo uid based on the summary checksum (can be useful with caldav sync)
    todo.add("uid", hashlib.sha256(line.encode("utf-8")).hexdigest())
    if not "dtstamp" in todo:
        todo.add("dtstamp", datetime.now())
    todo["status"] = status
    todo["summary"] = summary
    return todo


def make_calendar(args):
    cal = Calendar()
    for infile in args.infile:
        for line in infile:
            todo = make_todo(line)
            if todo:
                cal.add_component(todo)

    try:
        # line endings are part of the iCal standard, so if we're writing to a file
        # we need to write the bytes.
        args.outfile.write(cal.to_ical())
    except TypeError:
        # Writing to stdout is a bit different, as it requires an str on Linux. On
        # Windows stdout accepts a byte.
        args.outfile.write(cal.to_ical().decode("utf-8"))


load_dotenv()

parser = argparse.ArgumentParser(
    description="Converts TODOs in a text file into an iCal file."
)
parser.add_argument(
    "infile",
    nargs="*",
    type=argparse.FileType("r", encoding="utf-8"),
    default=os.getenv("infile"),
)
parser.add_argument(
    "--outfile", type=argparse.FileType("wb"), default=os.getenv("outfile") or "-"
)

make_calendar(parser.parse_args())
