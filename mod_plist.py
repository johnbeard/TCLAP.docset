#! /usr/bin/env python

import plistlib
import sys

import argparse
import logging


def open_infile(filename):
    # can't use stdin, not seekable. Could read to a buffer, but..eh
    return open(filename, 'rb')


def open_outfile(filename):
    return open(filename, 'wb') if filename else sys.stdout.buffer


def close_file(handle):

    if handle is not sys.stdout and handle is not sys.stdin:
        handle.close()


def main():

    parser = argparse.ArgumentParser(description='A very simple PList editor.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='show debugging information')
    parser.add_argument('-i', '--infile', required=True,
                        help='the input file')
    parser.add_argument('-o', '--outfile',
                        help='the output file, omit for stdout')
    parser.add_argument('-d', '--delete', action='append', metavar="KEY",
                        help='delete entries with the given key')
    parser.add_argument('-s', '--string', action='append', nargs=2,
                        metavar=("KEY", "VALUE"),
                        help='add a string value or change an existing one')
    parser.add_argument('-t', '--true', action='append', metavar="KEY",
                        help='add a boolean true with the given key')
    parser.add_argument('-f', '--false', action='append', metavar="KEY",
                        help='add a boolean false with the given key')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    logging.debug("Modifying plist {}".format(args.infile))

    ifhandle = open_infile(args.infile)
    plist = plistlib.load(ifhandle)
    close_file(ifhandle)

    if args.string:
        for key, val in args.string:
            logging.debug("Adding key {}: {}".format(key, val))
            plist[key] = val

    if args.delete:
        for key in args.delete:
            logging.debug("Deleting key {}".format(key))
            del plist[key]

    if args.true:
        for key in args.true:
            logging.debug("Adding true key {}".format(key))
            plist[key] = True

    if args.false:
        for key in args.false:
            logging.debug("Adding false key {}".format(key))
            plist[key] = False

    ofhandle = open_outfile(args.outfile)
    plistlib.dump(plist, ofhandle)
    close_file(ofhandle)


if __name__ == "__main__":
    main()
