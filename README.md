# What is this?
This is a simple utility designed to assist with editing setup.py files.  My initial goals were simply to avoid having to open the file and hand edit things such as install_requires.

# What this is not
It does not try to solve every use case (e.g. lists that are loaded from other modules, or even setups that are loaded...lookin at you Twisted), but for simple cases I have found it useful.

It is not a formatter, though a future version will optionally run a specified formatter, if installed in the environment, after modifying the setup file.

# Status
This is very alpha, and does not overwrite setup yet.

# Credits
I benefited greatly from examples of using lib2to3 to get an FST, but specifically I spent time in the source code of [black](https://github.com/ambv/black).
