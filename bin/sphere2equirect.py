#!/usr/bin/env python

# sphere2equirect.py - Create equirectangular images from sphere images
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
import sys

from PIL import Image
from math import cos, pi, radians, sin

# Globals

args           = {} # Command line arguments.
as_rad         = 0  # --angular-size in radians.
cam_sph_z      = 0  # Z-coordinate of the sphere.
min_z_ma       = 0  # Maximum Z-coordinate to render given --min-angle.
slope          = 0  # Maximum slope to render.

# Functions

# Write a fatal error message to stderr and exit.
def fatal(msg):
    print(msg, file=sys.stderr)
    sys.stderr.flush()
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
        help="The latitude at the center of the sphere in the input image. "
           + "Helpful for --multi.")
    parser.add_argument("--center-lon", type=float, default=0.0,
        help="The longitude at the center of the sphere in the input image. "
           + "Helpful for --multi.")
    parser.add_argument("-c", "--crop", action="store_true",
        help="Crop the output image to the smallest rectangle possible such "
           + "that only hidden pixels are removed.")
    parser.add_argument("-f", "--force", action="store_true",
        help="Overwrite the output image.")
    parser.add_argument("--height", type=int, default=0,
        help="Output image height. Based on the input image by default.")
    parser.add_argument("--hidden-color", type=str, default="black",
        help="Color to use for hidden pixels. Hidden pixels are pixels in the "
           + "output image that correspond to locations on the sphere in the "
           + "input image that are not visible to the camera.")
    parser.add_argument("-x", "--in-begin-x", type=int,
        help="X-coordinate of where the sphere begins in the input image "
           + "(inclusive).")
    parser.add_argument("-y", "--in-begin-y", type=int,
        help="Y-coordinate of where the sphere begins in the input image "
           + "(inclusive).")
    parser.add_argument("--in-end-x", type=int,
        help="X-coordinate of where the sphere ends in the input image "
           + "(exclusive).")
    parser.add_argument("--in-end-y", type=int,
        help="Y-coordinate of where the sphere ends in the input image "
           + "(exclusive).")
    parser.add_argument("-s", "--in-size", type=int,
        help="Size (diameter) of the sphere in the input image. This can be "
           + "overridden per dimension by the -in-size-* options. Default is "
           + "the diameter of the largest circle that will fit in the input "
           + "image.")
    parser.add_argument("--in-size-x", type=int,
        help="Horizontal size (width) of the sphere in the input image. "
           + "Default is the diameter of the largest circle that will fit in "
           + "the input image or --in-size if specified.")
    parser.add_argument("--in-size-y", type=int,
        help="Vertical size (height) of the sphere in the input image. "
           + "Default is the diameter of the largest circle that will fit in "
           + "the input image or --in-size if specified.")
    parser.add_argument("--min-angle", type=float, default=0.0,
        help="Minimum angle between line of sight and the surface of the "
           + "sphere. Pixels less than this will be hidden. Helpful when the "
           + "perimeter of the sphere is distorted.")
    parser.add_argument("-m", "--multi", action="store_true",
        help="Multiple write. If there is an existing image at the output "
           + "location then open it for write. This is helpful when "
           + "producing a map from multiple input images where each input "
           + "image is a portion of the entire sphere.")
    parser.add_argument("-o", "--output",
        help="Output filename. Default to adding \"-er\" to the basename "
           + "(before the extension) of the original filename.")
    parser.add_argument("-q", "--quiet", action="store_true",
        help="Quiet. Suppress output (warnings).")
    parser.add_argument("-r", "--rotate", type=float, default=0.0,
        help="Number of degrees the sphere in the input image is rotated "
           + "clockwise. The North pole at the top of the sphere is zero "
           + "degrees of rotation.")
    parser.add_argument("-v", "--verbose", action="store_true",
        help="Verbose. Additional output.")
    parser.add_argument("-w", "--width", type=int, default=0,
        help="Output image width. Based on the input image by default.")
    parser.add_argument("images", metavar="IMAGE", nargs="+",
        help="Sphere input images.")

    args = parser.parse_args()

    # Make sure that the options are consistent.

    if len(args.images) > 1 and args.output:
        # TODO: Come up with a format specifier system to allow a template to
        # be specified.
        fatal("The \"-o\" option can not be used with multiple images.")

    return args

# Process a particular image.
def process_image(in_fname, out_fname):
    verbose("Processing input image \"" + in_fname + "\" to output image \""
            + out_fname + "\".")

    if not os.path.isfile(in_fname):
        fatal("Input image \"" + in_fname + "\" does not exist.")

    in_im = Image.open(in_fname)
    in_width, in_height = in_im.size

    min_in = min(in_width, in_height)

    # The result of the following is that in_size_x and in_size_y will be known
    # whether they are give explicitly or calculated, and the begin, end and
    # size options will all be guaranteed to be consisted.
    in_size_x = args.in_size_x if args.in_size_x else args.in_size
    in_size_y = args.in_size_y if args.in_size_y else args.in_size
    in_begin_x = args.in_begin_x
    in_begin_y = args.in_begin_y
    in_end_x = args.in_end_x
    in_end_y = args.in_end_y
    if in_begin_x is not None and in_end_x is not None:
        in_size_x_calc = args.in_end_x - args.in_begin_x
        if in_size_x and in_size_x_calc != in_size_x:
            fatal("X begin and end specified does not match the size "
                  + str(in_size_x) + " specified.")
        in_size_x = in_size_x_calc
    if in_begin_y is not None and in_end_y is not None:
        in_size_y_calc = args.in_end_y - args.in_begin_y
        if in_size_y and in_size_y_calc != in_size_y:
            fatal("Y begin and end specified does not match the size "
                  + str(in_size_y) + " specified.")
        in_size_y = in_size_y_calc

    # For sizes that could not be determined use diameter of the largest circle
    # that will fit in the input image (min_in).
    if not in_size_x:
        in_size_x = min_in
    if not in_size_y:
        in_size_y = min_in
    in_size_x_2 = in_size_x / 2.0
    in_size_y_2 = in_size_x / 2.0

    # Now that the size is known the ranges can be calculated regardless of what
    # was specified.

    if args.in_begin_x is not None and args.in_end_x is None:
        in_begin_x = args.in_begin_x
        in_end_x = in_begin_x + in_size_x
    elif args.in_begin_x is None and args.in_end_x is not None:
        in_end_x = args.in_end_x
        in_begin_x = in_end_x - in_size_x
    elif args.in_begin_x is None and args.in_end_x is None:
        in_begin_x = (min_in - in_size_x) // 2
        in_end_x = in_begin_x + in_size_x

    if args.in_begin_y is not None and args.in_end_y is None:
        in_begin_y = args.in_begin_y
        in_end_y = in_begin_y + in_size_y
    elif args.in_begin_y is None and args.in_end_y is not None:
        in_end_y = args.in_end_y
        in_begin_y = in_end_y - in_size_y
    elif args.in_begin_y is None and args.in_end_y is None:
        in_begin_y = (min_in - in_size_y) // 2
        in_end_y = in_begin_y + in_size_y

    verbose(("Input \"%s\" is [%d, %d] (inclusive) to (%d, %d) (exclusive) "
             + "with size %dx%d.") % (in_fname, in_begin_x, in_begin_y,
                                  in_end_x, in_end_y, in_size_x, in_size_y))

    if (in_begin_x < 0 or in_begin_y < 0) or \
        (in_end_x > in_width or in_end_y > in_height):
        fatal(("For input image \"%s\" with size %dx%d the region [%d, %d] - "
              + "(%d, %d) specified won't fit. Try specifying --in-size, or "
              + "a lower value for it.") % (in_fname, in_width, in_height,
                in_begin_x, in_begin_y, in_end_x, in_end_y))

    if not args.width and not args.height:
        # Neither the width nor height was specified. Use the height of the
        # input image.
        out_height = in_size_y
        out_width = 2 * out_height
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
            out_width_old = out_width
            out_height_old = out_height
            out_width, out_height = out_im.size
            if (out_width_old  and (out_width_old  != out_width)) or \
               (out_height_old and (out_height_old != out_height)):
                warn("With --multi either the height or width specified does "
                        + "not match existing output image \"" + out_fname
                        + "\". Existing output image dimensions will be used "
                        + "instead.")
        elif not args.force:
            fatal("Output image file \"" + out_fname + "\" exists, but "
                  + "neither --multi nor --force was specified")
    if not out_im:
        if args.hidden_color.lower().startswith("trans"):
            # Color "trans" or "transparent' is a special case. It means an
            # alpha channel is needed, and the hidden pixels are to be
            # transparent.
            mode = "RGBA"
            color = (0, 0, 0, 0)
        else:
            mode = "RGB"
            color = args.hidden_color
        try:
            out_im = Image.new(mode, (out_width, out_height), color)
        except ValueError as err:
            if "unknown color specifier" in str(err):
                fatal("Hidden color \"" + color + "\" is not supported.")
            else:
                raise err
    out_pix = out_im.load()

    verbose("Output \"%s\" is %dx%d." % (out_fname, out_width, out_height))

    # Avoid references to globals in the loop.
    bl = args.bilinear
    slp = slope
    c_lat = radians(args.center_lat)
    c_lon = radians(args.center_lon)
    crop = args.crop
    rotate = radians(args.rotate)

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
        lon = 2 * pi * (((out_x + 0.5)/out_width) - 0.5) - c_lon
        for out_y in range(0, out_height):
            # The "+ 0.5" is to get the latitude at the center of the pixel.
            # This also prevents abs(sin(lon)) from being 1.0, so in_x and in_y
            # are always in the range [0, out_height).
            lat = -pi * (((out_y + 0.5)/out_height) - 0.5)

            # Convert from spherical coordinates to camera coordinates. The
            # sphere has radius one and it's centered at (0, 0, cam_sph_z) in
            # the camera coordinate system.
            cam_x = cos(lat) * sin(lon)
            cam_y = sin(lat)
            cam_z = cos(lat) * cos(lon)

            # Technically the cam_* variables are world coordinates at this
            # point, but they'll be updated to camera coordinates.

            if c_lat:
                # Rotate the unit sphere around the X-axis in order to bring
                # the closest point to the camera up along the closest meridian
                # to that latitude.
                new_cam_y = cam_y*cos(c_lat) - cam_z*sin(c_lat)
                cam_z = cam_z*cos(c_lat) + cam_y*sin(c_lat)
                cam_y = new_cam_y

            if rotate:
                # Rotate around the Z-axis. Note that the rotation is
                # clockwise, so the signs are flipped.
                new_cam_x = cam_x*cos(rotate) + cam_y*sin(rotate);
                cam_y = cam_y*cos(rotate) - cam_x*sin(rotate)
                cam_x = new_cam_x

            # For orthographic cam_sph_z is 0. This finishes the conversion
            # from world coordinates to camera coordinates.
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

            # Assure that ndc_* fall in range [0, 1).
            if ndc_x >= 1.0:
                ndc_x = 0.9999999
            if ndc_y >= 1.0:
                ndc_y = 0.9999999

            # Convert from NDC coordinates to pixel coordinates. Note the "-"
            # for ndc_y since the Y-axis is the opposite direction for pixel
            # coordinates.
            in_x = in_begin_x + in_size_x_2*(1 + ndc_x)
            in_y = in_begin_y + in_size_y_2*(1 - ndc_y)

            if bl:
                # Bilinear interpolation. This is a weighted average of the
                # four surrounding pixels.

                # Get X and Y coordinates of the four surrounding pixels
                # clipped into bounds. "l" is low (just below in_*), "h" is
                # high # (just above in_*).
                l_x = in_x - 0.5 if (in_x - 0.5) >= in_begin_x else in_begin_x
                h_x = in_x + 0.5 if (in_x + 0.5) < in_end_x else in_end_x - 1
                l_y = in_y - 0.5 if (in_y - 0.5) >= in_begin_y else in_begin_y
                h_y = in_y + 0.5 if (in_y + 0.5) < in_end_y else in_end_y - 1

                # The colors surrounding location (in_x, in_y).
                color_ll = in_pix[l_x, l_y]
                color_lh = in_pix[l_x, h_y]
                color_hl = in_pix[h_x, l_y]
                color_hh = in_pix[h_x, h_y]

                # The fraction of the way from the low color to the high
                # color. "l" is the distance from the low color to in_* and
                # "h" is the distance from in_* to the high color.
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
        # For crop the lower bound is inclusive and the upper bound is
        # exclusive, so the "+ 1" for the upper bound.
        verbose(("Output \"%s\" cropped from [%d, %d] (inclusive) to (%d, %d) "
                + "(exclusive) for a new size of %dx%d.") % (
                    out_fname, out_x_min, out_y_min, out_x_max + 1,
                    out_y_max + 1, out_x_max + 1 - out_x_min,
                    out_x_max + 1 - out_x_min))
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
    global min_z_ma
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

# Log a message to stdout if verbose.
def verbose(msg):
    if args.verbose:
        print(msg)

# Print a warning to stderr. It's flushed.
def warn(msg):
    if args.quiet:
        return
    print(msg, file=sys.stderr)
    sys.stderr.flush()

# Main

parse_args()
update_scene()
process_images()
