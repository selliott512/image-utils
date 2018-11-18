image-utils
==========

Open source command line utilities for working with images, which is currently
only sphere2equirect.py.

sphere2equirect.py converts images of spheres to equirectangular images.
Since an image of a sphere is considered to be a
[general perspective projection](https://en.wikipedia.org/wiki/General_Perspective_projection)
of that sphere this program converts from the general perspective projection to
the [equirectangular projection](https://en.wikipedia.org/wiki/Equirectangular_projection).

Here's an example of converting from an image of the Earth taken at 35,786 km,
which means that the Earth has an angular size of 17.3843°. Offsetting 1 pixels
(the "begin" options) to avoid a border leaves a 238 pixel size square that
tightly encloses the sphere to be converted.
```shell
sphere2equirect.py -a 17.3843 --in-begin-x 1 --in-begin-y 1 --in-size 238 -fo /tmp/earth-equirect.jpg test/data/in/earth.jpg
```

For celestial objects other than the sun and the moon the angular size (the
"-a" option) is small enough that it can probably be omitted. Omitting the
angular size results in an orthographic treatment.

Since equirectangular is a common projection the images produced can act as
input for other projection conversion programs such as
[G.Projector](https://www.giss.nasa.gov/tools/gprojector/). Also, they can
act as spherical texture maps for programs like
[Blender](https://www.blender.org/). The "--full" option may be helpful for
texture mapping.

There are [tools](http://paulbourke.net/miscellaneous/sphere2persp/) for
going the opposite direction.

Examples of sphere2equirect.py being used on [images of the moon](https://selliott.org/science/moon).

Check out image-utils's [home page](http://selliott.org/utilities/imageutils)
for more info.

See the "doc" directory for credit, development, license and version
information.
