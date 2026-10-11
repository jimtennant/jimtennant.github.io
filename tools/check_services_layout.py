#!/usr/bin/env python3
"""Regression check for the Services page heading structure."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path


class ServicesPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_main = False
        self.in_content = False
        self.main_headings: list[tuple[str, str, list[str]]] = []
        self._current_heading: tuple[str, list[str], list[str]] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()

        if tag == "main":
            self.in_main = True
        elif self.in_main and tag == "div" and "content" in classes:
            self.in_content = True

        if self.in_main and tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._current_heading = (tag, classes, [])

    def handle_data(self, data: str) -> None:
        if self._current_heading is not None:
            self._current_heading[2].append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._current_heading is not None and tag == self._current_heading[0]:
            heading_tag, classes, text_parts = self._current_heading
            text = " ".join("".join(text_parts).split())
            self.main_headings.append((heading_tag, text, classes.copy()))
            self._current_heading = None

        if tag == "div" and self.in_content:
            self.in_content = False
        elif tag == "main":
            self.in_main = False


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} PATH_TO_SERVICES_HTML", file=sys.stderr)
        return 2

    html_path = Path(sys.argv[1])
    parser = ServicesPageParser()
    parser.feed(html_path.read_text(encoding="utf-8"))

    h1s = [heading for heading in parser.main_headings if heading[0] == "h1"]
    expected = [("h1", "Services", ["dynamic-title"])]
    if h1s != expected:
        print(
            "Services page must have exactly one main H1 supplied by the page layout.\n"
            f"Expected: {expected}\n"
            f"Actual:   {h1s}",
            file=sys.stderr,
        )
        return 1

    print("Services layout check passed: one layout-owned H1 and no duplicate content H1.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
