#!/usr/bin/python

# Copyright (c)2009 Sean Langley.  Some rights reserved.
# portions Copyright (C) 2006-2009 Eric Florenzano from the following website:
# http://www.eflorenzano.com/blog/post/writing-markov-chain-irc-bot-twisted-and-python/
#
# see the accompanying LICENSE file


from twisted.words.protocols import irc
from twisted.internet import protocol
from random import *
import sys
from twisted.internet import reactor
from datetime import *
from threading import Timer
import string

deatharray = []
def load_death_array():
	
	for item in deatharray:
		deatharray.remove(item)
	
	f = open("deathlist.txt","r")
	print str(datetime.today()) + " | " + "Reloading Death Array"
	
	for line in f.readlines():
		deatharray.append(line)
		print str(datetime.today()) + " | " + "adding "+line
	
	

class WordWarBot(irc.IRCClient):
	ww_queue = []
	
	channel = ""
	
	def _get_nickname(self):
		return self.factory.nickname
	nickname = property(_get_nickname)

	def signedOn(self):
		self.join(self.factory.channel)
		print str(datetime.today()) + " | " + "Signed on as %s." % (self.nickname,)

	def joined(self, channel):
		print str(datetime.today()) + " | " + "Joined %s." % (channel,)
		self.channel = channel

	def check_for_daddy(self,user):
		short_user = user.split("!")[0]
		if (short_user == "quagmire") or (short_user == "smlangley") or (short_user =="quaggy"):
			return 1
		else:
			return 0
			

	def privmsg(self, user, channel, msg):
		father = self.check_for_daddy(user)
		lowmsg = msg.lower()
		if msg.find("!startwar")!= -1:
			self.parse_startwar(msg, user)
		elif msg.find("!status")!=-1:
			self.get_status(user)
		elif lowmsg.find("!time")!=-1:
			self.irc_send_msg(channel, "thinks the time is "+ str(datetime.today()))
		elif lowmsg.find("!joinwar")!=-1:
			self.parse_join_wordwar(msg,user)
		elif msg.find("!help")!=-1:
			self.print_usage(user)
		elif msg.startswith("!reloaddeath"):
			load_death_array()		
		elif lowmsg.find('errol') != -1:
			if (lowmsg.find('kill') != -1) or (lowmsg.find('die') != -1):
				index = randrange( len(deatharray) )
				death = deatharray[index]
				if (self.check_for_daddy(user) == 1):
					self.irc_send_say("Yes father.");
				irc.IRCClient.me(self, channel, string.strip(death % "Errol"))

	def parse_startwar(self, command, user):
		print str(datetime.today()) + " | " + command
		print str(datetime.today()) + " | " + user
		short_user = user.split("!")[0]
		for war in self.ww_queue:
			if (war.name == short_user):
				self.irc_send_msg(short_user,"Each user can only create one Word War at a time")
				return
		commandlist = command.split(" ")
		if (len(commandlist) < 3):
			self.irc_send_msg(user, "Start war usage: !startwar # ## -> create a war for # minutes starting in ## minutes")
			return
		self.create_word_war(short_user, commandlist[1], commandlist[2])
		print str(datetime.today()) + " | " + "Create word war "+short_user + " length "  + commandlist[1] + " starting in " + commandlist[2]
		if (self.check_for_daddy(user) == 1):
			self.irc_send_say("Yes father.");
		self.irc_send_say("The gauntlet has been thrown... "
						  + short_user + " called a word war of " 
						  + commandlist[1] + " min starting in "
						  + commandlist[2] + " minutes." )
		
	def parse_join_wordwar(self, command, user):
		if (self.check_for_daddy(user) == 1):
			self.irc_send_say("Yes father.");
		print command
		commandlist = command.split(" ")
		if len(commandlist) <2:
			return
		for war in self.ww_queue:
			if (war.name == commandlist[1]):
				print "Adding " + war.name + "-" +commandlist[1] + " - " + user 
				war.add_user_to_wordwar(user)
				self.irc_send_msg(user,"You have been added to WW: "+war.name)
				return
		
		
	def print_usage(self,user):
		self.irc_send_msg(user, "DeathBot Usage:")
		self.irc_send_msg(user, "!startwar # ## -> create a war for # minutes starting in ## minutes")
		self.irc_send_msg(user, "!status -> list wars that are in progress or not yet started")
		self.irc_send_msg(user, "!joinwar <warname> -> join a word war so you get msg'ed on start")
		self.irc_send_msg(user, "!time -> what's the server time")

	def create_word_war(self, name, length, start):
		new_ww = WordWar(name,length,start, self)
		self.ww_queue.append(new_ww)
		
	def done_word_war(self, wordwar):
		self.ww_queue.remove(wordwar)
		
	def get_status(self, user):
		if (self.check_for_daddy(user) == 1):
			self.irc_send_say("Yes father.");
		if len(self.ww_queue) == 0:
			self.irc_send_msg(user,"There are no active word wars")
			return
			
		for ww in self.ww_queue:
			ww.status_word_war(user)
			
		  
	def irc_send_me(self, message):
		irc.IRCClient.me(self, self.channel, message)
		print str(datetime.today()) + " | " + self.channel + " -- me --> " + message
	
	def irc_send_say(self, message):
		irc.IRCClient.say(self, self.channel, message)
		print str(datetime.today()) + " | " + self.channel + " -- say --> " + message

	def irc_send_msg(self, user, message):
		irc.IRCClient.msg(self, user.split("!")[0], message)
		print str(datetime.today()) + " | " + self.channel + " -- msg: "+user+" --> " + message
		
#	irc.IRCClient.me(self, channel, "heard:" + msg);


class WordWarBotFactory(protocol.ClientFactory):
	protocol = WordWarBot

	def __init__(self, channel, nickname='deathbot'):
		self.channel = channel
		self.nickname = nickname

	def clientConnectionLost(self, connector, reason):
		print str(datetime.today()) + " | " + "Lost connection (%s), reconnecting." % (reason,)
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		print str(datetime.today()) + " | " + "Could not connect: %s" % (reason,)
		
		
class WordWar():
	
	def __init__(self, name, length, start, queue):
		self.nicklist=[]
		self.name = name
		self.length = int(length)
		self.start = int(start)
		#self.timecalled = time.time()
		self.wwqueue = queue
		self.war_start_timer = Timer( self.start*60, self.start_word_war, [self] )
		self.war_start_timer.start()
		self.timestarted=""
		#self.start_word_war(["asdf"])
		if (int(self.start) >2 ):
			self.war_warning_timer = Timer( (self.start-2)*60, self.warning_word_war, [self] )
			self.war_warning_timer.start()
		self.status = 0		
		
	def warning_word_war(self, args):
		self.send_message("WW: " +self.name + " starts in 2 minutes for "+str(self.length))

		
	def start_word_war(self, args):
		# send out message
		self.status = 1
		self.send_message("GOOOOOOOOOOO!!! WW: " +self.name + " for " + str(self.length) + " minutes")
		self.timestarted = datetime.today()
		self.war_timer = Timer( float(self.length)*60.0, self.finish_word_war, [self])
		self.war_timer.start()
		
		
	def status_word_war(self, user):
		self.wwqueue.irc_send_msg(user, "name: "+self.name )
		self.wwqueue.irc_send_msg(user, "length: "+str(self.length))
		self.wwqueue.irc_send_msg(user, "start: "+str(self.start) )
		self.wwqueue.irc_send_msg(user, "started at:" +str(self.timestarted))
		if (self.status == 0):
			self.wwqueue.irc_send_msg(user, "status: waiting")
		else:
			self.wwqueue.irc_send_msg(user, "status: underway")
		
		self.wwqueue.irc_send_msg(user, "number members "+str(len(self.nicklist)))
		self.wwqueue.irc_send_msg(user, "-----")
		
		
	def finish_word_war(self, args):
		#remove from queue
		print str(datetime.today()) + " | " + "finish word war"
		print str(datetime.today()) + " | " + "remove from queue"
		self.send_message("WW: " +self.name + " is done - send your results")
		
		self.wwqueue.done_word_war(self)
		
	def add_user_to_wordwar(self, username):
		self.nicklist.append(username)
		
	def send_message(self, message):
		self.wwqueue.irc_send_say(message)
		
		for nick in self.nicklist:
			self.wwqueue.irc_send_msg(nick, message)



if __name__ == "__main__":
	
	
	chan = sys.argv[1]
	#chan = "slangley_test"
	load_death_array()
	reactor.connectTCP('irc.mibbit.com', 6667, WordWarBotFactory('#' + chan, 'deathbot'))
	reactor.run()
