import threading
import logging
from os import listdir
from os.path import isfile, join
import random
import pexpect
import time

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(asctime)s %(message)s',
                    )

class Light(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.device = args[0]
        self.currentcolor = (136, 34, 0)
        # self.currentcolor = (255, 60, 0)

        self.shouldstop = threading.Event()
        self.lightchanged = threading.Event()

        self.kwargs = kwargs
        
        return

    def stop(self):
        self.shouldstop.set()
        self.turnon() 
        self.closeprocess()

    def setup(self):
        # Run gatttool interactively.
        self.gatt = pexpect.spawn('gatttool -I')
        # Connect to the device.
        self.gatt.sendline('connect {0}'.format(self.device))
        self.gatt.expect('Connection successful')
        self.turnon() 

    def turnon(self):
        self.currentcolor = (136, 34, 0)
        self.lightchanged.set()

    def turnoff(self):
        self.currentcolor = (0, 0, 0)
        self.lightchanged.set()

    def fullon(self):
        line = 'char-write-cmd 0x002e 56000000fc0faa'
        if self.gatt and self.gatt.isalive():
            self.gatt.sendline(line) 

        self.lightchanged.clear()

    def changelight(self, color=None):
        if color:
            self.currentcolor = color

        r,g,b = self.currentcolor
        line = 'char-write-cmd 0x002e 56{0:02X}{1:02X}{2:02X}00f0aa'.format(r, g, b)
        logging.debug('light cmd: {}'.format(line))
        if self.gatt and self.gatt.isalive():
            self.gatt.sendline(line) 

        self.lightchanged.clear()


    def closeprocess(self):
        self.gatt.sendeof()
        self.gatt.close()
        self.gatt.wait()
        
    def run(self):
        logging.debug('running with %s and %s', self.args, self.kwargs)
        self.setup()

        while True:
            self.lightchanged.wait()
            self.changelight()

            if self.shouldstop.isSet():
                logging.debug('exiting light thread')
                return
