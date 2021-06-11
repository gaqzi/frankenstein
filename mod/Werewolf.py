#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

__author__    = 'Björn Andersson, Peter Sandvik'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2004, Björn Andersson and Peter Sandvik'
__license__   = 'LGPL'

from threading import Timer
from random import randint

class Werewolf:

	def __init__ (self, main_module):
		self.main = main_module

		# Configuration directives for this nice module!
		# All times are in seconds
		self.daytime   = 1
		self.votetime  = 10
		self.nighttime = 10
		self.jointime  = 10

		# Some bools so that we know when to do commands
		self.is_night = False
		self.voting = False
		self.started = False
		self.joining = False

		# The minimum amount of players to play the game
		self.min_players = 2
		self.max_players = 12

		# The amount of players
		self.num_players    = 0
		self.num_seer       = 0
		self.num_villagers  = 0
		self.num_werewolfes = 0

		# We need some variables to keep track of the users
		# that are playing
		self.players = {}

		# The player classes we can choose from. Their specialty, if any.
		# How many of that class at each level of players.
		# self.classes['werewolf'] = {'NumWolfes': 8}, 'Special': 'KILL'}
		self.classes = {}

		# These are variables that we want each round and will show at the
		# end of a round and reset at the beginning of next round.
		self.round_vars = {}

		# The channel we want to play teh game on!
		self.play_channel = '#test'

		# Lets load this module, eh!?
		self.load ()

	def load (self):
		self.classes['Werewolf'] = {'NumWolfes': 8, 'Special': 'KILL'}
		self.classes['Seer'] = {'Special': 'SEE'}
		self.classes['Villager'] = {}
		self.main.register_event_handler ('privmsg', '!ME!', 'kill', self, 'kill')
		self.main.register_event_handler ('privmsg', '!ME!', 'see', self, 'see')
		self.main.register_event_handler ('privmsg', '!ME!', 'vote', self, 'vote')
		self.main.register_event_handler ('privmsg', '!ME!', 'join', self, 'join')
		self.main.register_event_handler ('pubmsg', self.play_channel, \
										'!join', self, 'join')
		self.main.register_event_handler ('pubmsg', self.play_channel, \
										'!start', self, 'start')
#		self.main.irc.join (self.play_channel)

	def start (self, event, sender, args):
		if not self.joining and not self.started:
			self.joining = True
			self.message (self.play_channel, '%s has started a new game of \
							Werewolf. To join write !join or /msg %s JOIN' \
											% (sender[0], self.main.me ()))
			next = Timer (self.jointime, self.start_game)
			next.start ()
			self.num_players += 1
			self.join (event, sender, args)
		else:
			self.notice (sender[0], 'A game is already commencing!')

	def start_game (self):
		if self.joining:
			self.joining = False

		if not (len (self.players) >= self.min_players):
			self.message (self.play_channel, 'Not enough players to play \
			there\'ve to be atleast %s players to play.' % self.min_players)
			self.players.clear ()
		else:
			self.started = True
			self.assign_classes ()
			self.start_round ()

	def assign_classes (self):
		num_players = self.num_players
		# Lets start with deciding upon how many wolfes we want
		# as we will allow max 2 wolfes and the var in the class
		# desc gives us the number where we should start having two
		# wolfes or more
		if num_players >= self.classes['Werewolf']['NumWolfes']:
			self.num_werewolfes = 2
		else:
			self.num_werewolfes = 1

		# Makes it easier if we have a list of players that we can
		# remove players from when we've decided it's class.
		list_players = []
		werewolfs = []
		for player in self.players.iterkeys ():
			list_players.append (player)

		# Here now lets put in them wolfes and them in the list
		# named werewolfs
		for i in range (0, self.num_werewolfes):
			num = randint (1, len (list_players)) - 1
			werewolfs.append (list_players[num])
			list_players.remove (list_players[num])

		# Lets start with assigning that seer to, eh?
		seer_num = randint (1, len (list_players)) - 1
		seer = list_players[seer_num]
		list_players.remove (list_players[seer_num])

		# Now nice as we are we'll let the rest be villagers.
		# so now let's update the players classes and send them a message
		# telling them what they are, eh!?
		for player in werewolfs[:]:
			self.notice (player, 'You\'re a prowler of the night. \
												You\'re a Werewolf!')
			self.players[player] = {'class': 'werewolf'}

		# For that seer dude
		self.notice (seer, 'You\'ve been blessed with a third eye \
		each night you may gaze upon a villager and see his true    \
		identitiy. You\'re a seer')
		self.players[seer] = {'class': 'seer'}
		self.num_seer = 1

		# Now for the rest, which are all villagers
		for player in list_players[:]:
			self.notice (player, 'You\'re a villager. Each day you may \
			vote in the town meeting on who you think may be the werewolf')
			self.players[player] = {'class': 'villager'}
			self.num_villagers += 1

	def start_round (self):
		''' This is the start of the first round as all other rounds
		follow the day/night cykle but the first round is special and
		depends on wether there are an even or uneven amount of players. '''

		# At the start of every round we'll want to moderate the channel
		# and give voice to all players.
		self.main.irc.mode (self.play_channel, '+m')
		for user in self.players.iterkeys ():
			self.main.irc.mode (self.play_channel, '+v %s' % user)

		# If There are an even amount of players we want the Werewolf to
		# start else let the villagers start with lynching
		if (self.num_players % 2) == 0:
			self.night ()
		else:
			self.day_meeting ()

	def day_meeting (self):
		if self.is_night:
			self.is_night = False
			if self.round_vars.has_key ('killed'):
				self.message (self.play_channel, 'As the villager are \
				going to the meeting they see the sight of a dead \
				villager named %s' % self.round_vars['killed'])
			else:
				self.message (self.play_channel, 'There have been no \
				killing this night')

		self.message (self.play_channel, 'You now have %s seconds to cast \
		accusations and discuss who might be the Werewolf with the other  \
		villagers.' % self.daytime)
		next = Timer (self.daytime, self.day_voting)
		next.start ()

	def day_voting (self):
		self.voting = True
		self.message (self.play_channel, 'You now have %s seconds to vote \
		on the villager that you believe to be the Werewolf' % self.votetime)
		next = Timer (self.votetime, self.lynch)
		next.start ()

	def lynch (self):
		self.voting = False
		self.message (self.play_channel, 'Voting has ended. Counting votes..')
		most_votes = 0
		players = []
		if self.round_vars.has_key ('votes'):
			for player, votes in self.round_vars['votes'].items ():
				if votes > most_votes:
					most_votes = votes
					players = [player]
				elif votes == most_votes:
					players.append (player)
		else:
			self.message (self.play_channel, 'Noone voted!')

		if len (players) > 1:
			self.message (self.play_channel, 'There\'ve been a draw. \
								Chooses random of the tied players.')
			num = randint (1, len (players))
			players = [players[num - 1]]

		self.message (self.play_channel, 'The choosen villager is %s \
		and he is a %s' % (players[0], self.players[players[0]]['class']))
		if self.num_wolfes == 0:
			self.message (self.play_channel, 'The villagers have won! \
			the wolfie is dead!')
			self.clear ()
		elif self.num_wolfes == (self.num_villagers + self.num_seer):
			self.message (self.play_channel, 'There are as many warewolfes \
			as there are villagers. The werewolfs win!')
			self.clear ()
		else:
			self.night ()

	def clear (self):
		self.is_night       = False
		self.voting         = False
		self.started        = False
		self.joining        = False
		self.num_players    = 0
		self.num_warewolfes = 0
		self.num_seer       = 0
		self.round_vars.clear ()
		self.players.clear ()

	def night (self):
		# At night there's no need of round_vars so lets clear them
		# and then we set the game to night mode.
		self.round_vars.clear ()
		self.is_night = True
		self.message (self.play_channel, 'Night has decended over your \
													peacefull village.')
		next = Timer (self.nighttime, self.day_meeting)

		if self.num_werewolfes > 1:
			self.message (self.play_channel, 'The Werewolfes may now confer\
			and kill a villager. When you have decided write: \
			/msg %s KILL <victim>', self.main.me ())
		else:
			self.message (self.play_channel, 'The Werewolfe may now choose \
			this nights victim. When you have choosen your victim write:   \
			/msg %s KILL <victim>' % self.main.me ())

		if self.num_seer:
			self.message (self.play_channel, 'The seer may now confer with \
			the spirits and see the true identity of a villager. To do so  \
			write: /msg %s SEE <villager>' % self.main.me ())

	def kill (self, event, sender, args):
		''' This is the werewolf kill command. Checks wether the user is a 
		werewolf and if he's playing the game. If kill the other user.

		Variables:
		event  : The event that occurred 
		sender : the dude that sent the message
		args   : the arguments that we recieved '''

		if self.is_night:
			if self.is_class (sender[0], 'werewolf'):
				self.substract_class ( self.players[args[1]]['class'])
				self.remove_player (args[1])
				self.round_vars['killed'] = args[1]
				self.notice (sender[0], 'You\'ve choosen to kill %s' %
											args[1])
			else:
				self.notice (sender[0], 'Only the Werewolf may kill!')
		else:
			self.notice (sender[0], 'You can only use this command at night')

	def substract_class (self, pclass):
		if pclass.lower () == 'villager':
			self.num_villagers -= 1
		elif pclass.lower () == 'werewolf':
			self.num_werewolfes -= 1
		elif pclass.lower () == 'seer':
			self.num_seer -= 1

	def see (self, event, sender, args):
		''' This is the seer see command. Checks wether the user is a
		seer and if it's playing the game. If watch the class of the user

		Variables:
		event  : The event that occurred
		sender : the dude that sent the message
		args   : the arguments we recieved '''

		print 'See: %s' % self.is_night
		if self.is_night:
			if self.is_class (sender[0], 'seer'):
				print 'han är en seer bah!'
				pclass = self.players[args[1].lower ()]['class']
				if pclass:
					self.notice (sender[0], 'That villager is a %s!' % pclass)
			else:
				self.notice (sender[0], 'Only the seer may see! *pokes eye out*')
		else:
			self.notice (sender[0], 'You can only use this command at night')

	def vote (self, event, sender, args):
		''' This sets up the voting for each round. Checks if the user is
		playing this game and if let him vote his lynching!

		Variables:
		event  : The event that occurred
		sender : the dude that sent the event
		args   : the arguments we recieved '''

		print event, sender, args

		if self.voting:
			if self.is_playing (sender[0].lower ()):
				if self.round_vars.has_key ('has_voted'):
					if self.round_vars['has_voted'].has_key (sender[0]):
						return (false)
				# If we don't have a votes key we'd want it created
				if not self.round_vars.has_key ('votes'):
					self.round_vars['votes'] = {}

				# Now as we want to insert numbers and we can't insert numbers
				# unless we know the previous number, and if there's no previous
				if self.round_vars['votes'].has_key (args[1].lower ()):
					val = self.round_vars[args[1].lower ()]
					self.round_vars['votes'][args[1].lower ()] = val + 1
				else:
					self.round_vars['votes'][args[1].lower ()] = 1

				# So we know who've voted!
				if not self.round_vars.has_key ('has_voted'):
					self.round_vars['has_voted'] = {}
				self.round_vars['has_voted'][sender[0]] = True
				self.message (self.play_channel, '%s voted on %s' \
					% (sender[0], args[1]))
		else:
			self.notice (sender[0], 'Can only vote during a town meeting.')

	def is_playing (self, player):
		''' Checks if the player is in this game. Returns boolean '''
		return (self.players.has_key (player.lower ()))

	def is_class (self, player, pclass):
		''' Checks wether a player is a given class

		Variables:
		player: the player we want to look up
		pclass: the class we want to look up '''

		if self.is_playing (player):
			if self.players[player.lower ()]['class'] == plcass.lower ():
				return (True)
			else:
				return (False)
		else:
			return (False)

	def join (self, event, sender, args):
		''' Adds the player to the game '''
		if self.joining:
			if not self.players.has_key (sender[0]):
				self.players[sender[0].lower ()] = None
				self.num_players += 1
				self.message (self.play_channel, '%s have joined the game!' \
					% sender[0])
			else:
				self.notice (sender[0], 'You\'re already in this game.')
		else:
			self.message (self.play_channel, 'There\'s no active game!')

	def remove_player (self, player):
		''' Removes a player from the game. Happens if the player die,
		quits, get kicked etc. 
		
		Returns: The name of the player we removed'''
		if self.players.has_key (player):
			return (self.players.pop (player))

	def message (self, target, msg):
		''' Passess on a PRIVMSG to the IRC modules PRIVMSG function.
		Just to make it easier to understand. Target can be both channel
		and user.

		Variables:
		target: the channel or user to send to
		msg   : the message we want to send '''
		self.main.irc.privmsg (target, msg)

	def notice (self, reciever, msg):
		''' Passes on a PRIVNOTICE to the IRC modules notice function.
		Just to make it easier to understand.

		Variables:
		target: the channel or user to send to
		msg   : the message we want to send '''
		self.main.irc.notice (reciever, msg)
