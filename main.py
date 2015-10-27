from speaker import Speaker
from distance import Distance
from light import Light
from eyes import Eyes
from door import Door

import time
import logging
import threading
import RPi.GPIO as GPIO

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

scaring = threading.Event()
doneplaying = threading.Event()
closedevent = threading.Event()
openevent = threading.Event()

light = Light(args=('74:DA:EA:90:FD:87',))
spk = Speaker(args=('/home/pi/sounds',doneplaying))

eyes = Eyes(args=(), kwargs={'lefteye': 12, 'righteye': 13})

def open_callback():
    logging.info('Open callback')
    openevent.set()

    if scaring.is_set():
        spk.cancel()

    # threading.Timer(5, lambda: eyes.turnoff()).start()
    eyes.turnoff()
    light.fullon()
    
def close_callback():
    openevent.clear()
    logging.info('Turning light back "on"')
    light.turnon()


def distance_callback(dist):
    # only scare if we are not already scaring and if the 
    # door is closed
    if not scaring.is_set() and closedevent.is_set():
        scaring.set()
        logging.info('Time to scare, %d cm', dist)

        spk.play()
        time.sleep(.7)
        
        eyes.turnon()
        light.turnoff()

        doneplaying.wait()

        light.turnon()

        doneplaying.clear()

        openevent.wait(30)
        if openevent.is_set():
            closedevent.wait()
            # let em clear out
            time.sleep(5)

        scaring.clear()

door = Door(args=(open_callback, close_callback, closedevent), kwargs={'gpio_door': 11})

        
dist = Distance(args=(distance_callback, 150),
               kwargs={'gpio_trigger': 16,
                      'gpio_echo': 18})

def stopthreads():
    spk.stop()
    dist.stop()
    light.stop()
    eyes.stop()
    door.stop()

    eyes.join(1)
    door.join(1)
    spk.join(1)
    dist.join(1)
    light.join(1)

    # GPIO.cleanup()

try:
    GPIO.setmode(GPIO.BOARD)

    spk.start()
    light.start()
    dist.start()
    eyes.start()
    door.start()

    while True:
        eyes.join(1)
        door.join(1)
        #spk.join(1)
        dist.join(1)
        #light.join(1)

except KeyboardInterrupt:
    print "interrupt"
    stopthreads()
except Exception:
    stopthreads()

GPIO.cleanup()
