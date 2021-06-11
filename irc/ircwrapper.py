#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

__author__    = 'Björn Andersson <gaqzi@sanitarium.se>'
__version__   = '0.5'
__copyright__ = 'Copyright (c) 2004, Björn Andersson'
__license__   = 'GNU GPL'

import irclib
import re

class IRCWrapper:

	def __init__ (self, modman):
		self.irc            = irclib.IRC ()
		self.server         = self.irc.server ()
		self.module_manager = modman

	def connect (self, server, port, nick, passwd = '', ident = '', 
				ircname = ''):
		self.server.connect (server, port, nick, passwd, ident, ircname)

	def get_server_name (self):
		return (self.server.get_server_name ())

	def get_nickname (self):
		return (self.server.get_nickname ())

	def is_connected (self):
		return (self.server.get_server_name ())

	def add_global_handler (self, event):
		self.server.add_global_handler (event, getattr (self, 'event_handler'))

	def remove_global_handler (self, event):
		self.server.remove_global_handler (event, getattr (self, 'event_handler'))

	def event_handler (self, connection, event):
		modman = getattr (self.module_manager, 'on_event')
		modman (event.eventtype (), event.target (),        \
					re.split ('[!@]', event.source ()),     \
						''.join (event.arguments ()).split (' '))

	def action (self, target, action):
		self.server.action (target, action)

	def disconnect (self, msg = 'Rawr'):
		self.server.disconnect (msg)

	def invite (self, nick, channel):
		self.server.invite (nick, channel)

	def join (self, channel, key = ''):
		self.server.join (channel, key)

	def part (self, channel):
		self.server.part (channel)

	def kick (self, channel, nick, msg = ''):
		self.server.kick (channel, nick, msg)

	def mode (self, target, mode):
		self.server.mode (target, mode)

	def nick (self, newnick):
		self.server.nick (newnick)

	def notice (self, target, text):
		self.server.notice (target, text)

	def oper (self, nick, passwd):
		self.server.oper (nick, passwd)

	def part (self, channel):
		self.server.part (channel)

	def privmsg (self, target, text):
		self.server.privmsg (target, text)

	def privmsg_many (self, targets, text):
		self.server.privmsg_many (targets, text)

	def quit (self, msg = 'Rawr'):
		self.server.quit (msg)

	def quote (self, command):
		self.server.send_raw (command)

	def topic (self, chan, topic):
		self.server.topic (chan, topic)

	def who (self, target = '', op = ''):
		self.server.who (target, op)

	def whois (self, target):
		self.server.whois (target)

	def start (self):
		self.irc.process_forever ()

	def function (self, c, e):
		print c
		IRC.privmsg ('#test', join (e.arguments (), ' '))
		print e.eventtype ()
		print e.arguments ()
		print e.source ()
		print e.target ()
