Makedebpkg
==========
This repository consists of a bash script (makedebpkg) and its Python "porting".

# makedebpkg.sh
This script aims to provide makepkg's basic functionalites by sourcing the ```PKGBUILD``` file and generating the ```deb``` package.
The script will ```source``` the ```PKGBUILD``` file, allowing it to eventually execute code: this means that this script should be executed only with safe ```PKGBUILD``` files (thus, carefully read them).

## Usage
With a ```PKGBUILD``` file in the directory:

```
$ makedebpkg.sh
```

Or, if the ```PKGBUILD``` has another name (or is in another directory):
```
$ makedebpkg.sh -f <path/to/PKGBUILD>
```

# pymakedebpkg
This Python script aims to reproduce what makedebpkg.sh does in a not-so-pythonic way.

It breaks down the problem by internally parsing the needed fields of a standard PKGBUILD, compiling it by following its instructions and generating the deb package using the previously parsed metadata.
However, due to its structure, it is possible that the script will not work with complex PKGBUILDs. Indeed, ```makedebpkg``` is recommended.

## Requirements
The following modules are required: GitPython.

These modules can be installed with:
```
$ pip3 install GitPython
```

## Usage
```
$ python3 makedebpkg.py <path/to/PKGBUILD>
```
