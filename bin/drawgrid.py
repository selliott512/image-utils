#!/usr/bin/env python

# draw-drid.py - Draw a grid image
# Copyright (C)2019 Steven Elliott
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from __future__ import print_function

import os
import sys

from PIL import Image, ImageDraw

if len(sys.argv) != 5:
    print("Usage: " + sys.argv[0] + " fname width height step", file=sys.stderr)
    sys.exit(1)

fname = sys.argv[1]
width = int(sys.argv[2])
height = int(sys.argv[3])
step = int(sys.argv[4])

im = Image.new("RGB", (width, height), "white")

draw = ImageDraw.Draw(im)

for x in range(0, width, step):
    draw.line((x, 0) + (x, height - 1), fill="black")

for y in range(0, height, step):
    draw.line((0, y) + (width - 1, y), fill="black")

im.save(fname)
