
import mraa  
import time    
# Drives a bipolar stepper motor through 4 steps.
# Done on intel edison.
# Uses a L293D chip, one side of the L239 for each coil of the motor
# Uses up 4 gpio pins on a single motor. The entire digital pwm bank will need to be used,
#  which will supply enough pins for all 3 motors.
# see safari: practical electronics: section 15.6 for the polarities required for a bi-polar motor.
# -it is a repeating sequence of 4 polarities, resulting in 4 steps.
# -this code goes through a single 4 step sequence. It will need to be expanded to do more than this simple partial rotation.

# amount of time between each step. Could be shortened to make it more smooth.
sleepTime = 0.5
# enable a side of the L293D
enable = 1
# disable a side of L293D
disable = 0
# output 12 volts to motor
high = 1
# set to ground on motor
low = 0

###gpio pins to able/disable l293d sides. 
#Each side has it's own enable/dispable pin.
#side 1
side1OfL239ChipEnabler = mraa.Gpio(2)
side1OfL239ChipEnabler.dir(mraa.DIR_OUT)
#Goes to pin 1 of L239

#side 2
side2OfL239ChipEnabler = mraa.Gpio(3)
#Goes to pin 9 of L239
side2OfL239ChipEnabler.dir(mraa.DIR_OUT)

#These 2 pins are shared by each coil, by enabling/disable each side of the l293d.
#Writing 1 to high, and the other to low, creates the circuit on the currently selected coil, which drives the motor.
#In other words: coilLead1 goes into the current coil, and coilLead2 comes back out of it. 
coilLead1 = mraa.Gpio(4)
coilLead2 = mraa.Gpio(5)
coilLead1.dir(mraa.DIR_OUT)
coilLead2.dir(mraa.DIR_OUT)

def setCoilsForwardBiased():
  coilLead1.write(high)
  coilLead2.write(low)

def setCoilsReverseBiased():
  coilLead1.write(low)
  coilLead2.write(high)

################################ turn stage 1 forward ############################
def turnStage1Forward(): 
  # side 1 will be used 1st
  side1OfL239ChipEnabler.write(enable)
  
  setCoilsForwardBiased()

  time.sleep(sleepTime)

  side1OfL239ChipEnabler.write(disable)


################################ turn stage 1 back ############################
def turnStage1Backwards():
  # side 1 will be used 1st
  side1OfL239ChipEnabler.write(enable)
  
  setCoilsReverseBiased()

  time.sleep(sleepTime)
  
  side1OfL239ChipEnabler.write(disable)



############################### turn stage 2 forward ##############################
def turnStage2Forward():
  side2OfL239ChipEnabler.write(enable)
  
  setCoilsForwardBiased()
  
  time.sleep(sleepTime)
  
  side2OfL239ChipEnabler.write(disable)

############################### turn stage 2 back ########################3
def turnStage2Backwards():
  side2OfL239ChipEnabler.write(enable)

  setCoilsReverseBiased()
  time.sleep(sleepTime)
  side2OfL239ChipEnabler.write(disable)

############################### stage 3 #################################
def turnStage3Forward():
  side1OfL239ChipEnabler.write(enable)
  #set the voltages to create coil circuit
  setCoilsReverseBiased()
  #enable side 1
  
  
  time.sleep(sleepTime)
  side1OfL239ChipEnabler.write(disable)

################################# stage 4 ###############################
def turnStage4Forward():
  side2OfL239ChipEnabler.write(enable)

  setCoilsReverseBiased()

  time.sleep(sleepTime)

  side2OfL239ChipEnabler.write(disable)

def disableAll():
  #disable both sides of L239 chip to start out
  side1OfL239ChipEnabler.write(disable)
  side2OfL239ChipEnabler.write(disable)

############################### track stages ################################
def turnAndTrack(counter):
  turnStage1Forward()
  turnAndTrack_(2, counter - 1)

def turnAndTrack_(stage, counter):
  if counter > 0:
     if stage == 1:
       turnStage1Forward()
       turnAndTrack_(2, counter -1)
     elif stage == 2:
       turnStage2Forward()
       turnAndTrack_(3, counter -1)
     elif stage == 3:
       turnStage3Forward()
       turnAndTrack_(4, counter -1)
     else:
       turnStage4Forward()
       turnAndTrack_(1, counter -1) 
  
################################ test runs ##################################
def forward4():
  disableAll()
  turnStage1Forward()
  turnStage2Forward()
  turnStage3Forward()
  turnStage4Forward()

def forward1Back1():
  disableAll()
  turnStage1Forward()
  turnStage1Backwards()

def forward2Back2():
  turnStage1Forward()
  turnStage2Forward()
  turnStage2Backwards()
  turnStage1Backwards()
#################################run##########################################
turnAndTrack(8)
