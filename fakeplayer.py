#!/usr/bin/env python3

"""
.. module:: fakeplayer
   :synopsis: A tool for simulating a MPRIS 2.x compatible media player. For
              debugging lsmpris only. Does not actually implement MPRIS in its
              entirety.

.. moduleauthor:: Rodrigo Menezes <rodrigo@rapidlight.io>
   :copyright: Copyright (c) 2017 RapidLight
   :license: MIT

"""

################################################################################
#                                                                              #
#                            The MIT License (MIT)                             #
#                                                                              #
#                        Copyright (c) 2017 RapidLight                         #
#                                                                              #
# Permission is hereby granted, free of charge, to any person obtaining a copy #
# of this software and associated documentation files (the "Software"), to     #
# deal in the Software without restriction, including without limitation the   #
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or  #
# sell copies of the Software, and to permit persons to whom the Software is   #
# furnished to do so, subject to the following conditions:                     #
#                                                                              #
# The above copyright notice and this permission notice shall be included in   #
# all copies or substantial portions of the Software.                          #
#                                                                              #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR   #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,     #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER       #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING      #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS #
# IN THE SOFTWARE.                                                             #
#                                                                              #
################################################################################

# IMPORTS

from gi.repository import GLib, GObject
import argparse
import pydbus
import sys

# CONSTANTS

NAME = 'fakeplayer (pdmtools)'
VERSION = '001'

# GLOBALS

verbose = False

# PROGRAM

class MediaPlayer2(object):
    """
    <node>
        <interface name='org.mpris.MediaPlayer2'>
            <property name='Identity' type='s' access='read' />
        </interface>
    </node>
    """

    def __init__(self, identity):
        self.identity = identity

    @property
    def Identity(self):
        vprint('\"Identity\" property read.')
        return self.identity

def get_args():
    """
    Gets script arguments with the argparse argument parser.
    """

    parser = argparse.ArgumentParser(
        description="""
        A tool for simulating a MPRIS 2.x compatible media player. For debugging
        lsmpris only. Does not actually implement MPRIS in its entirety.
        """)
    parser.add_argument('--identity',
        default='Fake Player',
        help="""
        sets the identity string that the program should use (the default is
        \"Fake Player\")
        """)
    parser.add_argument('--name',
        default='org.mpris.MediaPlayer2.fakeplayer',
        help="""
        sets the bus name that the program should use (the default is
        \"org.mpris.MediaPlayer2.fakeplayer\")
        """)
    parser.add_argument('--system',
        help='uses the system message bus',
        action='store_true',
        default=False)
    parser.add_argument('--session',
        help='uses the session message bus (this is the default)',
        action='store_true',
        default=False)
    parser.add_argument('--bus',
        help='uses the message bus accessible via the provided address',
        default=False)
    parser.add_argument('-v', '--verbose',
        help='enable output of debug information',
        action='store_true',
        default=False)
    parser.add_argument('-V', '--version',
        help='shows version of the program and exit',
        action='store_true',
        default=False)
    args = parser.parse_args()

    # If no flags are present specifying which message bus should be used are
    # set, use the session message bus
    if (not args.session and not args.system and not args.bus):
        args.session = True
    # If more than one flag specifying which message bus should be used was
    # set, fail
    elif (args.session and
         (args.system or args.bus) or (args.system and args.bus)):
        raise ValueError('Must specify only one message bus.')

    # Set the 'verbose' global variable
    global verbose
    verbose = args.verbose

    return args

def vprint(message):
    """
    Prints a message if the "verbose" argument is set.

    :param message: The message to print.
    :type message: str
    """
    if (verbose):
        print(message)

def fail(eclass, value, traceback):
    """
    Exception hook.

    :param eclass: The exception class.
    :param value: The exception instance.
    :param traceback: A traceback object.
    """
    print('{}: {}'.format(eclass.__name__, value))
    raise SystemExit(1)

def version():
    """
    Prints program version and exit.
    """

    print('{} {}'.format(NAME, VERSION))
    raise SystemExit(0)

def main():
    """
    The script's main function.
    """

    # Sets up exception hook
    sys.excepthook = fail

    # Gets script arguments
    args = get_args()

    # If the "version" argument is present, prints version and exit
    if (args.version):
        version()

    # Attempts to connect to the bus specified via command line arguments
    if (args.system):
        bus = pydbus.SystemBus()
    elif (args.session):
        bus = pydbus.SessionBus()
    else:
        bus = pydbus.connect(args.bus)

    # Request bus name, register object and run loop
    loop = GObject.MainLoop()
    bus.request_name(args.name)
    bus.register_object('/org/mpris/MediaPlayer2',
        MediaPlayer2(args.identity), MediaPlayer2.__doc__)
    vprint('Registered object to the message bus.')
    loop.run()

# Guarantees the script is not being imported, but run directly
if __name__ == '__main__':
    main()