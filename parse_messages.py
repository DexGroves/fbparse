#!/usr/bin/env python
import argparse
from code.facebook_parser import FacebookParser


parser = argparse.ArgumentParser(description="Process messages.htm to JSON.")
parser.add_argument("path", help="Path to messages.htm")
parser.add_argument("dest", nargs='?', default='parsed_convos',
                    help="Output folder.")

args = parser.parse_args()

print "Parsing..."
fb = FacebookParser(args.path, outpath=args.dest)
print "Success!"
