#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from lib import make_calendar
from dotenv import load_dotenv
import argparse
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Converts TODOs in a text file into an iCal file."
)

parser.add_argument(
    "infile",
    nargs="?",
    type=str,
    default=os.getenv("infile"),
)
parser.add_argument("--port", type=int, default=os.getenv("port") or 8000)
parser.add_argument("--host", default=os.getenv("host") or "localhost")
args = parser.parse_args()


class CalendarHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # TODO check the file exists and is readable
        with open(file=args.infile, mode="r", encoding="utf-8") as infile:
            self.send_response(200)
            self.send_header("Content-Type", "text/calendar")
            self.end_headers()
            cal = make_calendar(infile)
            self.wfile.write(cal.to_ical())


with HTTPServer((args.host, args.port), CalendarHandler) as httpd:
    logger.info("serving at port {}".format(args.port))
    httpd.serve_forever()
