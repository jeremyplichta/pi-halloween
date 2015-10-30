import threading
import logging
from os import listdir
from os.path import isfile, join
import random
import time
import pexpect
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(asctime)s %(message)s',
                    )

class Speaker(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.sounddir = args[0]
        self.doneplaying = args[1]
        self.shouldstop = threading.Event()
        self.shouldplay = threading.Event()
        self.kwargs = kwargs
        
        return

    def stop(self):
        self.shouldstop.set()
        self.shouldplay.set()

    def play(self):
        self.shouldplay.set() 

    def cancel(self):
        self.aplay.terminate()

    def getfiletoplay(self, mypath):
        onlyfiles = [ join(mypath,f) for f in listdir(mypath) if isfile(join(mypath,f)) and not '.DS_Store' in f ]
        return random.choice(onlyfiles)

    def playfile(self, playfile):
        playfile = playfile.replace(' ', '\ ')
        logging.debug('Playing file: {}'.format(playfile))

        self.aplay = pexpect.spawn(command='aplay -D bluetooth {}'.format(playfile), logfile=sys.stdout)
        self.aplay.logfile = sys.stdout
        status = self.aplay.wait()
        
        logging.debug('Done playing file: {} ({})'.format(playfile, status))
        self.shouldplay.clear()
        self.doneplaying.set()
    
        
    def run(self):
        logging.debug('running with %s and %s', self.args, self.kwargs)
        while True:
            self.shouldplay.wait()
            if self.shouldstop.isSet():
                logging.debug('exiting play thread')
                return

            playfile = self.getfiletoplay(self.sounddir)
            self.playfile(playfile)
