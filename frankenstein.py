#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

__author__    = 'Björn Andersson <ba@sanitarium.se>'
__version__   = '0.5'
__copyright__ = 'Copyright (c) 2004, Björn Andersson'
__license__   = 'GNU GPL'

from irc.ircwrapper import IRCWrapper
import sys
from types import ListType

class IRCBot:
    ''' The core of the bot. Here we setup all events, configuration,
    modules and etc. '''

    def __init__(self):
        # The IRC settings
        self.irc = IRCWrapper(self)

        # register_event_handler dictionary
        self.on_event_dict = {}
        self.registered_modules = {}

        # Events we're listening on
#       TestModule (self)
#       Guessing (self)
#       Werewolf (self)
#       Order (self)

        self.modules = {}

    def load_module(self, module_name):
        ''' Imports the module given by module_name and creates an
        instance according to our module scheme.

        Variable:
        module_name : the name of the module to import. '''
        # The initial import, mod.PackageName
        mod = __import__(module_name)
        # To get out of the module, which are the same as the PackageName
        name = '.'.join(module_name.split ('.')[1:])
        # Puts together the instance of the mod.PackageName then the
        # module instance and saves it away in self.modules.
        tmp = getattr(mod, name)
        print tmp
        tmp = reload(tmp)
        print tmp
        tmp2 = getattr(tmp, name)
        self.modules[module_name] = tmp2(self)

    def unload_module(self, module_name):
        ''' Unloads all registered events given by module_name
        as well as unloads it from the bot.

        Variable:
        module_name : the name of the module we want to unload '''
        self.unregister_module(module_name)
        return self.modules.pop(module_name)

    def register_event_handler(self, event, target, args, module,
                                callback):
        ''' An event is something that occurs to the bot. For instance
        someone joins a channel the bot is on, someone gets kicked,
        is killed etc.

        Variables:
        event   : the event that we want to controll
        target  : a channel or the bot
        args    : the arguments as a string we want to look for
        module  : the calling module send 'self' here
        callback: the sending module send the name of the function it want
                  to recieve the event here.'''

        # A msg is a string of text, the easiest way to do something
        # with a string of text is to split it up and search for things
        # that we want in an event.
        if type(args) != ListType:
            args = args.lower()
            args = args.split(' ')

        # We want everything to be lowercase
        event = event.lower()
        if type(target) != ListType:
            target = target.lower()

        # To not raise an error in setting up the event we will make
        # sure that there's an event handler and a target handler
        if not self.on_event_dict.has_key(event):
            self.on_event_dict[event] = {}
            self.irc.add_global_handler(event)

        # If we recieve a list with targets we want to recursivly enter
        # them into this list.
        if type(target) == ListType:
            for n_target in target[:]:
                self.register_event_handler (event, n_target, args, module, \
                                            callback)
        else:
            # Sets up the target handler
            if not self.on_event_dict[event].has_key (target):
                self.on_event_dict[event][target] = {}

            # Sets the event as we're sure that the target exist.
            if not self.on_event_dict[event][target].has_key (args[0]):
                self.on_event_dict[event][target][args[0]] = \
                                            getattr (module, callback)

            # Just so we won't have to write it so many times :P
            module_name = module.__class__.__name__

            if not self.registered_modules.has_key (module_name):
                self.registered_modules[module_name] = []

            # Put in some unregister values for the module.
            # First the name of the module. Then a list of lists containing
            # 1: the event, 2: the target, 3: the argument
            self.registered_modules[module_name].append ([event, target, \
                                                        args[0]])

    def unregister_module(self, module):
        ''' Unregisters all event handlers of the module given by module.

        Variables:
        module: the name of the module. (modobj.__class__.__name__) '''

        if self.registered_modules.has_key(module):
            for list in self.registered_modules[module][:]:
                event, target, arg = list
                self.unregister_event_handler (event, target, arg)
            self.registered_modules.pop (module)

    def unregister_event_handler (self, event, target, arg):
        ''' Unregisters the given event handler based on arg, target
        and event

        Variables:
        event : the IRC event that we look for
        target: a channel or the bot itself
        arg   : the argument we look for in the event '''

        # Unregisters the arg
        self.on_event_dict [event][target].pop (arg)

        # Check if there's less than one item in the given target if
        # remove the target
        if (len (self.on_event_dict[event][target]) < 1):
            self.on_event_dict[event].pop (target)

        # Check if there's less than one item in the given event list
        # if let's remove that event and unregister the global handler
        if (len (self.on_event_dict[event]) < 1):
            self.on_event_dict.pop (event)
            self.irc.remove_global_handler (event)

    def register_message_handler (self, target, text, module, callback):
        ''' Syntetic sugar for messages. :)

        Variables:
        target  : a channel or the bot
        text    : the text to react on
        module  : the module that sent the request
        callback: the function in the module that want the message '''

        self.register_event_handler ('privmsg', target, text, module,
                                    callback)


    def on_event (self, event, target, sender, argv):
        ''' Sets up appropriate handlers for events that occurs
        around the bot.

        Variables:
        event : the event that did occur
        target: a channel or the bot itself
        sender: the user that made the event occur
        argv  : a list containing the arguments of the command '''
        target = target.lower()
        argv[0] = argv[0].lower()

        # If we have the event key lets see if we have the target
        if self.on_event_dict.has_key(event):
            # If the target is the bot the special key is !ME!
            if target == self.me().lower():
                target = '!me!'
            # If we have the target key lets check for what we want
            if self.on_event_dict[event].has_key (target):
                # If we got the text let's pass it all to the module and
                # it's function!
                if self.on_event_dict[event][target].has_key(argv[0]):
                    self.on_event_dict[event][target][argv[0]]\
                                                (target, sender, argv)

    def printing (self, target, sender, argv):
        print target, sender, argv

    def quit (self, a, b, c):
        self.irc.quit (' '.join (argv))
        sys.exit (0)

    def me (self):
        return (self.irc.get_nickname ())

    def reload (self, target, sender, args):
        if self.modules.has_key (args[1]):
            tmp = __import__ (args[1])
            self.irc.privmsg (sender[0], 'Unloading module %s' % args[1])
            self.unload_module (args[1])
            self.irc.privmsg (sender[0], self.modules)
            self.irc.privmsg (sender[0], 'Loading module %s' % args[1])
            self.load_module (args[1])
            self.irc.privmsg (sender[0], self.modules)
            self.irc.privmsg (sender[0], 'Module %s should be loaded' % args[1])
        else:
            self.irc.notice (sender[0], 'That module isn\'t loaded')

B = IRCBot ()
B.irc.connect ('irc.piratpartiet.se', 6667, 'Frankenstein')
#B.irc.join ('#ClubArrow')
B.irc.join ('#test')
B.load_module ('mod.Order')
B.register_event_handler ('privmsg', '!ME!', 'reload', B, 'reload')
#print B.on_event_dict
#B.irc.join ('#clubarrow')
#B.irc.join ('#arrow')
#B.irc.join ('#arrow')
#print B.on_event_dict
B.irc.start ()
