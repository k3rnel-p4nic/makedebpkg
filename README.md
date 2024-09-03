makedebpkg
==========

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

