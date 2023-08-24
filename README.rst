Disk Patrol
===========

This is a program to check disk space and alert the logged-in users 
if disk space is not enough.

Usage
------

Edit diskpatrol.env

Build
------

To build diskpatrol binary::

    $ docker run -it -v $(pwd):/build --rm docker.io/jijisa/pyoxidizer:rl8

docker run -it -v $(pwd):/build --rm --entrypoint=/bin/bash docker.io/jijisa/pyoxidizer:rl8
