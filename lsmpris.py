#!/usr/bin/env python3

"""
.. module:: lsmpris
   :synopsis: A tool for listing currently running MPRIS 2.x compatible media
              players.

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
# Uses termcolor for coloring the script's output, argparse for parsing
# arguments and pydbus as a D-Bus binding

from termcolor import colored
import argparse
import pydbus
import sys

# CONSTANTS

NAME = 'lsmpris (pdmtools)'
VERSION = '001'

# PROGRAM

def get_args():
    """
    Gets script arguments with the argparse argument parser.

    :rtype: :obj:`Namespace`
    :returns: Script arguments.
    """
    
    parser = argparse.ArgumentParser(
        description='Lists running MPRIS 2.x compatible media players.')
    parser.add_argument('--system',
        help='list players on system message bus',
        action='store_true',
        default=False)
    parser.add_argument('--session',
        help='list players on session message bus (this is the default)',
        action='store_true',
        default=False)
    parser.add_argument('--bus',
        help="""
        list players on the message bus accessible via the provided address
        """,
        default=False)
    parser.add_argument('--color', '--colour',
        help='use markers for easier reading of the output text',
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

    return args

def get_mpris_names(bus):
    """
    Gets the application names of currently running MPRIS 2.x compatible
    players.

    :param bus: The bus to which the media player is connected.
    :type bus: :obj:`pydbus.bus.Bus`

    :rtype: list
    :returns: Populated list of names.
    """

    # Lists all names from the message bus and get only those that start with
    # "org.mpris.MediaPlayer2."
    dbus = bus.get('.DBus', 'DBus')
    list_names = dbus.ListNames()
    mpris_names = list(
        filter(lambda name: name.startswith('org.mpris.MediaPlayer2.'),
            list_names)
    )

    return mpris_names

def get_proxy_object(bus, name):
    """
    Gets a proxy for D-Bus object /org/mpris/MediaPlayer2.

    :param bus: The bus to which the media player is connected.
    :type bus: :obj:`pydbus.bus.Bus`

    :param name: The application name of the media player responsible for the
                 D-Bus object that should be proxied.
    :type name: str

    :rtype: :obj:`DBUS.<CompositeObject>`
    :returns: Proxy object.
    """

    return bus.get(name, '/org/mpris/MediaPlayer2')

def print_player_info(player, color = False):
    """
    Prints information about a player.

    :param player: A dictionary object containing a bus constant, the player's
                   name and proxy object.
    :type player: dict

    :param color: Defines if output should be colored.
    :type color: bool
    """

    # Gets player identity. If "color" or "colour" argument is present,
    # highlights it
    identity = getattr(player['proxy'], 'Identity', 'Unknown')
    identity = colored(identity, attrs=['bold']) if color else identity

    print('{} ({})'.format(identity, player['name']))

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

    # Creates a list for storing data on found players
    player_list = list()

    # Attempts to connect to the bus specified via command line arguments
    if (args.system):
        bus = pydbus.SystemBus()
    elif (args.session):
        bus = pydbus.SessionBus()
    else:
        bus = pydbus.connect(args.bus)

    # Gets names and proxy objects, and appends them to the list of found
    # players
    names = get_mpris_names(bus)
    for name in names:
        proxy = get_proxy_object(bus, name)
        player_list.append({ 'name': name, 'proxy': proxy })

    # Prints information about each player found
    for player in player_list:
        print_player_info(player, args.color)

# Guarantees the script is not being imported, but run directly
if __name__ == '__main__':
    main()