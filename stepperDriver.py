
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

############################ turntable motor ########################
#refered to as: degree
# see Dropbox/3d/scanner_line.txt for wiring from L239 chip to motor.
# see Dropbox/3d/lineScanner.ods for data about speed/degrees and consistency.
# amount of time between each step. 
#0.01 is quite fast.
sleepTime = 0.01
# enable a side of the L293D
enable = 1
# disable a side of L293D
disable = 0
# output 12 volts to motor
high = 1
# set to ground on motor
low = 0
#coil stages per degree
stagesPerDegree = 128/30

###gpio pins to able/disable l293d sides. 
#Each side has it's own enable/dispable pin.
#side 1
enableDegreeL239Side1 = mraa.Gpio(2)
enableDegreeL239Side1.dir(mraa.DIR_OUT)
#Goes to pin 1 of L239

#side 2
enableDegreeL239Side2 = mraa.Gpio(3)
#Goes to pin 9 of L239
enableDegreeL239Side2.dir(mraa.DIR_OUT)

#These 2 pins are shared by both stepper motor coils, by enabling/disabling each side of the l293d.
#Writing 1 side to high, and the other to low, creates the circuit on the currently required coil, which drives the motor.
#In other words: coilLead1 goes into the current coil, and coilLead2 comes back out of it. 
coilLead1 = mraa.Gpio(4)
coilLead2 = mraa.Gpio(5)
coilLead1.dir(mraa.DIR_OUT)
coilLead2.dir(mraa.DIR_OUT)

def setCoilsForwardBiased():
  coilLead2.write(low)
  coilLead1.write(high)
  

def setCoilsReverseBiased():
  coilLead1.write(low)
  coilLead2.write(high)

def setCoilsNeutral():
  coilLead1.write(low)
  coilLead2.write(low)

############################ stage base ###############################
#task
 #Base function for turning the motor 1 step.
 #refer to safaribooks:Practical Electronics: 15.7 on operation of stepper motor.
 #Has to apply to:
  #2 coils:
   #each controlled by 1 side of the l239 chip
    #only 1 side of chip can be active at 1 time.
   #each can have a forward or reverse polarity
#given:
 #chipSide: the side of the L239 chip being used.
 #coilPolarity: Forward or reverse bias of the coil in the motor.
def turnMotor1Step(chipSide, setCoilPolarity):
  chipSide.write(enable)
  
  setCoilPolarity()

  time.sleep(sleepTime)
  
  #setCoilsNeutral()
  #not sure this is usefull. Try without for now.
  
  chipSide.write(disable)
################################ stage 1  ############################
def energizeStage1():
  turnMotor1Step(enableDegreeL239Side1, setCoilsForwardBiased)

############################### stage 2 ##############################
def energizeStage2():
  #turnMotor1Step(enableDegreeL239Side2, setCoilsReverseBiased)
  #should be
  turnMotor1Step(enableDegreeL239Side2, setCoilsForwardBiased)

############################### stage 3 #################################
def energizeStage3():
  turnMotor1Step(enableDegreeL239Side1, setCoilsReverseBiased)

################################# stage 4 ###############################
def energizeStage4():
  turnMotor1Step(enableDegreeL239Side2, setCoilsReverseBiased)

############################# misc support #############################

def disableAll():
  #disable both sides of L239 chip to start out
  enableDegreeL239Side1.write(disable)
  enableDegreeL239Side2.write(disable)

#turn motor forward from stage 1 to stage 4, so that motor is in known state, which is state 4,
#no matter what the initial state was.
def home():
  disableAll()
  energizeStage1()
  energizeStage2()
  energizeStage3()
  energizeStage4()
  time.sleep(1)

############################### degree  ################################
#Step the turntable a given number of <ticks or degrees?>, in either forward or backward direction. 
def rotateTurnTableForward(counter, tickCount, stage):
  rotateMotorBase(counter, tickCount, stage, incrementTick, rotateStageCountForward,
                  energizeStage2, energizeStage3, energizeStage4, energizeStage1)
##################### turn motors base #################################
                         ###### forward ######
#rotate a motor forward given # of ticks
#still needs input functions to control which motor
def rotateMotorBase(counter, tickCount, stage, tickCountStepper, rotateStageCounter,
                    rotateWhenAtStage1, rotateWhenAtStage2, rotateWhenAtStage3, rotateWhenAtStage4):
  stageShifted = stage
  tickCountShifted = tickCount
  for count in range(0,counter):
     if stageShifted == 1:
       rotateWhenAtStage1()
       stageShifted = rotateStageCounter(stageShifted)
       tickCountShifted = tickCountStepper(tickCountShifted)
     elif stageShifted == 2:
       rotateWhenAtStage2()
       stageShifted = rotateStageCounter(stageShifted)
       tickCountShifted = tickCountStepper(tickCountShifted)  
     elif stageShifted == 3:
       rotateWhenAtStage3()
       stageShifted = rotateStageCounter(stageShifted)
       tickCountShifted = tickCountStepper(tickCountShifted)  
     else:
       rotateWhenAtStage4()
       stageShifted = rotateStageCounter(stageShifted)
       tickCountShifted = tickCountStepper(tickCountShifted)  
  runScanner_(tickCountShifted, stageShifted)

#before making it handle forward and backwards rotation
def rotateMotorBaseOrig(counter, tickCount, stage):
  stageShifted = stage
  tickCountShifted = tickCount
  for count in range(0,counter):
     if stageShifted == 1:
       energizeStage2()
       stageShifted = rotateStageForward(stageShifted)
       tickCountShifted += 1  
     elif stageShifted == 2:
       energizeStage3()
       stageShifted = rotateStageForward(stageShifted)
       tickCountShifted += 1  
     elif stageShifted == 3:
       energizeStage4()
       stageShifted = rotateStageForward(stageShifted)
       tickCountShifted += 1  
     else:
       energizeStage1()
       stageShifted = rotateStageForward(stageShifted)
       tickCountShifted += 1  
  runScanner_(tickCountShifted, stageShifted)  

#move the current stage of the motor coil engergized state forward.
#stage 4 wraps back around to state 1.
#This is related to how there are 4 coil states inside a bi-polar stepper motor.
def rotateStageCountForward(stage):
  
  if (stage + 1) >= 5:
    return 1
  else:
    return (stage + 1)

def rotateStageCountBackward(stage):
  if (stage - 1) <= 0:
    return 4
  else:
    return stage - 1

def incrementTick(tick):
  return (tick + 1)

def decrementTick(tick):
  return (tick - 1)

                         ###### backward ######
def rotateTurnTableBackward(counter, tickCount, stage):
  rotateMotorBase(counter, tickCount, stage, decrementTick, rotateStageCountBackward,
                  energizeStage4, energizeStage1, energizeStage2, energizeStage3)

#before using the base turntable rotator which handles forward and back
def rotateTurnTableBackwardOrig(counter, degreeTickCount, stage):
  if counter > 0:
     counterShifted = counter - 1
     degreeTickCountShifted = degreeTickCount - 1
     if stage == 1:
       energizeStage4()
       rotateTurnTableBackward(counterShifted, degreeTickCountShifted, 4)
     elif stage == 2:
       energizeStage1()
       rotateTurnTableBackward(counterShifted, degreeTickCountShifted, 1)
     elif stage == 3:
       energizeStage2()
       rotateTurnTableBackward(counterShifted, degreeTickCountShifted, 2)
     else:
       energizeStage3()
       rotateTurnTableBackward(counterShifted, degreeTickCountShifted, 3) 
  else:
     runScanner_(degreeTickCount, stage)

################################ user input ##################################

#task:
 #home the motors so they are in intial state of 4
 #call runScanner_ with initial state of: stage 4, degreeTick 0
   #respond to user input for turning/zeroing motors.
   #track the state of each motor so positions can be calculated.
     #degree
     #height
     #radius
def runScanner():
  home()
  runScanner_(0,4)
    
#called from: runScanner
 #will have been initialized to be in stage 4 with degreeTickCount 0
def runScanner_(degreeTickCount, stage):
  prompt = "What next: \nstatus:s \nquit:q \nzeroDegree:zd \nforward: \nback:b "
  msg = raw_input(prompt)

  if msg == "q":
    print "quit"
  elif msg == "s":
   print "\ndegree ticks: " + str(degreeTickCount)
   runScanner_(degreeTickCount, stage) 
  elif msg == "zd":
    print "\ndegree ticks zero''d: " 
    runScanner_(0, stage)
  elif msg == "f":
    forwardCount = int(raw_input( "\nforward how many: "))
    rotateTurnTableForward(forwardCount, degreeTickCount, stage)
  elif msg == "b":
    backCount = int(raw_input( "\nback how many: "))
    rotateTurnTableBackward(backCount, degreeTickCount, stage)
  else:
    print "\nunkown command"
    runScanner_(degreeTickCount, stage)


#################################run##########################################
runScanner()
#testFor()

#home()
#turnAndTrackForward(4)
#turnAndTrackBackward(4)

#forward4()


#energizeStage1()
#energizeStage2()
#energizeStage3()
#energizeStage4()



