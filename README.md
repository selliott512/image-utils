# image-utils

Open source command line utilities for working with images, which is currently
only sphere2equirect.py.

image-utils has a small [home page](http://selliott.org/utilities/image-utils).

## sphere2equirect.py

sphere2equirect.py converts images of spheres to equirectangular images.
Since an image of a sphere is considered to be a [general perspective
projection](https://en.wikipedia.org/wiki/General_Perspective_projection)
of that sphere this program converts from the general perspective projection to
the [equirectangular projection](https://en.wikipedia.org/wiki/Equirectangular_projection).

For celestial objects other than the sun and the moon the angular size ("-a",
"--angular-size" option) is small enough that it can probably be omitted.
Omitting the angular size results in an orthographic treatment, which means
that exactly one hemisphere is visible, and the other hemisphere is hidden.
When the angular size of the sphere not negligible the visible portion is less
than a hemisphere.

Since equirectangular is a common projection the images produced can be used as
input for other projection conversion programs such as [G.Projector](https://www.giss.nasa.gov/tools/gprojector/). Also, they
can act as spherical texture maps for programs like [Blender](https://www.blender.org/).

There are [tools](http://paulbourke.net/miscellaneous/sphere2persp/) for going the opposite direction.

In addition to the examples at the end of this document there are examples of
sphere2equirect.py being used on [images of the moon](https://selliott.org/science/moon).

### Installation

[Python](https://www.python.org/) with the [Pillow](https://python-pillow.org/) image library is required (but plain PIL may also work).
The downloaded or git cloned files can be run in place:
```shell
bin/sphere2equirect.py ...
```

#### Usage

The usage can be seen by passing "-h" to sphere2equirect.py:

```txt
usage: sphere2equirect.py [-h] [-a ANGULAR_SIZE] [-b]
                          [--center-lat CENTER_LAT] [--center-lon CENTER_LON]
                          [-c] [-f] [--height HEIGHT]
                          [--hidden-color HIDDEN_COLOR] [-x IN_BEGIN_X]
                          [-y IN_BEGIN_Y] [-s IN_SIZE] [--min-angle MIN_ANGLE]
                          [-m] [-o OUTPUT] [-q] [-r ROTATE] [-v] [-w WIDTH]
                          IMAGE [IMAGE ...]

Create equirectangular images from sphere images.

positional arguments:
  IMAGE                 Sphere input images.

optional arguments:
  -h, --help            show this help message and exit
  -a ANGULAR_SIZE, --angular-size ANGULAR_SIZE
                        Angular size of the sphere. (default: 0.0)
  -b, --bilinear        Use bilinear interpolation instead of nearest.
                        (default: False)
  --center-lat CENTER_LAT
                        The latitude at the center of the sphere in the input
                        image. Helpful for --multi. (default: 0.0)
  --center-lon CENTER_LON
                        The longitude at the center of the sphere in the input
                        image. Helpful for --multi. (default: 0.0)
  -c, --crop            Crop the output image to the smallest rectangle
                        possible such that only hidden pixels are removed.
                        (default: False)
  -f, --force           Overwrite the output image. (default: False)
  --height HEIGHT       Output image height. Based on the input image by
                        default. (default: 0)
  --hidden-color HIDDEN_COLOR
                        Color to use for hidden pixels. Hidden pixels are
                        pixels in the output image that correspond to
                        locations on the sphere in the input image that are
                        not visible to the camera. (default: black)
  -x IN_BEGIN_X, --in-begin-x IN_BEGIN_X
                        X-coordinate of where the sphere begins in the input
                        image. (default: None)
  -y IN_BEGIN_Y, --in-begin-y IN_BEGIN_Y
                        Y-coordinate of where the sphere begins in the input
                        image. (default: None)
  -s IN_SIZE, --in-size IN_SIZE
                        Size (width or diameter) of the sphere in the input
                        image. Default is the largest size that will fit in
                        the input image. (default: None)
  --min-angle MIN_ANGLE
                        Minimum angle between line of sight and the surface of
                        the sphere. Pixels less than this will be hidden.
                        Helpful when the perimeter of the sphere is distorted.
                        (default: 0.0)
  -m, --multi           Multiple write. If there is an existing image at the
                        output location then open it for write. This is
                        helpful when producing a map from multiple input
                        images where each input image is a portion of the
                        entire sphere. (default: False)
  -o OUTPUT, --output OUTPUT
                        Output filename. Default to adding "-er" to the
                        basename (before the extension) of the original
                        filename. (default: None)
  -q, --quiet           Quiet. Suppress output (warnings). (default: False)
  -r ROTATE, --rotate ROTATE
                        Number of degrees the sphere in the input image is
                        rotated clockwise. The North pole at the top of the
                        sphere is zero degrees of rotation. (default: 0.0)
  -v, --verbose         Verbose. Additional output. (default: False)
  -w WIDTH, --width WIDTH
                        Output image width. Based on the input image by
                        default. (default: 0)
```
#### Test

There's a small test suite included at test/bin/test.sh. It works by comparing
the images produces against expected images. It's possible that it only works
on Linux.

#### Examples

##### Simple

A simple example where a sphere is far enough that the angular size does not
matter, so orthographic projection is used. The default output filename, which
is the input name with "-er" appended to the basename is used resulting in
"distant-sphere-er.jpg":

```shell
sphere2equirect.py distant-sphere.jpg
```

##### Complicated

A complicated example of converting from an image of the Earth taken at
35,786 km, which means that the Earth has an angular size of 17.3843° ("-a",
"--angular-size" option). Offsetting 1 pixels (the "begin" options) to avoid a
border leaves a 238 pixel size square ("-s", "--in-size" option) that tightly
encloses the sphere to be converted.

Verbose ("-v" option) is passed in order to get additional information. Verbose
is the opposite of quiet ("-q", "--quiet" option). Note that options can be
combined. In this case if "-a 17.3843" and "-v" had been combined it would have
been "-va 17.3843" (order matters).

In those cases where the sphere has its own latitude and longitude coordinate
system and where the center of the sphere in the input image is something other
than 0° North, 0° East the coordinates of the center ("center" options) can be
specified so that the output image is written correctly. In this case the input
image is centered over 90° West on the equator, where West is considered to be
negative. Also, it's possible that the sphere is rotated clockwise a certain
amount ("-r", "--rotate" option) from the viewer's perspective (0° in this case
which has no effect, but illustrates the option).

Since at most a hemisphere is visible at a time it may be helpful to combine
multiple photos of a sphere from different angles in a singe equirectangular
image. The multi option ("-m", "--multi" option) adds an output image if it
exists.

The pixels in the output image that that corresponds to points on the sphere in
the input image that are not visible are referred to as "hidden". It's possible
specify what color is used for hidden pixels ("--hidden-color" option). By
default the hidden color is "black", but something like "magenta" may be
specified to make the hidden portion more obvious. There's also the special
value "trans" that indicates that the hidden pixels should be transparent,
which can be helpful when overlaying the output image on a known good map. If
"trans" is specified the output image must be something like PNG that supports
transparency.

The crop option ("-c", "--crop" option) causes the output image to be cropped
with the smallest rectangle possible that only excludes hidden pixels. In the
simple case (which this isn't), like the first example, where exactly a
hemisphere centered at 0° North, 0° East is visible this results in a cropped
map that will extend from +- 90° horizontally instead of +- 180° horizontally.

The minimum angle option ("--min-angle" option) specifies the minimum angle
the line of sight may make with the sphere. In this case pixels within one
degree (1°) of the outer perimiter of the sphere in the input image will be
hidden. This is helpful when that portion of the input image does not have
sufficient resolution due to the angle.

The output file option ("-o", "--output") is used to explicitly specify the
output image name. When this option is used there can not be multiple input
images.

```shell
sphere2equirect.py -a 17.3843 --in-begin-x 1 --in-begin-y 1 --in-size 238 -v --center-lat 0 --center-lon -90 --rotate 0 --multi --hidden-color trans --crop --min-angle 1 -o /tmp/earth-equirect.png test/data/in/earth.jpg
```

See the "doc" directory for credit, development, license and version
information.
