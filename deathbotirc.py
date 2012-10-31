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
#from wordwar import *
from wordwar2 import WordWar
from wordwar2 import WordWarManager

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

    
    channel = ""
    victim = "drew"
    victim_display = "Drew"
    
    lastdeathtime = datetime.today() - timedelta(seconds=45)
    
    
    def __init__(self):
	self.wwMgr = WordWarManager(self)
    
    def long_enough_since_death(self):
	if ((datetime.today() - timedelta(seconds=30)) > self.lastdeathtime):
	    self.lastdeathtime = datetime.today()
	    return True
	else:
	    return False
	

    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print str(datetime.today()) + " | " + "Signed on as %s." % (self.nickname,)

    def part_room(self):
        self.part(self.factory.channel)
        print str(datetime.today()) + " | " + "Oarted on as %s." % (self.nickname,)

    def joined(self, channel):
        print str(datetime.today()) + " | " + "Joined %s." % (channel,)
        self.channel = channel

    def check_for_daddy(self,user):
        short_user = user.split("!")[0]
        if (short_user == "smlangley"):
                return 1
        else:
                return 0

    def parse_echo(self, msg, user):
        commandlist = msg.split(" ", 1)
        self.irc_send_say(commandlist[1])

    def parse_changevictim(self,msg,user):
        if (self.check_for_daddy(user) == 1):
            commandlist = msg.split(" ")
            self.victim = commandlist[1].lower()
            self.victim_display = commandlist[1]
            self.irc_send_msg(user,"You have changed the victim to: " + self.victim)
        

    def privmsg(self, user, channel, msg):
        father = self.check_for_daddy(user)
        lowmsg = msg.lower()
        if lowmsg.find("unicorn")!= -1:
                self.irc_send_say("You should go play http://games.adultswim.com/robot-unicorn-attack-twitchy-online-game.html")
        if msg.find("!startwar")!= -1:
                self.parse_startwar(msg, user)
        elif msg.find("!throwdown") != -1:
                self.parse_throwdown(msg, user)
        elif msg.find("!echo")!= -1:
            if (father==1):
                self.parse_echo(msg,user)
        elif msg.find("!status")!=-1:
                self.wwMgr.get_status(user)
        elif lowmsg.find("!time")!=-1:
                self.irc_send_msg(channel, "thinks the time is "+ str(datetime.today()))
        elif lowmsg.find("!joinwar")!=-1:
                self.parse_join_wordwar(msg,user)
        elif msg.find("!help")!=-1:
                self.print_usage(user)
        elif msg.startswith("!reloaddeath"):
                load_death_array()              
        elif msg.startswith("!rejoinroom"):
                self.signedOn()         
        elif msg.startswith("!leaveroom"):
            if (father==1):
                    self.part_room()            
        elif msg.find("!changevictim")!=-1:
            self.parse_changevictim(msg,user) 
        elif msg.find("!victim")!=-1:
            if (father == 1):
                self.irc_send_msg(user,"The victim is currently: " + self.victim )
        elif lowmsg.find(self.victim) != -1:
		if (self.long_enough_since_death() == True):
		    if (lowmsg.find('kill') != -1) or (lowmsg.find('die') != -1):
			    index = randrange( len(deatharray) )
			    death = deatharray[index]
			    if (self.check_for_daddy(user) == 1):
				    self.irc_send_say("Yes, father.");
			    irc.IRCClient.describe(self, channel, string.strip(death % self.victim_display))

                        
    def parse_throwdown(self, command, user):
        print str(datetime.today()) + " | " + command
        print str(datetime.today()) + " | " + user
        short_user = user.split("!")[0]
        if self.wwMgr.check_existing_war(short_user):
            self.irc_send_msg(short_user,"Each user can only create one Word War at a time")
            return
                        
        commandlist = [c for c in command.split(" ") if c != '']
        if (len(commandlist) < 3):
                self.irc_send_msg(user, "Thrown down usage: !throwdown # ## -> create a war for # minutes starting in ## minutes")
                return
                
        war = self.initiate_war(short_user, commandlist)
        if war != None:
            self.wwMgr.insert_into_war(war, user)
	    self.irc_send_msg(user, "You have been added to WW: " + war.name)
            
    def parse_startwar(self, command, user):
        print str(datetime.today()) + " | " + command
        print str(datetime.today()) + " | " + user
        short_user = user.split("!")[0]
        if self.wwMgr.check_existing_war(short_user):
            self.irc_send_msg(short_user,"Each user can only create one Word War at a time")
            return
            
        commandlist = [c for c in command.split(" ") if c != '']
        if (len(commandlist) < 3):
                self.irc_send_msg(user, "Start war usage: !startwar # ## -> create a war for # minutes starting in ## minutes")
                return
        self.initiate_war(short_user, commandlist)

    def initiate_war(self, user, commandlist):
        war = self.wwMgr.create_word_war(user, commandlist[1], commandlist[2])
        print str(datetime.today()) + " | " + "Create word war "+user + " length "  + commandlist[1] + " starting in " + commandlist[2]
        if (self.check_for_daddy(user) == 1):
                self.irc_send_say("Yes father.");
        self.irc_send_say("The gauntlet has been thrown... "
                                          + user + " called a word war of " 
                                          + commandlist[1] + " min starting in "
                                          + commandlist[2] + " minutes." )
        
        return war
                    
                        
    def parse_join_wordwar(self, command, user):
        if (self.check_for_daddy(user) == 1):
                self.irc_send_say("Yes father.");
        print command
        commandlist = [c for c in command.split(" ") if c != '']
        username = commandlist[1].lower()
        if len(commandlist) <2:
                return
	
    	war = username
    	    
    	if (self.wwMgr.insert_into_war(war,user) == True):
    	    self.irc_send_msg(user, "You have been added to WW: " + war)
    	else:
    	    self.irc_send_msg(user, "You have been added to WW: " + war)
            return    
            
    def print_usage(self,user):
        self.irc_send_msg(user, "DeathBot Usage:")
        self.irc_send_msg(user, "!startwar # ## -> create a war for # minutes starting in ## minutes")
        self.irc_send_msg(user, "!status -> list wars that are in progress or not yet started")
        self.irc_send_msg(user, "!joinwar <warname> -> join a word war so you get msg'ed on start")
        self.irc_send_msg(user, "!throwdown # ## - create a war for # minutes starting in ## minutes; add you automatically to your war.")
        self.irc_send_msg(user, "!time -> what's the server time")


    def irc_send_me(self, message):
        irc.IRCClient.describe(self, self.channel, message)
        print str(datetime.today()) + " | " + self.channel + " -- me --> " + message
    
    def irc_send_say(self, message):
        irc.IRCClient.say(self, self.channel, message)
        print str(datetime.today()) + " | " + self.channel + " -- say --> " + message

    def irc_send_msg(self, user, message):
        irc.IRCClient.msg(self, user.split("!")[0], message)
        print str(datetime.today()) + " | " + self.channel + " -- msg: "+user+" --> " + message
        
#    irc.IRCClient.describe(self, channel, "heard:" + msg);


class WordWarBotFactory(protocol.ClientFactory):
    protocol = WordWarBot

    def __init__(self, channel, nickname='adeathbot'):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print str(datetime.today()) + " | " + "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print str(datetime.today()) + " | " + "Could not connect: %s" % (reason,)
        
        


if __name__ == "__main__":    
    chan = sys.argv[1]
    load_death_array()
    reactor.connectTCP('irc.mibbit.com', 6667, WordWarBotFactory('#' + chan, 'deathbot'))
    reactor.run()
