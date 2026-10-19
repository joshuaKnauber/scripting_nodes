"""Installed node packages are subpackages of this package: it also looks in
the folder they're installed in (core/node_packages.py). Extending a
package's `__path__` leaves `sys` alone."""

from ..core.node_packages import install_folder

if install_folder() not in __path__:
    __path__.append(install_folder())
