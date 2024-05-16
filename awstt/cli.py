# -*- coding: utf-8 -*-

import sys
import textwrap
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter, RawTextHelpFormatter

from awstt.executor import execute
from awstt.worker import *


class RawFormatter(RawTextHelpFormatter, RawDescriptionHelpFormatter):
    """Formats argument help which maintains line length restrictions as well as appends default value if present."""

    def _split_lines(self, text, width):
        wrapper = textwrap.TextWrapper(width=width)
        lines = []
        for line in text.splitlines():
            if len(line) > width:
                lines.extend(wrapper.wrap(line))
            else:
                lines.append(line)
        return lines


def run():
    parser = ArgumentParser(
        prog="awstt",
        description="AWS-Tag-Tools: A bulk management tool for the tags of AWS resources",
        formatter_class=RawFormatter,
        usage=SUPPRESS,
    )

    parser.add_argument(
        "--key",
        type=str,
        required=False,
        help="the key of tag will be tagged to resources",
    )
    parser.add_argument(
        "--value",
        type=str,
        required=False,
        help="the value of tag will be tagged to resources",
    )
    parser.add_argument(
        "--overwrite",
        required=False,
        default=False,
        action="store_true",
        help="whether to overwrite exists value of tag when key is existed\ndefault to `False`",
    )
    parser.add_argument(
        "--regions",
        type=str,
        required=False,
        help="the AWS regions to execute actions\nwill auto detect if not set\nuse `','` to separate multi regions",
    )
    parser.add_argument(
        "--profile",
        type=str,
        required=False,
        help="the name of AWS credentials profile to use",
    )
    parser.add_argument(
        "--partition",
        type=str,
        required=False,
        choices=["aws", "aws-cn", "aws-us-gov"],
        default="aws",
        help="the partition to execute actions, must be one of `'aws' | 'aws-cn' | 'aws-us-gov'`\ndefault to `'aws'`",
    )
    parser.add_argument(
        "--list-services",
        required=False,
        action="store_true",
        help="list all supported services by this tool and exit",
    )

    args = parser.parse_args()

    if args.list_services is True:
        print("==== supported services ====")
        workers = Scanner.list_available()
        for worker in workers:
            print(f" --> {worker}")

        sys.exit(0)

    if args.key is None or args.value is None:
        parser.print_help(sys.stderr)
        sys.exit(1)

    execute(
        dict(
            partition=args.partition,
            regions=args.regions,
            profile=args.profile,
            tag_key=args.key,
            tag_value=args.value,
            overwrite=args.overwrite,
        ),
        None,
    )
