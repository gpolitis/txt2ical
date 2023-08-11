#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from . import make_calendar
from dotenv import load_dotenv
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert(args):
    cal = make_calendar(args.infile)

    try:
        # line endings are part of the iCal standard, so if we're writing to a file
        # we need to write the bytes.
        args.outfile.write(cal.to_ical())
    except TypeError:
        # Writing to stdout is a bit different, as it requires an str on Linux. On
        # Windows stdout accepts a byte.
        args.outfile.write(cal.to_ical().decode("utf-8"))

def httpd(args):
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

if __name__ == '__main__':
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Converts TODOs in a text file into an iCal file."
    )

    subparsers = parser.add_subparsers(title='subcommands',
                                   description='valid subcommands',
                                   help='additional help')
    httpd_parser = subparsers.add_parser('httpd')
    convert_parser = subparsers.add_parser('convert')

    httpd_parser.add_argument(
        "infile",
        nargs="?",
        type=str,
        default=os.getenv("infile"),
    )
    httpd_parser.add_argument("--port", type=int, default=os.getenv("port") or 8000)
    httpd_parser.add_argument("--host", default=os.getenv("host") or "localhost")
    httpd_parser.set_defaults(func=httpd)

    convert_parser.add_argument(
        "infile",
        nargs="?",
        type=argparse.FileType("r", encoding="utf-8"),
        default=os.getenv("infile"),
    )
    convert_parser.add_argument(
        "--outfile", type=argparse.FileType("wb"), default=os.getenv("outfile") or "-"
    )
    convert_parser.set_defaults(func=convert)

    args = parser.parse_args()
    args.func(args)