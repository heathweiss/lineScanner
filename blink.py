import mraa
import time

ledPin = 13
sleepTime = 0.2
x = mraa.Gpio(ledPin)
x.dir(mraa.DIR_OUT)

while True:
    x.write(1)
    time.sleep(sleepTime)
    x.write(0)
    time.sleep(sleepTime)
