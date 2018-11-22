#!/usr/bin/env python

# wad2image - Create equirectangular images from sphere images
# Copyright (C)2018S Steven Elliott
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
import os
import math
import sys

from PIL import Image
from math import radians, sin, pi, cos
from wx._propgrid import new_LongStringProperty

# Globals

as_rad         = 0  # --angular-size in radians.
args           = {} # Command line arguments.
cam_sph_z      = 0  # Z-coordinate of the sphere.
min_z          = 0  # Maximum Z-coordinate to render at tangent.
min_z_ma       = 0  # Maximum Z-coordinate to render given --min-angle.
ndc_inset      = 0  # Inset in NDC coordinates.
scale          = 0  # Scale the output image by this amount.
slope          = 0  # Maximum slope to render.

# Functions

# Write a fatal error message to stderr and exit.
def fatal(msg):
    warn(msg)
    sys.exit(1)

# Parse the command line arguments and store the result in 'args'.
def parse_args():
    global args

    parser = argparse.ArgumentParser(
        description="Create equirectangular images from sphere images.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # The following is sorted by long argument.

    parser.add_argument("-a", "--angular-size", type=float, default=0.0,
        help="Angular size of the sphere.")
    parser.add_argument("-b", "--bilinear", action="store_true",
        help="Use bilinear interpolation instead of nearest.")
    parser.add_argument("--center-lat", type=float, default=0.0,
        help="The latitude at the center of the equirectangular output. "
           + "Helpful for --multi.")
    parser.add_argument("--center-lon", type=float, default=0.0,
        help="The longitude at the center of the equirectangular output. "
           + "Helpful for --multi.")
    parser.add_argument("--crop", action="store_true",
        help="Crop the equirectangular image to written to pixels.")
    parser.add_argument("-f", "--force", action="store_true",
        help="Overwrite the output image.")
    parser.add_argument("--height", type=int, default=0,
        help="Output height. Based on input image by default.")
    parser.add_argument("--in-begin-x", type=int,
        help="X-coordinate of where the sphere begins in the input.")
    parser.add_argument("--in-begin-y", type=int,
        help="Y-coordinate of where the sphere begins in the input.")
    parser.add_argument("--in-size", type=int,
        help="Size of the sphere in the input. Default is fit to input.")
    parser.add_argument("--min-angle", type=float, default=0.0,
        help="Minimum angle line of sight to sphere surface considered.")
    parser.add_argument("-m", "--multi", action="store_true",
        help="Write to the existing output image again.")
    parser.add_argument("--offset-lat", type=float, default=0.0,
        help="Offset output latitude by this amount. Helpful for --multi.")
    parser.add_argument("--offset-lon", type=float, default=0.0,
        help="Offset output longitude by this amount. Helpful for --multi.")
    parser.add_argument("--offset-x", type=int, default=0,
        help="Offset output X by this amount. Helpful for --multi.")
    parser.add_argument("--offset-y", type=int, default=0,
        help="Offset output Y by this amount. Helpful for --multi.")
    parser.add_argument("-o", "--output",
        help="Output filename. Default to adding \"-er\" to original name.")
    parser.add_argument("-s", "--stretch", action="store_true",
        help="Stretch to fill the equirectangular map region.")
    parser.add_argument("-v", "--verbose", action="store_true",
        help="Verbose.")
    parser.add_argument("-w", "--width", type=int, default=0,
        help="Output width. Based on input image by default.")
    parser.add_argument("images", metavar="IMAGE", nargs="+",
        help="Input spherical images.")

    args = parser.parse_args()

    if len(args.images) > 1 and args.output:
        # TODO: Come up with a format specifier system to allow a template to
        # be specified.
        fatal("The \"-o\" option can not be used with multiple images.")

    return args

# Process a particular image.
def process_image(in_fname, out_fname):
    verbose("Processing input image \"" + in_fname + "\" to output image \""
            + out_fname + "\".")

    in_im = Image.open(in_fname)
    in_width, in_height = in_im.size

    min_in = min(in_width, in_height)
    if args.in_size:
        in_size = args.in_size
    else:
        in_size = min_in
    in_size_2 = in_size / 2.0

    if args.in_begin_x is None:
        in_begin_x = int((min_in - in_size) / 2)
    else:
        in_begin_x = args.in_begin_x

    if args.in_begin_y is None:
        in_begin_y = int((min_in - in_size) / 2)
    else:
        in_begin_y = args.in_begin_y

    if max(in_begin_x, in_begin_y) + in_size > min_in:
        fatal("For input image \"" + in_fname + "\" the region specified "
                + "won't fit into " + str(min_in) + " pixels. Try "
                + "specifying --in-size, or a lower value for it.")

    if not args.width and not args.height:
        # Neither the width nor height was specified. Use the height of the
        # input image.
        out_height = in_size
        out_width = 2 * in_size
    elif args.width and args.height:
        # Both  the height and width was specified, so use that.
        out_width = args.width
        out_height = args.height
        if out_width != 2 * out_height:
            fatal("The width must be exactly twice the height. Try specifying "
                  + "only one of --width or --height, or neither.")
    elif args.width:
        # Width specified, but not height.
        out_width = args.width
        out_height = out_width // 2
    else:
        # Height specified, but not width.
        out_height = args.height
        out_width = 2 * out_height

    # Create the output image making use of the existing image if --multi was
    # specified.
    out_im = None
    if os.path.isfile(out_fname):
        if args.multi:
            out_im = Image.open(out_fname)
            # Override out_width and out_height with the the values actually
            # used. Perhaps this should be a warning if either --width or
            # --height was specified.
            out_width, out_height = out_im.size
        elif not args.force:
            fatal("Output image file \"" + out_fname + "\" exists, but "
                  + "neither --multi nor --force was specified")
    if not out_im:
        out_im = Image.new("RGB", (out_width, out_height))
    out_pix = out_im.load()

    # Determine the bounds of the equirectangular map region in the output
    # image. If --stretch is not specified then this will be +- 90 degrees
    # both dimensions.
    if out_width >= out_height:
        # The normal default cause as well as the --full case.
        eq_size = out_height
        eq_begin_x = int((out_width - out_height)/2)
        eq_begin_y = 0
    else:
        # Unusual case.
        eq_size = out_width
        eq_begin_x = 0
        eq_begin_y = int((out_height - out_width)/2)
    eq_end_x = eq_begin_x + eq_size
    eq_end_y = eq_begin_y + eq_size

    # TODO: Offset really only works accurately for longitude. Latitude offset
    # adds a lot of distortion, so it's probably only suitable for small
    # corrections. This should be approached differently by rotating the unit
    # sphere.
    total_offset_x = int(round(eq_size*(args.offset_lon/180.0) +
                               args.offset_x))
    total_offset_y = int(round(eq_size*(-args.offset_lat/180.0) +
                               args.offset_y))
    eq_begin_x += total_offset_x
    eq_begin_y += total_offset_y
    eq_end_x += total_offset_x
    eq_end_y += total_offset_y

    # Determine the number of pixels that the writable region is inset in the
    # equirectangular map. This is only non-zero if the --angular-size was
    # specified, which means that less than a full hemisphere is visible.
    # the image rendered pixels are not stretched to fill the equirectangular
    # map region.
    inset = int(ndc_inset * eq_size)

    # Avoid references to globals in the loop.
    bl = args.bilinear
    slp = slope
    c_lat = -radians(args.center_lat)
    c_lon = radians(args.center_lon)
    crop = args.crop

    # Ranges that are needed when the image is cropped.
    out_x_min = 9999999
    out_x_max = 0
    out_y_min = 9999999
    out_y_max = 0

    # "2.0" (float) used to allow the center of the center pixel to be chosen
    # in the case where the height is odd.
    in_pix = in_im.load()
    for out_x in range(0, out_width):
        # The "+ 0.5" is to get the longitude at the center of the pixel.
        lon = 2 * math.pi * (((out_x + 0.5)/out_width) - 0.5) / scale - c_lon
        for out_y_range in range(eq_begin_y + inset, eq_end_y - inset):
            out_y = out_y_range % out_height
            # The "+ 0.5" is to get the latitude at the center of the pixel.
            # This also prevents abs(sin(lon)) from being 1.0, so in_x and in_y
            # are always in the range [0, out_height).
            lat = -math.pi * ((((out_y - eq_begin_y) + 0.5)/eq_size) -
                             0.5) / scale

            # Convert from spherical coordinates to camera coordinates. The
            # sphere has radius one and it's centered at (0, 0, cam_sph_z) in
            # the camera coordinate system.
            # TODO: Rename based on coordinate system.
            cam_x = cos(lat) * sin(lon)
            cam_y = sin(lat)
            cam_z = cos(lat) * cos(lon)

            if c_lat:
                # Rotate the unit sphere around the X-axis in order to bring
                # the closest point to the camera up along the closest meridian
                # to that latitude.
                cam_y = cam_y*cos(c_lat) - cam_z*sin(c_lat)
                cam_z = cam_z*cos(c_lat) + cam_y*sin(c_lat)

            # For orthographic cam_sph_z is 0.
            cam_z += cam_sph_z

            if cam_z < min_z_ma:
                # Not on the visible portion of the sphere.
                continue

            # Convert from camera coordinates to NDC (Normalized Device
            # Coordinates) with range [-1, 0).
            if as_rad:
                # Perspective, hard case.
                ndc_x = -cam_x/(slp*cam_z)
                ndc_y = -cam_y/(slp*cam_z)
            else:
                # Orthographic, simple case.
                ndc_x = cam_x
                ndc_y = cam_y

            # Convert from NDC coordinates to pixel coordinates. Note the "-"
            # for ndc_y since the Y-axis is the opposite direction for pixel
            # coordinates.
            in_x = in_begin_x + in_size_2*(1 + ndc_x)
            in_y = in_begin_y + in_size_2*(1 - ndc_y)

            color = (255, 0, 255) # Revert once center is debugged.
            if bl:
                # Bilinear interpolation. This is a weighted average of the
                # four surrounding pixels.

                # Get the surrounding pixels clipped into bounds.
                l_x = in_x - 0.5 if (in_x - 0.5) >= 0.0 else 0.0
                h_x = in_x + 0.5 if (in_x + 0.5) < in_height else in_height - 1.0
                l_y = in_y - 0.5 if (in_y - 0.5) >= 0.0 else 0.0
                h_y = in_y + 0.5 if (in_y + 0.5) < in_height else in_height - 1.0

                # The colors surrounding in_x and in_y
                color_ll = in_pix[l_x, l_y]
                color_lh = in_pix[l_x, h_y]
                color_hl = in_pix[h_x, l_y]
                color_hh = in_pix[h_x, h_y]

                # The fraction of the way from the low color to the high color.
                frac_l_x = (in_x + 0.5) % 1.0
                frac_l_y = (in_x + 0.5) % 1.0
                frac_h_x = 1.0 - frac_l_x
                frac_h_y = 1.0 - frac_l_y

                # Create a new color, starting as an array, where each color
                # is weighted by the area opposite the pixel being considered.
                # The "+ 0.5" is to round. This should be guaranteed to produce
                # tuples in the range (0, 0, 0) to (255, 255, 255) since the
                # individual colors are in that range, and since the sum of the
                # area weights is 1.0.
                color_ar = [None] * 3
                for i in range(3):
                    color_ar[i] = int(color_ll[i] * frac_h_x * frac_h_y + \
                                      color_lh[i] * frac_h_x * frac_l_y + \
                                      color_hl[i] * frac_l_x * frac_h_y + \
                                      color_hh[i] * frac_l_x * frac_l_y + 0.5)
                color = tuple(color_ar)
            else:
                # Nearest interpolation. This []s implicitly floor the values,
                # which helpful since each rectangular pixel region is labeled
                # by it's lowest X and Y coordinates.

                color = in_pix[in_x, in_y]
            out_pix[out_x, out_y] = color

            # TODO: it should be possible to calculate the bounds
            # programmatically in most cases.
            if crop:
                if out_x < out_x_min:
                    out_x_min = out_x
                elif out_x > out_x_max:
                    out_x_max = out_x
                if out_y < out_y_min:
                    out_y_min = out_y
                elif out_y > out_y_max:
                    out_y_max = out_y

    if crop:
        out_im = out_im.crop((out_x_min, out_y_min, out_x_max + 1, out_y_max + 1))
    out_im.save(out_fname)

# Process the images.
def process_images():
    for in_fname in args.images:
        dot = in_fname.rindex(".")
        if args.output:
            out_fname = args.output
        else:
            out_fname = in_fname[:dot] + "-er" + in_fname[dot:]
        process_image(in_fname, out_fname)

# Update globals that are necessary to render the scene.
def update_scene():
    global as_rad
    global cam_sph_z
    global min_z
    global min_z_ma
    global ndc_inset
    global scale
    global slope

    # Calculate maximum angle between the line of sight (Z-axis) and a
    # rendered point on the sphere. This is where the line of sight is
    # tangential to the sphere's surface.
    as_rad = radians(args.angular_size)
    as_rad_2 = as_rad / 2.0
    as_rad_2_ma = as_rad_2 + radians(args.min_angle)
    max_xy = cos(as_rad_2)
    min_z_rel = sin(as_rad_2)
    min_z_rel_ma = sin(as_rad_2_ma)
    if as_rad_2:
        cam_sph_z = -1.0 / min_z_rel
        min_z = cam_sph_z + min_z_rel
        min_z_ma = cam_sph_z + min_z_rel_ma
        slope = -max_xy/min_z
    else:
        min_z_ma = min_z_rel_ma
    as_frac = as_rad_2_ma / (pi / 2.0) # Fraction of the way to 90 degrees.
    if args.stretch:
        scale = 1/(1 - as_frac)
        ndc_inset = 0
    else:
        scale = 1.0
        ndc_inset = as_frac / 2.0
    ndc_inset = 0 # Restore when center is working correctly.

# Log a message to stdout if verbose.
def verbose(msg):
    if args.verbose:
        print(msg)

# Print a warning to stderr. It's flushed.
def warn(msg):
    print(msg, file=sys.stderr)
    sys.stderr.flush()

# Main

parse_args()
update_scene()
process_images()
