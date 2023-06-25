#!/usr/bin/env python3

import os
from icalendar import Calendar, Todo
import sys
import argparse
import re
from dotenv import load_dotenv

#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)

STATUS_REGEX = r"^- \[( |x)\]"
KEYWORD_REGEX = r"^- (TODO|DONE|EXPIRED|CANCELLED|NEEDS-ACTION|COMPLETED|IN-PROCESS)"

# Valid VTODO statuses are listed in the RFC https://www.rfc-editor.org/rfc/rfc5545#section-3.8.1.11
# We mark cancelled as completed because Thunderbird shows cancelled tasks https://bugzilla.mozilla.org/show_bug.cgi?id=382363
KEYWORD_MAP = {
    'TODO': '',
    'DONE': 'COMPLETED', 
    'EXPIRED': 'COMPLETED',
    'CANCELLED': 'COMPLETED'
}

def make_todo(line):
    rematch = re.match(STATUS_REGEX, line)
    if rematch:
        # Github-style task.
        status = "DONE" if rematch.group(1) == "x" else "TODO"
    else:
        rematch = re.match(KEYWORD_REGEX, line)
        if rematch:
            # keyword-style task.
            status = rematch.group(1)
        else:
            # not a task.
            return
    
    summary = line[len(rematch.group(0)):].strip()
    if len(summary) == 0:
        # task without a summary.
        return
    
    # map keywords -> vtodo status.
    if status in KEYWORD_MAP:
        status = KEYWORD_MAP[status]

    todo = Todo()
    todo["status"] = status
    todo["summary"] = summary
    return todo

def make_calendar(infile):
    cal = Calendar()
    for line in infile:
        todo = make_todo(line)
        if todo:
            cal.add_component(todo)
    return cal

def txt2ics(args):
    cal = make_calendar(args.infile)
    try:
        # line endings are part of the iCal standard, so if we're writing to a file
        # we need to write the bytes.
        args.outfile.write(cal.to_ical())
    except TypeError:
        # Writing to stdout is a bit different, as it requires an str on Linux. On
        # Windows stdout accepts a byte.
        args.outfile.write(cal.to_ical().decode("utf-8"))

load_dotenv()

parser = argparse.ArgumentParser(description='Converts TODOs in a text file into an iCal file.')
parser.add_argument('infile', nargs='?', type=argparse.FileType('r', encoding="utf-8"), default=os.getenv("infile"))
parser.add_argument('outfile', nargs='?', type=argparse.FileType('wb'), default=os.getenv("outfile"))

txt2ics(parser.parse_args())
