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

class Eyes(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.lefteye = kwargs['lefteye']
        self.righteye = kwargs['righteye']

        self.shouldstop = threading.Event()
        self.turnonevent = threading.Event()
        self.kwargs = kwargs

        self.curInt = 0
        self.step = 1

        return

    def stop(self):
        self.shouldstop.set()

    def setup(self):
        # Set pins as output and input
        GPIO.setup(self.lefteye,  GPIO.OUT) 
        GPIO.setup(self.righteye, GPIO.OUT) 

        GPIO.output(self.lefteye, GPIO.HIGH) # Set pins to high(+3.3V) to off led
        GPIO.output(self.righteye, GPIO.HIGH) # Set pins to high(+3.3V) to off led

        self.leye = GPIO.PWM(self.lefteye, 100)  # set Frequece to 2KHz
        self.reye = GPIO.PWM(self.righteye, 100)

        self.leye.start(0)      # Initial duty Cycle = 0(leds off)
        self.reye.start(0)

    def cleanup(self):
        GPIO.output(self.lefteye, GPIO.HIGH) 
        GPIO.output(self.righteye, GPIO.HIGH) 


    def turnon(self):
        self.turnonevent.set()
    def turnoff(self):
        self.turnonevent.clear()


    def run(self):
        logging.info('Entering eyes thread')
        self.setup()
        
        self.leye.ChangeDutyCycle(100)
        self.reye.ChangeDutyCycle(100)

        while True:
            if self.shouldstop.isSet():
                logging.debug('exiting eyes thread')
                return

            self.turnonevent.wait(1)
            if self.turnonevent.is_set():

                #logging.info('Lights on')
                self.leye.ChangeDutyCycle(100-self.curInt) 
                self.reye.ChangeDutyCycle(100-self.curInt)

                self.curInt = self.curInt + self.step
                if self.curInt > 100:
                    self.curInt = 0

            else:
                #logging.info('Lights off')
                self.leye.ChangeDutyCycle(100)
                self.reye.ChangeDutyCycle(100)
            time.sleep(0.01)

        self.cleanup()
