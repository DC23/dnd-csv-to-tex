#!/usr/bin/env python
import argparse
import csv
from pathlib import Path


def escape_tex_line(line: str):
    for x in "&%{}":
        line = line.replace(x, f"\\{x}")
    return line


class LineParser:
    "Parses individual lines from an input file"

    # TABLE_HEADER is used as a format pattern, so curly braces have to be escaped
    TABLE_HEADER = """\\tableheading{{{table_name}}}{label}
\\begin{{DndTable}}[]{{{column_formats}}}\n"""

    TABLE_HEADER_NAME_AS_HEADER = (
        "\\begin{{DndTable}}[header={table_name}]{{{column_formats}}}{label}\n"
    )
    TABLE_HEADER_NO_NAME = "\\begin{{DndTable}}[]{{{column_formats}}}{label}\n"

    def __init__(
        self,
        label_prefix: str = "",
        escape_content: bool = True,
        name_as_header: bool = False,
        no_name: bool = False,
        no_format_first_row: bool = False,
    ) -> None:
        self._escape_content = escape_content
        self._name_as_header = name_as_header
        self._no_name = no_name
        self._no_format_first_row = no_format_first_row
        self._no_default_numbers = False
        self._emit_label = False
        self._label_prefix = label_prefix

    def _clean(self, value):
        value = value.strip()
        return escape_tex_line(value) if self._escape_content else value

    def parse_table_footer(self, f):
        f.write("\\end{DndTable}")

    def parse_first_line(self, output_file, line):
        table_name = line[0].strip()
        table_name = escape_tex_line(table_name) if self._escape_content else table_name
        try:
            column_format = line[1].strip()
        except IndexError:
            column_format = "c X"

        try:
            file_options = line[2].split(" ")
            self._no_name = "no-name" in file_options
            self._name_as_header = "name-as-header" in file_options
            self._no_format_first_row = "no-format-first-row" in file_options
            self._no_default_numbers = "no-default-numbers" in file_options
            self._emit_label = "emit-label" in file_options
        except IndexError:
            pass

        label = f"\\label{{{self._label_prefix}{table_name.replace(' ', '_').replace(':', '').lower()}}}" if self._emit_label else ""
        if self._no_name:
            output_file.write(
                self.TABLE_HEADER_NO_NAME.format(column_formats=column_format, label=label)
            )
        else:
            fmt = (
                self.TABLE_HEADER_NAME_AS_HEADER
                if self._name_as_header
                else self.TABLE_HEADER
            )
            output_file.write(
                fmt.format(
                    table_name=table_name,
                    column_formats=column_format,
                    label=label,
                )
            )

    def parse_table_entry(self, output_file, line, row_num):
        def write(x, suffix=" & "):
            if row_num == 0 and not self._no_format_first_row:
                prefix = r"\columnheader{"
                suffix = "}" + suffix
            else:
                prefix = ""

            if self._no_default_numbers:
                output_file.write(f"{prefix}{self._clean(x) if x else ' '}{suffix}")
            else:
                output_file.write(f"{prefix}{self._clean(x) if x else row_num}{suffix}")

        for x in line[0:-1]:
            write(x)
        write(line[-1], suffix="\\\\\n")


class TableParser:
    "The common parsing algorithm. This code is invariant across all output options."

    def __init__(
        self,
        line_parser,
        input_file: str,
        output_file: str,
        delimiter: str,
    ):
        self.line_parser = line_parser
        self._input_file = Path(input_file)
        self._output_file = Path(output_file)
        self._delimiter = delimiter

    def parse(
        self,
    ):
        with open(self._output_file, "w") as output_file:
            with open(self._input_file) as input_file:
                input_reader = csv.reader(input_file, delimiter=self._delimiter)
                row_num = 0
                for line in input_reader:
                    if row_num == 0:
                        # Parse metadata from the first line
                        self.line_parser.parse_first_line(output_file, line)
                    else:
                        # a table row
                        self.line_parser.parse_table_entry(
                            output_file, line, row_num - 1
                        )

                    row_num += 1

            self.line_parser.parse_table_footer(output_file)


if __name__ == "__main__":

    # command line options
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-d",
        "--dont-escape-content",
        action="store_true",
        help="Don't escape LaTeX symbols in the row content. Allows LaTeX markup in the text file",
    )
    arg_parser.add_argument("-i", "--input", type=str, help="Input file")
    arg_parser.add_argument("-o", "--output", type=str, help="Output file")
    arg_parser.add_argument("-p", "--label-prefix", type=str, default="", help="Label prefix")
    arg_parser.add_argument(
        "-l", "--delimiter", type=str, default="|", help="Input file delimiter"
    )
    arg_parser.add_argument(
        "-x",
        "--no-name",
        action="store_true",
        help="Do not emit a table name at all.",
    )
    arg_parser.add_argument(
        "-n",
        "--name-as-header",
        action="store_true",
        help="Embed the table name as a header in the table rather than using the \\tableheading macro",
    )
    arg_parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Print the version number and exit.",
    )
    arg_parser.add_argument(
        "-r",
        "--no-format-first-row",
        action="store_true",
        help="Do not apply formatting to the first content row.",
    )
    args = arg_parser.parse_args()

    if args.version:
        print(f"{__file__} 1.4.2")
        exit()

    if not args.input or not args.output:
        arg_parser.print_usage()
        exit()

    parser = TableParser(
        LineParser(
            args.label_prefix,
            not args.dont_escape_content,
            args.name_as_header,
            args.no_name,
            args.no_format_first_row,
        ),
        args.input,
        args.output,
        args.delimiter,
    )
    parser.parse()
