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

# Imports

import argparse

from PIL import Image, ImageDraw

# Draw a drid image.
def draw_drid():
    im = Image.new("RGB", (args.width, args.height), "white")
    draw = ImageDraw.Draw(im)

    # Find the midpoint.
    mid_x = args.width//2
    mid_y = args.height//2

    for x in range(0, mid_x, args.step):
        draw.line((mid_x + x, 0) + (mid_x + x, args.height - 1), fill="black")
        draw.line((mid_x - x, 0) + (mid_x - x, args.height - 1), fill="black")

    for y in range(0, mid_y, args.step):
        draw.line((0, mid_y + y) + (args.width - 1, mid_y + y), fill="black")
        draw.line((0, mid_y - y) + (args.width - 1, mid_y - y), fill="black")

    im.save(args.image)

# Parse the command line arguments and store the result in 'args'.
def parse_args():
    global args

    parser = argparse.ArgumentParser(
        description="Create a grid image.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # The following is sorted by long argument.

    parser.add_argument("-y", "--height", type=int, default=1080,
        help="Height of the image created.")
    parser.add_argument("-s", "--step", type=int, default=10,
        help="Step between grid lines.")
    parser.add_argument("-x", "--width", type=int, default=1920,
        help="Width of the image created.")
    parser.add_argument("image", metavar="IMAGE",
        help="Output image filename.")

    args = parser.parse_args()

    return args

# Main

parse_args()
draw_drid()