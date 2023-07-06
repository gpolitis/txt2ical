#!/usr/bin/env python3

from icalendar import Calendar, Todo
import dateutil.parser
from datetime import datetime
import re
import hashlib

import logging

logger = logging.getLogger(__name__)


# TODO add support for [x]it! (harder because subtasks require context and icalendar does not support sub-tasks)
# TODO add some fuzzy logic to handle minor typos
# TODO add proper unit tests
# TODO add http a server

TAGS_PATTERN = r"([^\s:]+):(?!\/\/)([^\s]+)"
PROJECT_PATTERN = r" \+([^\s]+)"
CONTEXT_PATTERN = r" @([^\s]+)"
DATE_PATTERN = r"([0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?)?)"
STATUS_PATTERNS = [
    # GH_PATTERN
    r"^- \[(?P<status> |x|\@|\~|\^)\] (?:(\(?P<priority>[A-Z]\)) )?(?:(?P<completed>[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?)? )?(?P<created>[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?)?))?",
    # KEYWORD_PATTERN
    r"^- (?P<status>TODO|DONE|EXPIRED|CANCELL?ED|NEEDS-ACTION|COMPLETED|IN-PROCESS|DELEGATED)",
    # TDTXT_PATTERN
    r"^- (?:(?P<status>x) )?(?:(\(?P<priority>[A-Z]\)) )?(?:(?P<completed>[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?)? )?(?P<created>[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?)?))",
]
DESCRIPTION_PATTERN = r" \/\/ (.+)$"

STATUS_EMOJIS = {"IN-PROCESS": "🚧", "CANCELLED": "❌", "DELEGATED": "↗️"}

# setting a default time to 23:59 makes due dates inclusive
DEFAULT_DATETIME = dateutil.parser.isoparse("1970-01-01 23:59")
def parse_date(value):
    # TODO add support for human readable dates https://github.com/scrapinghub/dateparser. Note that dateutil seems to have some fuzzy parsing.
    rematch = re.match(DATE_PATTERN, value)
    date = dateutil.parser.parse(rematch.group(1), default=DEFAULT_DATETIME)
    return date


def parse_status(value):
    # Valid VTODO statuses are listed in the RFC https://www.rfc-editor.org/rfc/rfc5545#section-3.8.1.11
    match value.upper():
        # We mark cancelled as completed because Thunderbird shows cancelled tasks https://bugzilla.mozilla.org/show_bug.cgi?id=382363
        case "CANCELLED" | "EXPIRED" | "DONE" | "X" | "~":
            return "COMPLETED"
        case "TODO" | " ":
            return "NEEDS-ACTION"
        case "@":
            return "IN-PROCESS"
        case "^":
            return "DELEGATED"
        case _:
            raise Exception("Status not recognized: {}".format(value))


TAG_PARSE = {
    "created": parse_date,
    "completed": parse_date,
    "status": parse_status,
    "due": parse_date,
    "start": parse_date,
    "dtstamp": parse_date,
    "location": lambda value: value,
    "categories": lambda value: value.split(","),
}


def make_todo(line):
    tags = dict()

    for status_pattern in STATUS_PATTERNS:
        rematch = re.match(status_pattern, line, re.IGNORECASE)
        if rematch:
            tags.update(rematch.groupdict())
            summary = re.sub(status_pattern, "", line)
            break

    if not rematch:
        # skip tasks without a summary.
        return

    todo = Todo()

    tags.update(dict(re.findall(TAGS_PATTERN, summary)))

    # map various parsed tags into vtodo tags.
    for key, value in tags.items():
        if not key in TAG_PARSE:
            logger.info("An unknown field was detected: {}".format(key))
        if value and key in TAG_PARSE:
            parse = TAG_PARSE[key]
            parsed_value = parse(value)
            if parsed_value:
                todo.add(key, parsed_value)
                # cleanup the summary (note the space) <- FIXME what if there is no space?
                summary = summary.replace("{}:{}".format(key, value), " ")

    todo.add("categories", re.findall(PROJECT_PATTERN, summary))
    summary = re.sub(PROJECT_PATTERN, "", summary)

    todo.add("resources", re.findall(CONTEXT_PATTERN, summary))
    summary = re.sub(CONTEXT_PATTERN, "", summary)

    # generate a vtodo uid based on the summary checksum (can be useful with caldav sync)
    todo.add("uid", hashlib.sha256(line.encode("utf-8")).hexdigest())
    if not "dtstamp" in todo:
        todo.add("dtstamp", datetime.now())

    rematch = re.search(DESCRIPTION_PATTERN, summary)
    if rematch:
        todo.add("description", rematch.group(1))
        summary = re.sub(DESCRIPTION_PATTERN, "", summary)

    if "status" in todo and todo["status"] in STATUS_EMOJIS:
        summary = "{} {}".format(STATUS_EMOJIS[todo["status"]], summary)

    # FIXME if we require a strip here it could mean our patterns are not perfect
    todo.add("summary", summary.strip())
    return todo


def make_calendar(infile):
    cal = Calendar()
    if infile:
        for line in infile:
            todo = make_todo(line)
            if todo:
                cal.add_component(todo)
    return cal
