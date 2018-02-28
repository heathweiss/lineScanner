import mraa  
import time  
import sqlite3
from sqliteDB import sayHello, printLayers, getLayers, insertLayer, insertPoint

scannerState = {'turnTblTtlSteps':0, 'turnTblCoilState':4,
                'radiusTtlSteps':0, 'radiusCoilState':4,
                'heightTtlSteps':0, 'heightCoilState':4,
                'currentLayerId':0 
               }
getUserInput = True

conn = sqlite3.connect('lineScanner.db')

c = conn.cursor()
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


#coil stages(ticks) per degree
#Found out with testing. 
#should never be declared, so as not to create state.
#Just pass in this value to any required functions.
#coilStagesPer360Degree = 1552


################################ user input ##################################

#task:
 #home the motors so they are in intial state of 4
 #call runScanner_ with initial state of: stage 4, degreeTick 0
   #respond to user input for turning/zeroing motors.
   #track the state of each motor so positions can be calculated.
     #degree
     #height
     #radius

# amount of time between each step. 
#0.01 is quite fast and smooth.
sleepTime = 0.01
# output 12 volts to motor
high = 1
# set to ground on motor
low = 0

#refer to Practical Electronics chap. 15.6 on polarities required to drive the stepper motor.
#step1 corresponds to 1st step as required to energize coil 1 in the required polarity.
#time is give to the coil to move. Then is is set to nuetral and given some time to adjust. 
### turnTable motor steps ### 
def turnTableStep1():
  turnTableCoil1a.write(high)
  turnTableCoil1b.write(low)
  time.sleep(sleepTime)
  turnTableCoil1a.write(low)
  time.sleep(sleepTime)

def turnTableStep2():
  turnTableCoil2a.write(high)
  turnTableCoil2b.write(low)
  time.sleep(sleepTime)
  turnTableCoil2a.write(low)
  time.sleep(sleepTime)  

def turnTableStep3():
  turnTableCoil1a.write(low)
  turnTableCoil1b.write(high)
  time.sleep(sleepTime)
  turnTableCoil1b.write(low)
  time.sleep(sleepTime)

def turnTableStep4():
  turnTableCoil2a.write(low)
  turnTableCoil2b.write(high)
  time.sleep(sleepTime)
  turnTableCoil2b.write(low)
  time.sleep(sleepTime)

### radius motor steps ###
def radiusStep1():
  radiusCoil1a.write(high)
  radiusCoil1b.write(low)
  time.sleep(sleepTime)
  radiusCoil1a.write(low)
  time.sleep(sleepTime)

def radiusStep2():
  radiusCoil2a.write(high)
  radiusCoil2b.write(low)
  time.sleep(sleepTime)
  radiusCoil2a.write(low)
  time.sleep(sleepTime)  

def radiusStep3():
  radiusCoil1a.write(low)
  radiusCoil1b.write(high)
  time.sleep(sleepTime)
  radiusCoil1b.write(low)
  time.sleep(sleepTime)

def radiusStep4():
  radiusCoil2a.write(low)
  radiusCoil2b.write(high)
  time.sleep(sleepTime)
  radiusCoil2b.write(low)
  time.sleep(sleepTime)

### height motor steps ####
heightCoil1a = mraa.Gpio(10)
heightCoil1b = mraa.Gpio(11)
heightCoil1a.dir(mraa.DIR_OUT)
heightCoil1b.dir(mraa.DIR_OUT)

heightCoil2a = mraa.Gpio(12)
heightCoil2b = mraa.Gpio(13)
heightCoil2a.dir(mraa.DIR_OUT)
heightCoil2b.dir(mraa.DIR_OUT)

def heightStep1():
  heightCoil1a.write(high)
  heightCoil1b.write(low)
  time.sleep(sleepTime)
  heightCoil1a.write(low)
  time.sleep(sleepTime)

def heightStep2():
  heightCoil2a.write(high)
  heightCoil2b.write(low)
  time.sleep(sleepTime)
  heightCoil2a.write(low)
  time.sleep(sleepTime)  

def heightStep3():
  heightCoil1a.write(low)
  heightCoil1b.write(high)
  time.sleep(sleepTime)
  heightCoil1b.write(low)
  time.sleep(sleepTime)

def heightStep4():
  heightCoil2a.write(low)
  heightCoil2b.write(high)
  time.sleep(sleepTime)
  heightCoil2b.write(low)
  time.sleep(sleepTime)



#The gpio pwm (pulse width modulation) pins that set the voltages on the motor stepper coils.
#<motor>Coil1a/b is for one coil, and <motor>Coil2a/b is for the other coil. There are 2 coils/motor.
#These are named to go with chart: http://mechatronics.mech.northwestern.edu/design_ref/actuators/stepper_drive1.html
### turntable motor coils ###
turnTableCoil1a = mraa.Gpio(2)
turnTableCoil1b = mraa.Gpio(3)
turnTableCoil1a.dir(mraa.DIR_OUT)
turnTableCoil1b.dir(mraa.DIR_OUT)

turnTableCoil2a = mraa.Gpio(4)
turnTableCoil2b = mraa.Gpio(5)
turnTableCoil2a.dir(mraa.DIR_OUT)
turnTableCoil2b.dir(mraa.DIR_OUT)

### radius motor coils ###
radiusCoil1a = mraa.Gpio(6)
radiusCoil1b = mraa.Gpio(7)
radiusCoil1a.dir(mraa.DIR_OUT)
radiusCoil1b.dir(mraa.DIR_OUT)

radiusCoil2a = mraa.Gpio(8)
radiusCoil2b = mraa.Gpio(9)
radiusCoil2a.dir(mraa.DIR_OUT)
radiusCoil2b.dir(mraa.DIR_OUT)

#Turn the each motor 4 steps to ensure they are all step 4.
#This initializes motor step position for start of scan.
### turnTable ###
def turnTableHome():
  turnTableStep1()
  turnTableStep2()
  turnTableStep3()
  turnTableStep4()
   
### radius ###
def radiusHome():
  radiusStep1()
  radiusStep2()
  radiusStep3()
  radiusStep4()

### height ###
def heightHome():
  #move downwards
  #heightStep1()
  #heightStep2()
  #heightStep3()
  #heightStep4()
  #move upwards
  heightStep4()
  heightStep3()
  heightStep2()
  heightStep1()
    
stepsPer360Degree = 1552
stepsPerMMRadius = 25.6
stepsPerMMHeight = 25.6


    ##################### turn motors base #################################
#task:
 #rotate a motor forward/back a given number of steps
 #still needs input functions to control which motor
    #given:
     #stepsToTake: how many steps to take(steps as in stepper motor)
     #totalStepsTaken: the current amount(pos/neg) of steps taken since motor was started or zeroed.
     #internalMotorStepState: The internal state of the motor coils, which needs to be know so that the
      #correct polarities can be applied to the correct coil, to turn the motor 1 step in required direction.
     #adjTotalStepsTaken: function increments/decrements the stepCount, as dictated by forward or backwards
     #adjInternalMotorStepState: move the internalMotorStepState forward/backward as dictated by motor direction.
     # use of this base function.
def rotateMotorBase(stepsToTake, scannerState, extractCoilState, adjTotalStepsTaken, adjInternalMotorStepState,
                    rotateMotorAwayFromInternalStep1, rotateMotorAwayFromInternalStep2, rotateMotorAwayFromInternalStep3, rotateMotorAwayFromInternalStep4):
      for i in range(0,stepsToTake):
         if extractCoilState(scannerState) == 1:
           rotateMotorAwayFromInternalStep1()
           scannerState = adjInternalMotorStepState(scannerState)
           scannerState = adjTotalStepsTaken(scannerState)
         elif extractCoilState(scannerState) == 2:
           rotateMotorAwayFromInternalStep2()
           scannerState = adjInternalMotorStepState(scannerState)
           scannerState = adjTotalStepsTaken(scannerState)  
         elif extractCoilState(scannerState) == 3:
           rotateMotorAwayFromInternalStep3()
           scannerState = adjInternalMotorStepState(scannerState)
           scannerState = adjTotalStepsTaken(scannerState)  
         else:
           rotateMotorAwayFromInternalStep4()
           scannerState = adjInternalMotorStepState(scannerState)
           scannerState = adjTotalStepsTaken(scannerState)  
      return scannerState

def getDegreeFromTotalStepsTaken(totalStepsTaken, stepsPer360Degree):
        def wrapDegrees(degrees):
            if degrees > 360:
              return wrapDegrees((degrees - 360))
            elif degrees < 0:
              return wrapDegrees((degrees + 360))
            else:
              return degrees
        return round((wrapDegrees(((360.0/stepsPer360Degree) * totalStepsTaken))),2)

def getRadiusFromTotalStepsTaken(scannerState, stepsPerMMRadius):
      return extractRadiusStepsTaken(scannerState) / stepsPerMMRadius

def getHeightFromTotalStepsTaken(scannerState, stepsPerMMHeight):
      return extractHeightStepsTaken(scannerState) / stepsPerMMHeight

def setRadiusTotalStepsTaken(scannerState, newStepsTaken):
      scannerState['radiusTtlSteps'] = newStepsTaken
      return scannerState

def setHeightTotalStepsTaken(scannerState, newStepsTaken):
      scannerState['heightTtlSteps'] = newStepsTaken
      return scannerState

def converMMToRadiusSteps(millimeters, stepsPerMMRadius):
      return (millimeters * stepsPerMMRadius)

def converMMToHeightSteps(millimeters, stepsPerMMHeight):
      return (millimeters * stepsPerMMHeight)
    
def incrementStepsTaken(tick):
        return (tick + 1)

def decrementStepsTaken(tick):
        return (tick - 1)

def extractTurnTableCoilState(scannerState):
      return scannerState['turnTblCoilState']

def extractHeightCoilState(scannerState):
      return scannerState['heightCoilState']

def extractHeightStepsTaken(scannerState):
      return scannerState['heightTtlSteps']

def extractTurnTableStepsTaken(scannerState):
      return scannerState['turnTblTtlSteps']

def extractRadiusStepsTaken(scannerState):
      return scannerState['radiusTtlSteps']

def extractRadiusCoilState(scannerState):
      return scannerState['radiusCoilState']

def setTurnTableCoilState(scannerState, newCoilState):
      scannerState['turnTblCoilState'] = newCoilState 
      return scannerState

def setHeightCoilState(scannerState, newCoilState):
      scannerState['heightCoilState'] = newCoilState 
      return scannerState

def setTurnTableStepsTaken(scannerState, newStepsTaken):
      scannerState['turnTblTtlSteps'] = newStepsTaken
      return scannerState

def setRadiusCoilState(scannerState, newCoilState):
      scannerState['radiusCoilState'] = newCoilState 
      return scannerState

def setRadiusStepsTaken(scannerState, newStepsTaken):
      scannerState['radiusTtlSteps'] = newStepsTaken
      return scannerState

def setHeightStepsTaken(scannerState, newStepsTaken):
      scannerState['heightTtlSteps'] = newStepsTaken
      return scannerState
   
    #Step the turntable a given number of <ticks or degrees?>, in either forward or backward direction. 
def rotateTurnTableForward(stepsToTake, scannerState):
      #Increases the state. 4 wraps around to state 1.
      def moveCoilStateForward(scannerState):
        if (extractTurnTableCoilState(scannerState) + 1) >= 5:
          return (setTurnTableCoilState(scannerState, 1))
        else:
          return (setTurnTableCoilState(scannerState, (extractTurnTableCoilState(scannerState) + 1)))
       
      def incrementStepsTaken(scannerState):
        scannerState['turnTblTtlSteps'] = (scannerState['turnTblTtlSteps'] + 1)
        return scannerState
       
      scannerState = rotateMotorBase(stepsToTake, scannerState, extractTurnTableCoilState, incrementStepsTaken, moveCoilStateForward,
                              turnTableStep4, turnTableStep3, turnTableStep2, turnTableStep1)  
      return scannerState

    #rotates the turntable motor backwards to decrease the degrees.
    #Makes a call to rotateMotorBase with appropriate functions passed in for target motor and direction..
    #return:
     #turntable moved backwards.
     #totalStepsTaken: the scoped state is adjusted to reflects final state.
     #coilState: the scoped state is adjusted to reflect the final state.
def rotateTurnTableBackward(stepsToTake, scannerState):
      #Decreases the coil state. 1 wraps back up to state 4.
      def moveCoilStateBackwards(scannerState):
        if (extractTurnTableCoilState(scannerState) - 1) <= 0:
          return setTurnTableCoilState(scannerState, 4)
        else:
          return setTurnTableCoilState(scannerState, (extractTurnTableCoilState(scannerState) - 1))
       
      def decrementStepsTaken(scannerState):
        return setTurnTableStepsTaken(scannerState, extractTurnTableStepsTaken(scannerState) - 1)
         
      scannerState = rotateMotorBase(stepsToTake, scannerState, extractTurnTableCoilState, decrementStepsTaken, moveCoilStateBackwards,
                                     turnTableStep4, turnTableStep3, turnTableStep2, turnTableStep1)
      return scannerState

    #Steps the radius motor a given number of ticks inwards, decreasing the radius. 
def rotateRadiusIn(stepsToTake, scannerState):
      #Increases the state. 4 wraps around to state 1.
      def moveCoilStateBackwards(scannerState):
        if (extractRadiusCoilState(scannerState) - 1) <= 0:
          return (setRadiusCoilState(scannerState, 4))
        else:
          return (setRadiusCoilState(scannerState, (extractRadiusCoilState(scannerState) - 1)))
       
      def decrementStepsTaken(scannerState):
        scannerState = setRadiusStepsTaken(scannerState, extractRadiusStepsTaken(scannerState) - 1) 
        return scannerState

      scannerState = rotateMotorBase(stepsToTake, scannerState, extractRadiusCoilState, decrementStepsTaken, moveCoilStateBackwards,
                                     radiusStep4, radiusStep3, radiusStep2, radiusStep1)  
      return scannerState

    #Steps the radius motor a given number of ticks outwards, increasing the radius. 
def rotateRadiusOut(stepsToTake, scannerState):
      #Increases the state. 4 wraps around to state 1.
      def moveCoilStateForward(scannerState):
        if (extractRadiusCoilState(scannerState) + 1) >= 5:
          return (setRadiusCoilState(scannerState, 1))
        else:
          return (setRadiusCoilState(scannerState, (extractRadiusCoilState(scannerState) + 1)))
       
      def incrementStepsTaken(scannerState):
        scannerState = setRadiusStepsTaken(scannerState, extractRadiusStepsTaken(scannerState) + 1) 
        return scannerState

      scannerState = rotateMotorBase(stepsToTake, scannerState, extractRadiusCoilState, incrementStepsTaken, moveCoilStateForward,
                                     radiusStep4, radiusStep3, radiusStep2, radiusStep1)  
      return scannerState

    #Step the height a given number of <ticks or degrees?>, in upward direction. 
def rotateHeightUp(stepsToTake, scannerState):
      #Increases the state. 4 wraps around to state 1.
      def moveCoilStateForward(scannerState):
        if (extractHeightCoilState(scannerState) + 1) >= 5:
          return (setHeightCoilState(scannerState, 1))
        else:
          return (setHeightCoilState(scannerState, (extractHeightCoilState(scannerState) + 1)))
       
      def incrementStepsTaken(scannerState):
        scannerState['heightTtlSteps'] = (scannerState['heightTtlSteps'] + 1)
        return scannerState
         
      scannerState = rotateMotorBase(stepsToTake, scannerState, extractHeightCoilState, incrementStepsTaken, moveCoilStateForward,
                                     heightStep4, heightStep3, heightStep2, heightStep1)  
      return scannerState

    #Step the height a given number of <ticks or degrees?>, in downwards direction. 
def rotateHeightDown(stepsToTake, scannerState):
      #Increases the state. 4 wraps around to state 1.
      def moveCoilStateBackward(scannerState):
        if (extractHeightCoilState(scannerState) - 1) <= 0:
          return (setHeightCoilState(scannerState, 4))
        else:
          return (setHeightCoilState(scannerState, (extractHeightCoilState(scannerState) - 1)))
       
      def decrementStepsTaken(scannerState):
        scannerState['heightTtlSteps'] = (scannerState['heightTtlSteps'] - 1)
        return scannerState
         
      scannerState = rotateMotorBase(stepsToTake, scannerState, extractHeightCoilState, decrementStepsTaken, moveCoilStateBackward,
                                     heightStep4, heightStep3, heightStep2, heightStep1)  
      return scannerState

def ensureInt(inputToCx):
  try:
    int(inputToCx)
  except ValueError:
    print "value was not an int"
    return False
  else:
    return True

def userInput(scannerState):
    prompt = "What next: help:h "
    msg = raw_input(prompt)

    if msg == "quit":
      conn.close()
      print "quit"
      return False
      
    elif msg == "h":
      print "\nstatus:s \nquit:q \nzero turntable steps:zt \nzero radius steps:zr \nset radius mm:sr \nset height mm:sh  "
      print "forward steps:f \nback steps:b \nin:i \nout:0 \nup:u \ndown:d"
      return True
      #runScanner_(scannerState) 
    elif msg == "s":
     #show current status of scanner: degrees, radius <and soon height>
     print "\ntotal turntable steps taken: " + str(extractTurnTableStepsTaken(scannerState))
     print "total turntable degrees: " + str(getDegreeFromTotalStepsTaken(extractTurnTableStepsTaken(scannerState), stepsPer360Degree)) 
     print "\ntotal radius steps taken: " + str(extractRadiusStepsTaken(scannerState))
     print "\ncurrent radius: " + str(getRadiusFromTotalStepsTaken(scannerState, stepsPerMMRadius))
     print "\ntotal height steps taken: " + str(extractHeightStepsTaken(scannerState))
     print "\ncurrent height: " + str(getHeightFromTotalStepsTaken(scannerState, stepsPerMMHeight))
     return True
    elif msg == "turnTableHome":
      #run turnTableHome() to initialize the turntable motor.
      turnTableHome()
      return True
    elif msg == "heightHome":
      #run heightHome() to initialize the turntable motor.
      heightHome()
      return True
    elif msg == "radiusHome":
      #run radiusHome() to initialize the turntable motor.
      radiusHome()
      return True
    elif msg == "zeroTable":
      #zero out the total turn table steps taken
      print "\ndegree ticks zero''d: " 
      scannerState = setTurnTableStepsTaken(scannerState, 0)
      return True
    elif msg == "zeroRadius":
      #zero out the total radius steps taken
      print "\nradius ticks zero''d: " 
      scannerState = setRadiusStepsTaken(scannerState, 0)
      return True
    elif msg == "setRadius":
      userInput = (raw_input( "\nradius in mm? "))
      if ensureInt(userInput):
         radiusTicks = converMMToRadiusSteps(int(userInput), stepsPerMMRadius)
         scannerState = setRadiusTotalStepsTaken(scannerState, radiusTicks)
         print "\nradius ticks set to " + str(radiusTicks)
      return True
    elif msg == "setHeight":
      userInput = raw_input( "\nheight in mm? ")
      if (ensureInt(userInput)):
        heightMM = int(userInput)
        heightTicks = converMMToHeightSteps(heightMM, stepsPerMMHeight)
        print "\nheight set to " + str(heightMM)
        print "\nticks set to " + str(heightTicks)
        scannerState = setHeightTotalStepsTaken(scannerState, heightTicks)
      return True
    #forward
    elif msg == "f":
      userInput = (raw_input( "\nhow many ticks forward? "))
      if (ensureInt(userInput)):
         print "was valid input"
         forwardStepsToTake = int(userInput)
         scannerState = rotateTurnTableForward(forwardStepsToTake, scannerState)
      else:
         print "was not valid input"
      return True
    #back
    elif msg == "b":
      userInput = (raw_input( "\nhow many ticks back? "))
      if (ensureInt(userInput)):
         backwardStepsToTake = int(userInput)
         scannerState = rotateTurnTableBackward(backwardStepsToTake, scannerState)
      return True
    #in radius
    elif msg == "i":
      userInput = (raw_input( "\nhow many ticks in? "))
      if (ensureInt(userInput)):
         inwardStepsToTake = int(userInput)
         scannerState = rotateRadiusIn(inwardStepsToTake,scannerState)
      return True
    #out radius
    elif msg == "o":
      userInput = (raw_input( "\nhow many ticks out? "))
      if (ensureInt(userInput)):
         outwardStepsToTake = int(userInput)
         scannerState = rotateRadiusOut(outwardStepsToTake,scannerState)
      return True
    #down height
    elif msg == "d":
      userInput = (raw_input( "\nhow many ticks down? "))
      if (ensureInt(userInput)):
         downwardStepsToTake = int(userInput)
         scannerState = rotateHeightDown(downwardStepsToTake,scannerState)
      return True
    #up height
    elif msg == "u":
      userInput = (raw_input( "\nhow many ticks up? "))
      if (ensureInt(userInput)):
         upwardStepsToTake = int(userInput)
         scannerState = rotateHeightUp(upwardStepsToTake,scannerState)
      return True
    elif msg == "insertLayer":
      layerName = (raw_input( "\nenter layer name: "))
      x = int(raw_input( "x-axis value: "))
      y = int(raw_input( "y-axis value: "))
      z = int(raw_input( "z-axis value: "))
      insertLayer(layerName, x, y, z, conn, c)
      return True
    elif msg == "showLayers":
      printLayers(getLayers(c))
      return True
    elif msg == "setCurrentLayerId":
      userInput = (raw_input( "\nset Current Layer Id? "))
      if (ensureInt(userInput)):
         layerId = int(userInput)
         scannerState['currentLayerId'] = layerId
      return True
    elif msg == "showCurrentLayerId":
      print str(scannerState['currentLayerId'])
      return True
    #insertPoint
    elif msg ==  "ip":
      degree = getDegreeFromTotalStepsTaken(extractTurnTableStepsTaken(scannerState), stepsPer360Degree)
      height = getHeightFromTotalStepsTaken(scannerState, stepsPerMMHeight)
      radius = getRadiusFromTotalStepsTaken(scannerState, stepsPerMMRadius)
      insertPoint(degree, height, radius, (scannerState['currentLayerId']), conn, c)
      return True
    else:
      print "\nunkown command"
      return True
      

################################################################################################################################### 



 


#initialize motors so they are all in a know coil state
turnTableHome()
radiusHome()
heightHome()


while getUserInput:
  getUserInput = userInput(scannerState)
  
