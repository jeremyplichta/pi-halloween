from speaker import Speaker
from distance import Distance
from light import Light
import time
import logging
import threading
import RPi.GPIO as GPIO

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

scaring = threading.Event()
doneplaying = threading.Event()

light = Light(args=('74:DA:EA:90:FD:87',))
spk = Speaker(args=('/home/pi/sounds',doneplaying))

def distance_callback(dist):
    if not scaring.is_set():
        scaring.set()
        logging.info('Time to scare, %d cm', dist)

        spk.play()
        time.sleep(.7)

        light.turnoff()

        doneplaying.wait()

        light.turnon()

        doneplaying.clear()
        scaring.clear()

        
dist = Distance(args=(distance_callback, 500),
               kwargs={'gpio_trigger': 16,
                      'gpio_echo': 18})

def stopthreads():
    spk.stop()
    dist.stop()
    light.stop()
    GPIO.cleanup()

try:
    spk.start()
    light.start()
    dist.start()

    while True:
        spk.join(1)
        dist.join(1)
        light.join(1)
except KeyboardInterrupt:
    print "interrupt"
    stopthreads()
except Exception:
    stopthreads()
