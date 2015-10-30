import threading
from os.path import isfile, join
import random
import time
import time
import RPi.GPIO as GPIO
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(asctime)s %(message)s',
                    )

class Distance(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.distcallback = args[0]
        self.mindistance = args[1]
        self.gpio_trigger = kwargs['gpio_trigger']
        self.gpio_echo = kwargs['gpio_echo']

        self.shouldstop = threading.Event()
        self.kwargs = kwargs
        
        return

    def stop(self):
        self.shouldstop.set()

    def setup(self):
        # Define GPIO to use on Pi

        # Set pins as output and input
        GPIO.setup(self.gpio_trigger,GPIO.OUT)  # Trigger
        GPIO.setup(self.gpio_echo, GPIO.IN)      # Echo

        # Set trigger to False (Low)
        GPIO.output(self.gpio_trigger, False)

        time.sleep(0.5)


    def getDistance(self):
        # Send 10us pulse to trigger
        GPIO.output(self.gpio_trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.gpio_trigger, False)

        start = time.time()
        stop = time.time()

        while GPIO.input(self.gpio_echo)==0:
            start = time.time()

        while GPIO.input(self.gpio_echo)==1:
            stop = time.time()

        # Calculate pulse length
        elapsed = stop-start
        # Distance pulse travelled in that time is time
        # multiplied by the speed of sound (cm/s)
        distance = elapsed * 34300

        # That was the distance there and back so halve the value
        distance = distance / 2
        return distance
       
    def run(self):
        logging.debug('running with %s and %s', self.args, self.kwargs)
        self.setup()

        GPIO.setmode(GPIO.BOARD)

        while True:
            if self.shouldstop.isSet():
                logging.debug('exiting distance thread')
                return

            dist = self.getDistance()
            #logging.debug('distance=%d', dist)
            if dist <= self.mindistance and dist > 10:
                self.distcallback(dist)


            time.sleep(.05)
