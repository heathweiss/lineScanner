
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
def runScanner():
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

  #Turn the motor 4 steps to ensure it is in step 4.
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
    
  
  #motor(s) should have been initialized to be in coil stage 4 and total<motor>StepsTaken is started
  #out at 0.
  def runScanner_(scannerState):
  #def runScanner_(totalStepsTaken, coilState):
    stepsPer360Degree = 1552
    stepsPerMMRadius = 25.6
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
      runScanner_(scannerState)
    
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

    def setRadiusTotalStepsTaken(scannerState, newStepsTaken):
      scannerState['radiusTtlSteps'] = newStepsTaken
      return scannerState

    def converMMToRadiusSteps(millimeters, stepsPerMMRadius):
      return (millimeters * stepsPerMMRadius)
    
    def incrementStepsTaken(tick):
        return (tick + 1)

    def decrementStepsTaken(tick):
        return (tick - 1)

    def extractTurnTableCoilState(scannerState):
      return scannerState['turnTblCoilState']

    def extractTurnTableStepsTaken(scannerState):
      return scannerState['turnTblTtlSteps']

    def extractRadiusStepsTaken(scannerState):
      return scannerState['radiusTtlSteps']

    def extractRadiusCoilState(scannerState):
      return scannerState['radiusCoilState']

    def setTurnTableCoilState(scannerState, newCoilState):
      scannerState['turnTblCoilState'] = newCoilState 
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
         
      rotateMotorBase(stepsToTake, scannerState, extractTurnTableCoilState, incrementStepsTaken, moveCoilStateForward,
                      turnTableStep4, turnTableStep3, turnTableStep2, turnTableStep1)  
    

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
         

      rotateMotorBase(stepsToTake, scannerState, extractTurnTableCoilState, decrementStepsTaken, moveCoilStateBackwards,
                      turnTableStep4, turnTableStep3, turnTableStep2, turnTableStep1)


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

      rotateMotorBase(stepsToTake, scannerState, extractRadiusCoilState, decrementStepsTaken, moveCoilStateBackwards,
                      radiusStep4, radiusStep3, radiusStep2, radiusStep1)  

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

      rotateMotorBase(stepsToTake, scannerState, extractRadiusCoilState, incrementStepsTaken, moveCoilStateForward,
                      radiusStep4, radiusStep3, radiusStep2, radiusStep1)  

  
    
    prompt = "What next: help:h "
    msg = raw_input(prompt)

    if msg == "q":
      print "quit"
    elif msg == "h":
      print "\nstatus:s \nquit:q \nzero turntable steps:zt \nzero radius steps:zr \nset radius mm:sr \nforward steps:f \nback steps:b \nin:i \nout: "
      runScanner_(scannerState) 
    elif msg == "s":
     #show current status of scanner: degrees, radius <and soon height>
     print "\ntotal turntable steps taken: " + str(extractTurnTableStepsTaken(scannerState))
     print "total turntable degrees: " + str(getDegreeFromTotalStepsTaken(extractTurnTableStepsTaken(scannerState), stepsPer360Degree)) 
     print "\ntotal radius steps taken: " + str(extractRadiusStepsTaken(scannerState))
     print "\ncurrent radius: " + str(getRadiusFromTotalStepsTaken(scannerState, stepsPerMMRadius))
     runScanner_(scannerState) 
     #runScanner_(totalTurntableStepsTaken, turntableCoilState, totalRadiusStepsTaken, radisuCoilState) 
    elif msg == "zt":
      #zero out the total turn table steps taken
      print "\ndegree ticks zero''d: " 
      runScanner_(setTurnTableStepsTaken(scannerState, 0))
    elif msg == "zr":
      #zero out the total radius steps taken
      print "\nradius ticks zero''d: " 
      runScanner_(setRadiusStepsTaken(scannerState, 0))
    elif msg == "sr":
      radiusMM = int(raw_input( "\nhow many radius mm: "))
      radiusTicks = converMMToRadiusSteps(radiusMM, stepsPerMMRadius)
      print "\nradius ticks set to " + str(radiusTicks)
      runScanner_(setRadiusTotalStepsTaken(scannerState, radiusTicks))
    elif msg == "f":
      forwardStepsToTake = int(raw_input( "\nforward how many: "))
      #rotateTurnTableForward(forwardStepsToTake, totalStepsTaken, coilState)
      rotateTurnTableForward(forwardStepsToTake, scannerState)
    elif msg == "b":
      backwardStepsToTake = int(raw_input( "\nback how many: "))
      #rotateTurnTableBackward(backwardStepsToTake, totalStepsTaken, coilState)
      rotateTurnTableBackward(backwardStepsToTake, scannerState)
    elif msg == "i":
      inwardStepsToTake = int(raw_input( "\nin how many: "))
      rotateRadiusIn(inwardStepsToTake,scannerState)
    elif msg == "o":
      outwardStepsToTake = int(raw_input( "\nout how many: "))
      rotateRadiusOut(outwardStepsToTake,scannerState)
    else:
      print "\nunkown command"
      runScanner_(scannerState)
      

  #where the rubber meets the road.
  #initialize motors
  turnTableHome()
  radiusHome()

  #runScanner_({'trnTblCoilSteps : 0},4)
  runScanner_({'turnTblTtlSteps':0, 'turnTblCoilState':4,
                'radiusTtlSteps':0, 'radiusCoilState':4 })
  


#################################run##########################################
runScanner()

#testWrapDegrees()
#testGetDegreeFromTotalStepsTaken(388,1552)
