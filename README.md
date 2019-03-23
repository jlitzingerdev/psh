# What is this?
This is a simple utility designed to assist with editing setup.py files.  My initial goals were simply to avoid having to open the file and hand edit things such as install_requires.

# What this is not
It does not try to solve every use case (e.g. lists that are loaded from other modules, or even setups that are loaded...lookin at you Twisted), but for simple cases I have found it useful.

It is not a formatter, though a future version will optionally run a specified formatter, if installed in the environment, after modifying the setup file.

# Status
This is very alpha, but currently works well for adding to install_requires.

# Caveats
This will only work for the Python version you have installed psh under, and possibly earlier versions.  Specifically, depending on the grammar needed to parse the target file, this may fail.  I plan to be more flexible in the future, but have no intention of vendoring any core code.

Also, because lib2to3 does not promise stability, this is not guaranteed to work on new versions.

# Tested on
- Python 3.6.7

# Credits
I benefited greatly from examples of using lib2to3 to get an FST, but specifically I spent time in the source code of [black](https://github.com/ambv/black).
