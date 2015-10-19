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
        self.gpio_door = kwargs['gpio_door']

        self.shouldstop = threading.Event()
        self.kwargs = kwargs
        self.start()
        
        return

    def stop(self):
        self.shouldstop.set()

    def setup():
        GPIO.setmode(GPIO.BOARD)

        # Set pins as output and input
        GPIO.setup(self.gpio_door,GPIO.IN) 


    def run(self):
        while True:
            if self.shouldstop.isSet():
                logging.debug('exiting door thread')
                return

            time.sleep(0.1)
