#!/usr/bin/env python

import re

class Order:

        def __init__ (self, main_module):
                self.main = main_module
                self.requests = []
                self.load ()

        def load(self):
                self.main.register_event_handler ('pubmsg', ['#clubarrow', '#test'], '!order', self, 'order')
                self.main.register_event_handler ('join', ['#test', '#clubarrow'], '', self, 'join_mess')
                self.main.register_event_handler ('pubmsg', ['#clubarrow', '#test'], '!request', self, 'request')
                self.main.register_event_handler ('pubmsg', ['#clubarrow', '#test'], '!requests', self, 'show_requests')
                self.main.register_event_handler ('privmsg', '!ME!', 'delrequest', self, 'del_request')

        def order(self, target, sender, args):
                order = ' '.join (args[1:])
                if order.lower () == 'sneaky fuker':
                        order = r'Bonkinkz on the rockz'
                elif re.search ('(sex on the beach)', order.lower ()):
                        self.main.irc.action (target, 'slaps %s! Behave or I\'ll call the Bouncer!' % sender[0])
                if re.search ('(\d+)', args[1]):
                        self.main.irc.action (target, 'serves %s to %s' % (order, sender[0]))
                else:
                        self.main.irc.action (target, 'serves %s %s' % (sender[0], order))

        def join_mess(self, target, sender, args):
                self.main.irc.notice (sender[0], 'Remember to tune into the radio at sfynx.et.tudelft.nl:8000 !')
                targ = re.search ('(Zonk)', sender[0])
                if targ:
                        self.main.irc.privmsg (target, 'THE ZONKMEISTER IS IN THE HOUSE!!')
                elif re.search ('(Gaqzi)', sender[0]):
                        self.main.irc.action (target, 'slides %s a cold Trocadero, "on the house mate"' % sender[0])

        def request(self, target, sender, args):
                args = ' '.join (args[1:])
                self.requests.append (args)
                self.main.irc.privmsg (target, '%s requested: %s' % (sender[0], args))

        def show_requests(self, target, sender, args):
                counter = 1
                if len (self.requests) > 0:
                        self.main.irc.privmsg (target, 'These are the requests:')
                        for request in self.requests[:]:
                                self.main.irc.privmsg (target, '%s: %s' % (counter, request))
                                counter += 1
                else:
                        self.main.irc.privmsg (target, 'There\'re no requests!')

        def del_request(self, event, target, args):
                args = int (' '.join (args[1]))
                requests = self.requests[:args - 1]
                requests.extend (self.requests[args:])
                self.requests = requests
                self.main.irc.privmsg (target[0], '-- The new request list follows --')
                num = 1
                for request in self.requests[:]:
                        self.main.irc.privmsg (target[0], '%s: %s' % (num, request))
                        num += 1
