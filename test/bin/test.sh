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

# Tests

# Tests that are expected have a zero exit, and produce an exact output image.
pass_tests=(
    # Try with bilinear (-b).
    "$s2e -a 17.3843 -bfo $tmp_dir/\$test_num.png $test_data/in/earth.jpg"

    # Above non-bilinear. This is faster, but more aliasing.
    "$s2e -a 17.3843  -fo $tmp_dir/\$test_num.png $test_data/in/earth.jpg"

    # Same as the above, but select exactly the sphere in the input image.
    # This is the most correct usage for earth.jpg in this test.
    "$s2e -a 17.3843 --in-begin-x  1 --in-begin-y  1 --in-size 238 \
        -fo $tmp_dir/\$test_num.png $test_data/in/earth.jpg"

    # A green circle. It gets a few white pixels in a symmetrical way.
    "$s2e             -fo $tmp_dir/\$test_num.png $test_data/in/green.png"

    # Same as above, two pixels smaller, which is pure green output.
    "$s2e --in-begin-x  1 --in-begin-y  1 --in-size 238 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green.png"

    # A green circle at a particular offset.
    "$s2e --in-begin-x 10 --in-begin-y 20 --in-size 200 \
        -fo $tmp_dir/\$test_num.png $test_data/in/offset-green.png"

    # Same as above, two pixels smaller, which is pure green output.
    "$s2e --in-begin-x 11 --in-begin-y 21 --in-size 198 \
        -fo $tmp_dir/\$test_num.png $test_data/in/offset-green.png"

    # The green circle, but with the minimum angle set to 1/2 the angular size
    # of the first test resulting a similar black border as the first test.
    # There should be no white pixels.
   "$s2e --min-angle 8.6922 -fo $tmp_dir/\$test_num.png \
        $test_data/in/green.png"

    # Part one of a full sized image that's the first image on the left, and
    # green on the right (but black on the right this part).
    "$s2e -a 17.3843 --center-lon 90 -bfo $tmp_dir/\$test_num.png \
        $test_data/in/earth.jpg"

    # Part two of a full sized image that's the first image on the left, and
    # green on the right. This is different than other tests in that it takes
    # the image created by the previous test as input.
    "$s2e -a 17.3843 --multi --center-lon -90 -bfo $tmp_dir/\$test_num.png \
        $test_data/in/green.png"

    # Attempt test #3 centered over Austin Texas (30.3 N 97.7 W). Note the
	# earth.jpg was centered over 0 N 90 W, which is why -7.7 is specified for
    # the longitude.
    # TODO: It looks like it's centered below Austin.
    "$s2e -a 17.3843 -a 17.3843 --in-begin-x 1 --in-begin-y 1 --in-size 238 \
        --center-lat 30.3 --center-lon -7.7 -bfo $tmp_dir/\$test_num.png \
        $test_data/in/earth.jpg" )

# Tests that are expected have a non-zero exit.
fail_tests=(
    # A command line option this not supported.
    "$s2e --bad-option"

    # An input image that does not exist.
    "$s2e -a 17.3843 -bfo $tmp_dir/\$test_num.png $test_data/in/not-exist.jpg"

    # Outside the input image by one pixel.
    "$s2e --in-begin-x  1 --in-begin-y  1 \
        -fo $tmp_dir/\$test_num.png $test_data/in/green.png" )

# Tests that aren't run because they are slow.
pass_slow_tests=(
    # A large version of test #3 with bilinear.
    "$s2e -a 17.3843 --in-begin-x 7 --in-begin-y 7 --in-size 2044 \
        -bfo $tmp_dir/\$test_num.png $test_data/in/big-earth.jpg" )

### Main ###

# Create the temporary directory.
if ! mkdir "$tmp_dir"
then
    echo "Could not make temporary directory \"$tmp_dir\"." 1>&2
    exit 1
fi
echo "Test output is in \"$tmp_dir\"."
echo

# Run the tests
test_num=0
failures=0
for test in "${pass_tests[@]}" "${fail_tests[@]}"
do
    let test_num++
    echo -n "Test #$test_num: "

    # Assume pass tests are first. Use the index to determine what is expected
    # of the exit code.
    if [[ $test_num -gt ${#pass_tests[@]} ]]
    then
        fail_expected=t
    else
        unset fail_expected
    fi

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
