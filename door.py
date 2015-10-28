import threading
import logging
from os import listdir
from os.path import isfile, join
import random
import time
import time
import RPi.GPIO as GPIO


logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

class Door(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.doorcallback = args[0]
        self.closecallback = args[1]
        self.closedevent = args[2]
        self.closedcount = 0
        self.gpio_door = kwargs['gpio_door']

        self.shouldstop = threading.Event()
        self.kwargs = kwargs

        self.closed = True
        
        return

    def stop(self):
        self.shouldstop.set()

    def setup(self):

        # Set pins as output and input
        GPIO.setup(self.gpio_door,GPIO.IN) 


    def run(self):
        self.setup()

        threshold = 40
        while True:
            if self.shouldstop.isSet():
                logging.debug('exiting door thread')
                return

            # logging.debug('Door state: {} closedcount={}'.format(GPIO.input(self.gpio_door), self.closedcount))

            if GPIO.input(self.gpio_door) == GPIO.LOW: # Check whether the button is pressed or not.
                self.closedcount = min(threshold,self.closedcount + 1)
                if not self.closed and self.closedcount == threshold:
                    self.closed = True
                    self.closedevent.set()
                    logging.info('Door Closed')
                    if self.closecallback:
                        self.closecallback()
            else:
                self.closedcount = 0
                if self.closed:
                    self.closed = False
                    self.closedevent.clear()
                    logging.info('Door Open')
                    if self.doorcallback:
                        self.doorcallback()

            time.sleep(.05)
