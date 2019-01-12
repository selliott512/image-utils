#!/usr/bin/env python3

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
