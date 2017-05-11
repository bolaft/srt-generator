#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
:Name:
srt_generator.py

:Authors:
Soufian Salim (soufi@nsal.im)

:Date:
15/10/16

:Description:
Markovian subtitle generator
"""

import codecs

from progressbar import ProgressBar
from optparse import OptionParser
from sentence_generator import generate_sentence


# Main
def main(opts, args):
    corpus = args[0]
    target = args[1]

    clean_file(target)

    to_write = []

    line_type = "EMPTY"

    p = ProgressBar()

    for line in p(codecs.open(target, encoding="utf-8").readlines()):
        line = line.strip()

        if line == "":
            line_type = "EMPTY"
        else:
            if line_type == "EMPTY":
                line_type = "NUMBER"
            elif line_type == "NUMBER":
                line_type = "TIMESTAMP"
            elif line_type == "TIMESTAMP" or line_type == "DIALOG":
                line_type = "DIALOG"

        if line_type != "DIALOG":
            to_write.append(line)
        else:
            gen_line = generate_sentence(corpus, opts.ngrams, len(line.split(" ")), opts.start)
            to_write.append(str(gen_line))
    output_file = target.replace(".srt", ".{}.srt".format(corpus.split("/")[1].split(".")[0]))
    out = codecs.open(output_file, "w", encoding="utf-8")

    print("Exported generated subtitles to {}".format(output_file))

    for l in to_write:
        out.write(l + "\n")


def clean_file(target):
    to_print = []

    line_type = "EMPTY"

    for line in codecs.open(target, encoding="utf-8").readlines():
        line = line.strip()

        if line == "":
            line_type = "EMPTY"
        else:
            if line_type == "EMPTY":
                line_type = "NUMBER"
            elif line_type == "NUMBER":
                line_type = "TIMESTAMP"
            elif line_type == "TIMESTAMP" or line_type == "DIALOG":
                line_type = "DIALOG"

        to_print.append((line_type, line))

    out = codecs.open(target, "w", encoding="utf-8")
    prev = None
    for t, l in to_print:
        l = l.strip()
        if prev == "DIALOG" and len(l) > 0 and not l[0].isupper():
            out.write(" " + l)
        else:
            out.write("\n" + l)
        prev = t


def parse_args():
    """
    Parses command line options and arguments
    """
    op = OptionParser(usage="usage: %prog [opts] corpus_file subtitle_file")

    op.add_option(
        "-s", "--start",
        dest="start",
        type="string",
        default=False,
        help="start string")

    op.add_option(
        "-n", "--ngrams",
        dest="ngrams",
        type="int",
        default=2,
        help="number of ngrams")

    return op.parse_args()

# Launch
if __name__ == "__main__":
    options, arguments = parse_args()

    if len(arguments) != 2:
        print("This script takes exactly 2 arguments. Use --help for more details.")
    else:
        main(options, arguments)
