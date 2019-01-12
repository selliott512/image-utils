#!/bin/bash

# Tests for the image-utils project.
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

# Global
bname="${0##*/}"                    # Basename of this script.
dname="${0%/*}"                     # Directory that this script is in.
root=$(realpath "$dname/../..")     # Project root.
test_data="$root/test/data"         # Test data files.
tmp_dir="/tmp/image-utils-$bname.$$" # Temp directory

# Scripts to test.
s2e="$root/bin/sphere2equirect.py"
dg="$root/bin/drawgrid.py"

# TODO: Comparing PNG files with "diff" is probably not robust. Find a way of
# converting the PNGs to a canonical format by stripping comments and other
# extraneous chunks, turning off compression, or maybe convert to a simpler
# image format such as PPM.

# Tests

# Tests that are expected have a zero exit, and produce an exact output image.
pass_tests=(
    # sphere2equirect.py tests

    # Try with bilinear (-b).
    "$s2e -v -a 17.3843 -bfo $tmp_dir/\$test_num.png $test_data/in/90w-small.jpg"

    # Above non-bilinear. This is faster, but more aliasing.
    "$s2e -v -a 17.3843  -fo $tmp_dir/\$test_num.png $test_data/in/90w-small.jpg"

    # Same as the above, but select exactly the sphere in the input image.
    # This is the most correct usage for 90w-small.jpg in this test.
    "$s2e -v -a 17.3843 --in-begin-x  1 --in-begin-y  1 --in-size 238 \
        -fo $tmp_dir/\$test_num.png $test_data/in/90w-small.jpg"

    # A green circle. It gets a few white pixels in a symmetrical way.
    "$s2e -v             -fo $tmp_dir/\$test_num.png $test_data/in/green.png"

    # Same as above, two pixels smaller, which is pure green output.
    "$s2e -v --in-begin-x  1 --in-begin-y  1 --in-size 238 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green.png"

    # A green circle at a particular offset.
    "$s2e -v --in-begin-x 10 --in-begin-y 20 --in-size 200 \
        -fo $tmp_dir/\$test_num.png $test_data/in/offset-green.png"

    # Same as above, two pixels smaller, which is pure green output.
    "$s2e -v --in-begin-x 11 --in-begin-y 21 --in-size 198 \
        -fo $tmp_dir/\$test_num.png $test_data/in/offset-green.png"

    # The green circle, but with the minimum angle set to 1/2 the angular size
    # of the first test resulting a similar black border as the first test.
    # There should be no white pixels.
   "$s2e -v --min-angle 8.6922 -fo $tmp_dir/\$test_num.png \
        $test_data/in/green.png"

    # Part one of a full sized image that's the first image on the left, and
    # green on the right (but black on the right this part).
    "$s2e -v -a 17.3843 --center-lon -90 -bfo $tmp_dir/\$test_num.png \
        $test_data/in/90w-small.jpg"

    # Part two of a full sized image that's the first image on the left, and
    # green on the right. This is different than other tests in that it takes
    # the image created by the previous test as input.
    "$s2e -v -a 17.3843 --multi --center-lon 90 -bfo $tmp_dir/\$test_num.png \
        $test_data/in/green.png"

    # Process an orthographic image centered over Chicago IL. Since the input
    # image was produced by G.Projector this image can be verified by importing
    # the equirectangular output into G.Projector and verifying that the
    # overlay is aligned.
    "$s2e -v --center-lat 41.8781 --center-lon -87.6298 -fo $tmp_dir/\$test_num.png \
        $test_data/in/chicago-small.png"

    # Process an orthographic image centered over Melbourne Australia.
    # See the previous test comment.
    "$s2e -v --center-lat -37.8136 --center-lon 144.9631 -fo $tmp_dir/\$test_num.png \
        $test_data/in/melbourne-small.png"

    # Like the Chicago test except the input image is rotated 45 degrees
    # clockwise.
    "$s2e -v --center-lat 41.8781 --center-lon -87.6298 --rotate 45 \
        -fo $tmp_dir/\$test_num.png $test_data/in/chicago-small-rotate-45.png"

    # Like the Melbourne test except the input image is rotated -123 degrees
    # clockwise.
    "$s2e -v --center-lat -37.8136 --center-lon 144.9631 --rotate -123 \
        -fo $tmp_dir/\$test_num.png $test_data/in/melbourne-small-rotate--123.png"

    # The Chicago test, but with magenta hidden pixels.
    "$s2e -v --center-lat 41.8781 --center-lon -87.6298 --hidden-color magenta \
        -fo $tmp_dir/\$test_num.png $test_data/in/chicago-small.png"

    # The Chicago test, but with transparent hidden pixels.
    "$s2e -v --center-lat 41.8781 --center-lon -87.6298 --hidden-color trans \
        -fo $tmp_dir/\$test_num.png $test_data/in/chicago-small.png"

    # The green circle cropped. Since the output is square no hidden (black)
    # pixels remain.
    "$s2e -v --crop -fo $tmp_dir/\$test_num.png $test_data/in/green.png"

    # The second test, but cropped.
    "$s2e -v -a 17.3843 --crop -fo $tmp_dir/\$test_num.png $test_data/in/90w-small.jpg"

    # The third test, but specify the end instead of the beginning. This should
    # produce the same output as the third test.
    "$s2e -v -a 17.3843 --in-end-x 239 --in-end-y 239 --in-size 238 \
        -fo $tmp_dir/\$test_num.png $test_data/in/90w-small.jpg"

    # The third test, but specify beginning and end instead of the size. This
    # should produce the same output as the third test.
    "$s2e -v -a 17.3843 --in-begin-x 1 --in-begin-y 1 \
                     --in-end-x 239 --in-end-y 239 \
        -fo $tmp_dir/\$test_num.png $test_data/in/90w-small.jpg"

    # Similar to the first offset-green.png test, except with an ellipse.
    # This should produce a bit of white around the edges in a symmetrical way.
    "$s2e -v --in-begin-x 31 --in-end-x 225 --in-begin-y 55 --in-end-y 180 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green-ellipse.png"

    # The ellipse test, but with begin and size. This should produce the same
    # output.
    "$s2e -v --in-begin-x 31 --in-begin-y 55 --in-size-x 194 --in-size-y 125 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green-ellipse.png"

    # The ellipse test, but with end and size. This should produce the same
    # output.
    "$s2e -v --in-end-x 225 --in-end-y 180 --in-size-x 194 --in-size-y 125 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green-ellipse.png"

    # The previous test, but --in-size instead of --in-size-x testing that
    # --in-size provides a default value for the --in-size-* options.
    "$s2e -v --in-end-x 225 --in-end-y 180 --in-size 194 --in-size-y 125 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green-ellipse.png"

    # The ellipse test, but with begin, end and size. They must be consistent.
    # This should produce the same output.
    "$s2e -v --in-begin-x 31 --in-end-x 225 --in-end-x 225 --in-end-y 180 \
        --in-size-x 194 --in-size-y 125 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green-ellipse.png"

    # Similar to the second offset-green.png test, except with an ellipse.
    # This should produce solid green output due to the additional one pixel
    # margin.
    "$s2e -v --in-begin-x 32 --in-end-x 224 --in-begin-y 56 --in-end-y 179 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green-ellipse.png"

    # The ellipse test, but using the --ellipse option with cropped output.
    # This should produce the same output as the original ellipse test.
    "$s2e --ellipse \
        -fo $tmp_dir/\$test_num.png $test_data/in/green-ellipse-crop.png"

    # drawgrid.py tests

    # A default grid.
    "$dg $tmp_dir/\$test_num.png"

    # A grid with default values given explicitly. This should produce the
    # same output as the above.
    "$dg -x 1920 -y 1080 -s 10 -b white -f black $tmp_dir/\$test_num.png"

    # A grid with non-default values.
    "$dg -x 500 -y 400 -s 20 -b red -f blue -m $tmp_dir/\$test_num.png" )

# Tests that are expected have a non-zero exit.
fail_tests=(
    # sphere2equirect.py tests

    # A command line option that not supported.
    "$s2e -v --bad-option"

    # An input image that does not exist.
    "$s2e -v -a 17.3843 -bfo $tmp_dir/\$test_num.png $test_data/in/not-exist.jpg"

    # Outside the input image by one pixel.
    "$s2e -v --in-begin-x  1 --in-begin-y  1 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green.png"

    # Test that it is an error for the horizontal size to not be consistent.
    "$s2e -v --in-begin-x 1 --in-end-x 10 --in-size-x 20 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green.png"

    # Test that it is an error for the vertical size to not be consistent.
    "$s2e -v --in-begin-y 1 --in-end-y 10 --in-size-y 20 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green.png"

    # drawgrid.py tests

    # A command line option that not supported.
    "$s2e -v --bad-option" )

# Tests that aren't run because they are slow.
pass_slow_tests=(
    # A large version of test #3 with bilinear.
    "$s2e -v -a 17.3843 --in-begin-x 7 --in-begin-y 7 --in-size 2044 \
        -bfo $tmp_dir/\$test_num.png $test_data/in/90w-big.jpg" )

### Main ###

# Create the temporary directory.
if ! mkdir "$tmp_dir"
then
    echo "Could not make temporary directory \"$tmp_dir\"." 1>&2
    exit 1
fi
echo "Test output is in \"$tmp_dir\"."
echo

echo -e "\nStart of success tests (tests with an expected zero exit code).\n"

# Run the tests
test_num=0
failures=0
for test in "${pass_tests[@]}" "${fail_tests[@]}"
do
    let test_num++

    # Assume pass tests are first. Use the index to determine what is expected
    # of the exit code.
    if [[ $test_num -gt ${#pass_tests[@]} ]]
    then
        if [[ -z $fail_expected ]]
        then
            echo -e "\nStart of fails tests (tests with an expected non-zero \
exit code).\n"
        fi
        fail_expected=t
    else
        unset fail_expected
    fi

    echo -n "Test #$test_num: "

    if [[ $test == *--multi* ]]
    then
        # If this is multi then the output image should be a copy of the
        # previous output image.
        cp -f "$tmp_dir/$((test_num - 1)).png" "$tmp_dir/$test_num.png"
    fi

    eval echo "$test"
    if eval "$test" &> "$tmp_dir/$test_num.out"
    then
        if [[ -n $fail_expected ]]
        then
            echo -e "Failed. Exit code unexpectedly zero.\n"
            let failures++
            continue
        fi
    else
        if [[ -n $fail_expected ]]
        then
            echo -e "Success. Exit code non-zero as expected.\n"
        else
            echo -e "Failed. Exit code unexpectedly non-zero.\n"
            let failures++
        fi
        # An image is not expected in this case.
        continue
    fi

    if diff -q "$test_data/expected/$test_num.png" "$tmp_dir/$test_num.png" &> /dev/null
    then
        echo -e "Success. Image matched.\n"
    else
        echo -e "Failed. Image not matched.\n"
        let failures++
    fi
done

if [[ $failures -eq 0 ]]
then
    echo "All $test_num tests passed." 1>&2
else
    echo "$failures of $test_num tests failed." 1>&2
    exit 1
fi
