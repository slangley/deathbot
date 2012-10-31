
from twisted.words.protocols import irc
from twisted.internet import protocol
from random import *
import sys
from twisted.internet import reactor
from datetime import *
from threading import Timer
import string

class WordWarManager:
    ww_queue = []
    def __init__(self,irc):
        self.irc = irc
    

    def check_existing_war(self, user):
        for war in self.ww_queue:
                if (war.name == user):
                        return True
        return False
    
        
    def insert_into_war(self, war, user):
	for awar in self.ww_queue:
            if (awar.name.lower() == war):
		print "Adding " + awar.name + " - " + user 
                awar.add_user_to_wordwar(user)
        
	
    def create_word_war(self, name, length, start,prompt):
        new_ww = WordWar(name,length,start, self,prompt)
        self.ww_queue.append(new_ww)
        return new_ww
        
    def done_word_war(self, wordwar):
        self.ww_queue.remove(wordwar)
        
    def get_status(self, user):
#        if (self.check_for_daddy(user) == 1):
#                self.irc_send_say("Yes father.");
        if len(self.ww_queue) == 0:
                self.irc.irc_send_msg(user,"There are no active word wars")
                return
                
        for ww in self.ww_queue:
                ww.status_word_war(user)
    def irc_send_me(self, message):
        self.irc.irc_send_me( message)

    
    def irc_send_say(self, message):
        self.irc.irc_send_say( message)


    def irc_send_msg(self, user, message):
        self.irc.irc_send_msg( user.split("!")[0], message)

                    


class WordWar():
    
    def __init__(self, name, length, start, queue, prompt):
        self.nicklist=[]
        self.name = name
        self.prompt = prompt
        self.length = int(length)
        self.start = int(start)
        self.timecalled = datetime.today()
        self.wwqueue = queue
        self.war_start_timer = Timer( self.start*60, self.start_word_war, [self] )
        self.war_start_timer.start()
        self.timestarted=""
        if (int(self.start) >2 ):
                self.war_warning_timer = Timer( (self.start-2)*60, self.warning_word_war, [self] )
                self.war_warning_timer.start()
        self.status = 0         
        
    def warning_word_war(self, args):
        self.send_message("WW: " +self.name + " starts in 2 minutes for "+str(self.length))
        self.notify_nics()

        
    def start_word_war(self, args):
        # send out message
        self.status = 1
        self.send_message("GOOOOOOOOOOO!!! WW: " +self.name + " for " + str(self.length) + " minutes")
        self.send_message("Prompt for this WW is: %s" % self.prompt )
        self.notify_nics()
        self.timestarted = datetime.today()
        self.war_timer = Timer( float(self.length)*60.0, self.finish_word_war, [self])
        self.war_timer.start()
        
        
    def status_word_war(self, user):
        self.wwqueue.irc_send_msg(user, "name: "+self.name )
        self.wwqueue.irc_send_msg(user, "length: "+str(self.length))
        self.wwqueue.irc_send_msg(user, "start: "+str(self.start) )
        if (self.status == 0):
            self.wwqueue.irc_send_msg(user, "status: waiting")
            self.wwqueue.irc_send_msg(user, "called at:" +str(self.timecalled))
            interval = timedelta(minutes=self.start) 
            then = self.timecalled + interval
            timeleft = then - datetime.today() 
            self.wwqueue.irc_send_msg(user, "time til start (min): " + str(timeleft))

        else:
            self.wwqueue.irc_send_msg(user, "status: underway")
            self.wwqueue.irc_send_msg(user, "started at:" +str(self.timestarted))
        
        self.wwqueue.irc_send_msg(user, "number members "+str(len(self.nicklist)))
        self.wwqueue.irc_send_msg(user, "-----")
        
        
    def finish_word_war(self, args):
        #remove from queue
        print str(datetime.today()) + " | " + "finish word war"
        print str(datetime.today()) + " | " + "remove from queue"
        self.send_message("WW: " +self.name + " is done - send your results")
        self.notify_nics()
        
        self.wwqueue.done_word_war(self)
        
    def add_user_to_wordwar(self, username):
        self.nicklist.append(username)

    def notify_nics(self):
        second_message = "Hey! That means you: "
        for nick in self.nicklist:
                shortnick = nick.split("!")
                second_message = second_message + shortnick[0] + " "
        self.wwqueue.irc_send_say(second_message)

        
    def send_message(self, message):        
        self.wwqueue.irc_send_say(message)
        for nick in self.nicklist:
                self.wwqueue.irc_send_msg(nick, message)

