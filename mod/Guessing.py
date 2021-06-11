#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

__author__    = 'Björn Andersson <gaqzi@sanitarium.se>'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2004, Björn Andersson'
__license__   = 'GNU GPL'

from re import search

class Guessing:
	def __init__ (self, main_module):
		self.main = main_module
		self.load ()

	def load (self):
		self.main.register_event_handler ('pubmsg', ['#arrow', '#test'], '!guess', self, 'guess')
		self.main.register_event_handler ('pubmsg', ['#arrow', '#test'], '!explain', self, 'explain')

	def guess (self, target, sender, argv):
		var = argv[-1]
		if var[-1] == '?':
			answer = 'Yes'
		else:
			answer = 'No'
		self.main.irc.privmsg (target, '%s: %s' % (sender[0], answer))

	def explain (self, target, sender, argv):
		self.main.irc.notice (sendar[0], 'This game is rather simple. I am something and you can ask me what I am using the !guess command. I will answer your question with either Yes or No and when you guess correct I will tell you so.')
