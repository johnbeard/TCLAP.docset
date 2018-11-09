TCLAP Docset
==============

TCLAP (Templatized C++ Command Line Parser Library) Docset for
Dash (http://kapeli.com/dash) and Zeal (https://zealdocs.org/)

# Information

This is a compilation of the documentation available for the TCLAP library.
Please visit http://tclap.sourceforge.net/ for more information about this project.

TCLAP is released under the MIT license.

TCLAP is authored by Michael E. Smoot.

This docset for Dash was compiled by John Beard.

# Generate docset

You need `doxygen`, `doxytag2zealdb`, `cmake` and `sed` to build this docset.

If you specify CMake `UPDATE_ICONS`, you need `inkscape`, `pngcrush` too.

```
mkdir build
cd build
cmake ..
make
```

The docset archive will be in the `build` directory.