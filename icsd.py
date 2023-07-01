#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from lib import make_calendar
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Converts TODOs in a text file into an iCal file."
)

parser.add_argument(
    "infile",
    nargs="?",
    type=argparse.FileType("r", encoding="utf-8"),
    default=os.getenv("infile"),
)
parser.add_argument("--port", default=os.getenv("port") or 8000)
parser.add_argument("--host", default=os.getenv("host") or "localhost")
args = parser.parse_args()


class CalendarHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/calendar")
        self.end_headers()
        cal = make_calendar(args.infile)
        self.wfile.write(cal.to_ical())


with HTTPServer((args.host, args.port), CalendarHandler) as httpd:
    logger.info("serving at port {}".format(args.port))
    httpd.serve_forever()
