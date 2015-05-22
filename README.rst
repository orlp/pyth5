Pyth
====

Pyth, an extremely concise language.

Install Pyth
------------
On Windows, add ``%APPDATA%\Python\Scripts`` to your PATH. On linux add ``~/.local/bin/`` to your PATH.

Then, to install or update Pyth as a user from PyPi, use::

    pip3 install --user --upgrade pyth-lang
    
To use the latest development version::

    git clone https://github.com/orlp/pyth5
    cd pyth5
    pip3 install --user --upgrade .
    
If you want to help develop Pyth, install the package as editable, so your changes become active immediately::

    git clone https://github.com/orlp/pyth5
    cd pyth5
    pip3 install --user --editable .
    
For all of the above, to uninstall Pyth run::

    pip3 uninstall pyth-lang
