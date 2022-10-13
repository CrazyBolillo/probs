import argparse
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("file", help="File containing ISPs' information")
    parser.add_argument("output", help="Path where output will be written to")
    args = parser.parse_args()

    config = {}
    with open(os.path.abspath(args.file), 'r') as fl:
        config = json.load(fl)

    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "../templates")),
        autoescape=select_autoescape()
    )
    template = env.get_template("report.html")
    with open(os.path.abspath(args.output), 'w') as fl:
        fl.write(template.render(**config))


if __name__  == "__main__":
    main()
