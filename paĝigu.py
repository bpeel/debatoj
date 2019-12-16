#!/usr/bin/env python3

import gi
gi.require_version('Pango', '1.0')
from gi.repository import Pango
gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo
import cairo
import re

POINTS_PER_MM = 2.8346457

PAGE_WIDTH = 210
PAGE_HEIGHT = 297

COLUMNS = 2
ROWS = 11
ENTRIES_PER_PAGE = COLUMNS * ROWS

FONT = "Sans 4"

TEXT_INSET = 5.0

class Generator:
    def __init__(self):
        self.surface = cairo.PDFSurface("debatoj.pdf",
                                        PAGE_WIDTH * POINTS_PER_MM,
                                        PAGE_HEIGHT * POINTS_PER_MM)

        self.cr = cairo.Context(self.surface)

        # Use mm for the units from now on
        self.cr.scale(POINTS_PER_MM, POINTS_PER_MM)

        # Use ½mm line width
        self.cr.set_line_width(0.5)

        self.page_pos = 0

        self.font = Pango.FontDescription.from_string(FONT)

    def flush_page(self):
        self.cr.show_page()
        self.page_pos = 0

    def start_page(self):
        for col in range(1, COLUMNS):
            self.cr.move_to(PAGE_WIDTH * col / COLUMNS, 0)
            self.cr.rel_line_to(0, PAGE_HEIGHT)

        for row in range(1, ROWS):
            self.cr.move_to(0, PAGE_HEIGHT * row / ROWS)
            self.cr.rel_line_to(PAGE_WIDTH, 0)

        self.cr.stroke()

    def add_element(self, text):
        if self.page_pos == 0:
            self.start_page()

        layout = PangoCairo.create_layout(self.cr)
        layout.set_font_description(self.font)
        layout.set_text(text + " Debatu.")
        layout.set_alignment(Pango.Alignment.CENTER)
        layout.set_width((PAGE_WIDTH / COLUMNS - TEXT_INSET * 2.0) *
                         Pango.SCALE)
        (ink_rect, logical_rect) = layout.get_pixel_extents()

        self.cr.move_to((self.page_pos % COLUMNS) * PAGE_WIDTH / COLUMNS +
                        TEXT_INSET,
                        (self.page_pos // COLUMNS) * PAGE_HEIGHT / ROWS +
                        PAGE_HEIGHT / ROWS / 2.0 -
                        logical_rect.height / 2.0)
        PangoCairo.show_layout(self.cr, layout)

        self.page_pos += 1

        if self.page_pos >= ENTRIES_PER_PAGE:
            self.flush_page()

generator = Generator()

with open("debatoj.txt", "rt", encoding="utf-8") as f:
    for line in f:
        if re.match(r'^\s*(#|$)', line):
            continue
        generator.add_element(line.strip())
