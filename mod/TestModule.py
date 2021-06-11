#!/usr/bin/env python

class TestModule:

	def __init__ (self, main_module):
		self.version = '1.0'
		self.main = main_module
		self.load ()

	def load (self):
		self.main.register_event_handler ('pubmsg', ['#test', '#arrow'], '!w00t', self, 'repeat')

	def repeat (self, target, sender, argv):
		self.main.irc.privmsg (target, ' '.join (argv))
