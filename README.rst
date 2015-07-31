Pyth
====

Pyth, an extremely concise language.

Installing Pyth
---------------
On Windows, add ``%APPDATA%\Python\Scripts`` to your PATH. On linux add
``~/.local/bin/`` to your PATH.

Then, to install or update Pyth as a user from PyPi, use::

    pip3 install --user --upgrade pyth-lang
    
To use the latest development version::

    git clone https://github.com/orlp/pyth5
    cd pyth5
    pip3 install --user --upgrade .
    
If you want to help develop Pyth, install the package as editable, so your
changes become active immediately::

    git clone https://github.com/orlp/pyth5
    cd pyth5
    pip3 install --user --editable .
    
For all of the above, to uninstall Pyth run::

    pip3 uninstall pyth-lang

Using Pyth
----------
Pyth is invoked using the ``pyth`` command. Use ``pyth --help`` to see its
usage.

To run the Pyth testsuite run ``python3 -m unittest`` from the source directory,
or ``python3 -m unittest pyth_lang.test`` from anywhere. You can run only the
tests for, say, ``+`` by running ``python3 -m unittest pyth_lang.test.Add``.

Or even better, use nose (``pip3 install nose``) and run ``nosetests``. nose has
all kinds of amazing plugins and tools, for example if you install Ned
Batchelder’s coverage plugin (``pip3 install coverage``) and run ``nosetests
--with-coverage --cover-html --cover-package pyth_lang`` you get a code coverage
summary for the testsuite.
