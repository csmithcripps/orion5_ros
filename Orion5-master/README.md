# Orion5 Robotic Arm

_Please read through the Quick Start Guide and watch the videos before using Orion5_
### Orion5 Quick Start Guide: https://goo.gl/DQm3x3
### Orion5 User Manual: https://goo.gl/h3i2br
### Orion5 Tutorial Videos: https://goo.gl/5tkjUF

## Install Dependencies
_Follow these steps before attempting to use the Python or MATLAB libraries, or the Visualiser_
1. Install python 3.6.2 on your machine: https://www.python.org/downloads/
2. Windows users: Make sure to select the "Add python to environment variables" option while installing.
3. Install dependencies for libraries using `pip3 install pyserial pyglet`.
4. If the pip3 command is not found, navigate to your Python install directory, on Windows this is usually `C:\Users\<username>\AppData\Local\Programs\Python\Python36-32`, enter the `Scripts` directory and launch a Powershell window using `Shift + RightClick`, and then try `./pip3 install pyserial pyglet`.

## MATLAB Library
_In order to use the MATLAB library, the `Orion5_Server.py` Python program is required to run in the background; it acts as an interface between MATLAB and the Orion5 Robotic Arm_
### Python Server
1. The program `Orion5_Server.py` is required to be running in the background to use the MATLAB library.
2. If the 'Install Dependencies' steps above have been completed, launch the `Orion5_Server.py` program by double clicking it or by running `python3 Orion5_Server.py` in the Libraries directory.
3. The serial port name of the Orion5 robotic arm should be printed in the terminal if found, otherwise the program will keep waiting until it is able to find one. Press `Ctrl+C` to exit the program.
4. The message `Waiting for MATLAB` means the program is ready to communicate with MATLAB.
5. The message `Connected to MATLAB` means your MATLAB script is currently running and communicating with the `Orion5_Server.py`.
6. If your MATLAB script crashes midway or does not call the `<library_reference>.stop()` function correctly upon completion, a socket may be kept open from MATLAB to `Orion5_Server.py`. This may appear as an `OS Error` in python, or a `socket error` in MATLAB next time you run your script. Simply call the `<library_reference>.stop()` function in the MATLAB console to cleanly exit the Orion5.m library.
7. Press `Ctrl+C` to quit the server cleanly.

### Basic Usage 
The library pings the Python server every second if no other library functions are being called, this is like a watchdog timer, if Python server doesn't hear anything for 5 seconds, it will return to waiting for a new connection.  
The MATLAB script `test_script.m` demonstrates some of the functionality.

#### Create an instance of the library
```matlab
orion = Orion5();
```

#### Cleanup and quit an instance
```matlab
orion.stop();
```

#### Joint ID constants
Use these constants to select which joint to interact with.
```matlab
Orion5.BASE
Orion5.SHOULDER
Orion5.ELBOW
Orion5.WRIST
Orion5.CLAW
```

#### Notes about control mode
The smart servos used in Orion5 have a number of control modes; namely `POS_SPEED`, `POS_TIME` and `VELOCITY`.

**POS_SPEED:** The servo will move towards the desired goal position (set using `setJointPosition`) at the desired speed (set using `setJointSpeed`) after moving through its acceleration profile.

**POS_TIME:** The servo will move towards the desired goal position (set using `setJointPosition`) and arrive there in a specified amount of time (set using `setJointTimeToPosition`). Time is passed to the function as seconds, and the time can have a resolution of 100ms.

**VELOCITY:** In this mode the servo will move at the speed set by `setJointSpeed` or `setAllJointsSpeed` and ignore desired position and hard angle limits set in the servo by the embedded electronics. Users must make sure to read servo positions in a high frequency control loop to avoid driving joints through each other. There is no acceleration profile in this mode; so users will have to consider this in their control system implementations - Otherwise inertia of moving joints will damage gearboxes and make for not-very-smooth motion.

_(Embedded processor enables Orion5 to prevent users from driving joints through each other. However do not rely on this in your control loop as it enables emergency stop mode, requiring user intervention to resolve. See the user manual (https://goo.gl/h3i2br) for more details.)_

#### To set the control mode for each joint
The following constants are available in the Orion5.m library.

```matlab
Orion5.POS_SPEED
Orion5.POS_TIME
Orion5.VELOCITY

```
This function will set the desired control mode for a specified joint.
```matlab
orion.setJointControlMode(Orion5.BASE, Orion5.POS_TIME);
```

### Getters and Setters for all joints

#### Read all joint positions
This will return an array of 5 angles in degrees in the range 0-359 for all joints.  
You can use the Joint ID constants to index this array.
```matlab
all_positions = orion.getAllJointsPosition();
```

#### Read all joint speeds
This will return an array of 5 speeds, servo speed is represented as a 10 bit number (0-1023).  
The conversion to RPM is shown in the example below.  
You can use the Joint ID constants to index this array.
```matlab
all_speeds = orion.getAllJointsSpeed();
shoulder_speed_RPM = all_speeds(Orion5.SHOULDER) * 0.110293;
```

#### Read all joint loads
This will return an array of 5 values representing the current load on each joint.  
Load for the G15 servos is an arbitrary value representing the electrical current through the motor.  
The load value is a 10 bit number (0-1023).  
You can use the Joint ID constants to index this array.
```matlab
all_loads = orion.getAllJointsLoad();
```

#### Set all joint positions
This function takes an array of 5 angles in degrees, in the range 0-359, and sets the position for all joints in one function call.  
This method is several times faster than calling the `setJointPosition` function separately for each joint.
```matlab
positions = [0 216.8 62.5 225.94 30];
orion.setAllJointsPosition(positions);
```

#### Set all joint speeds
This function takes an array of 5 speeds, in the range 0-1023, and sets the speed for all joints in one function call.  
This method is several times faster than calling the `setJointSpeed` function separately for each joint.  
**Set the direction of the velocity by wrapping the desired speed with the `CWVelocity(v)` and `CCWVelocity(v)` functions - for clockwise, and counter-clockwise movement respectively.**  
_(A future update will use the sign of the velocity to determine the direction)_  
**Make sure to set control mode to `Orion5.POS_SPEED` or `Orion5.VELOCITY` before calling this function.**  
_Read more about control mode at the top of this file_
```matlab
speeds = [0 0 CWVelocity(120) CCWVelocity(90) 0];
orion.setAllJointsSpeed(speeds);
```

#### Set all joints torque enable setting
The G15 servos have a torque enable setting, if enabled in position mode this means the servos will hold their position using motor torque.  
Be aware that if torque is disabled in position mode the servo will still move.  
If torque is disabled in velocity mode, the servo should stop moving suddenly, the same effect as setting speed to 0.
```matlab
orion.setAllJointsTorqueEnable([1 1 1 1 0]);
```

### Getters and Setters for one joint

#### Read a joint position
This will return an angle in degrees in the range 0-359 for one joint specified using the Joint ID constants.
```matlab
shoulder_pos = orion.getJointPosition(Orion5.SHOULDER)
```

#### Read a joint Speed
This will return a speed as a 10 bit number for one joint. Find the conversion factor for RPM above.
```matlab
elbow_speed = orion.getJointSpeed(Orion5.ELBOW)
```

#### Read a joint load
This will return the load for a single joint - represented as a 10 bit number. Read above for more information.
```matlab
shoulder_pos = orion.getJointLoad(Orion5.WRIST)
```

#### Set a joint position
This takes an angle in degrees in the range 0-359.
```matlab
orion.setJointPosition(Orion5.ELBOW, 135)
```

#### Set a joint speed
This function sets the speed for the specified servo.  
**Please read the notes about `setAllJointsSpeed` above**  
_Read more about control mode at the top of this file_
```matlab
orion.setJointPosition(Orion5.ELBOW, 135)
```

#### Set a time to position
This function will set the speed such that the specified joint will arrive at the goal position in `time` seconds.  
**Make sure to set control mode to `Orion5.POS_TIME` before calling this function**
```matlab
orion.setJointTimeToPosition(Orion5.SHOULDER, time)
```

#### Turn on/off torque for one servo
```matlab
% turn on
orion.setJointTorqueEnable(Orion5.WRIST, 1)

% turn off
orion.setJointTorqueEnable(Orion5.BASE, 0)
```

### Configuration Values
There are several configuration values that are writable from user software. These variables are stored in volatile memory, so remember to set these each time you power cycle Orion5. Offsets can be used to correct any missaligned joints, such as the shoulder or base. 

**Offset angles are integers in units of 0-1087, which corresponds to the range 0-359**
```matlab
angle1087 = int32(angle360 * 1088.0 / 360.0)
```

Configuration values include:
* **baseOffset:** Offset angle added to base angle in embedded firmware, default is 0.
* **shoulderOffset:** Offset angle added to shoulder angle in embedded firmware, default is 0.
* **elbowOffset:** Offset angle added to elbow angle in embedded firmware, default is 0.
* **wristOffset:** Offset angle added to wrist angle in embedded firmware, default is 0.
* **clawOffset:** Offset angle added to claw angle in embedded firmware, default is 0.
* **clawLoadLimit:** Value between 0-1023, claw won't move if load exceeds this, default is 180.
* **fieldInflation:** This value inflates the protection fields of each joint, default is 3mm.
* **clawHomePos:** This value sets the position that claws move to when Claw Home Button is used, default is 120.

**To change one of these configuration values**
```matlab
orion.setConfigValue('clawLoadLimit', 250);
```

### Known Issues & Future Work
* If user MATLAB code calling the library crashes, the *keep alive* ping will keep happening in the background. Users can stop this by running `<library_instance>.stop()` in MATLAB console. It would be best to surround your code with a try/catch structure.
* Most functionality is implemented, we are working on making a nicer interface for setting/getting positions in deg360, deg180 and radians.
* We are considering adding the capability to alter the acceleration profile and torque settings etc from MATLAB.

## Python 3d Visualiser Controller
The `Orion5 Controller.py` program is a 3d controller and visualiser made in Python; it implements OpenGL for graphics rendering.
The visualiser is designed as an aid to understand the 5 degrees of freedom of Orion5, and also as a way to control the robotic arm visually.

On launch the program will ask you to select a serial port, if you have an Orion5 connected select its serial port.  
Users can drag the white squares (they are like scroll bars) to move the arm around using our 6 DoF controller.  
The controller sets the tool-point of the robotic arm in cylindrical coordinates, along with tool attack configuration.

The scrollbar controls are:
* **Far-left:** Z height
* **Inner-left:** Tool attack angle in plane of joints
* **Middle-top:** Rotation of arm
* **Middle-bottom:** Tool-point radius
* **Inner-right:** Tool attack distance (sets the point at which tool attack rotates about)
* **Far-right:** Claw open/close

### Dependencies:
* Python 3.6
* pip
* pyserial
* pyglet

Install these dependencies with:

```
pip3.6 install pyglet, pyserial
```

### Keyboard Controls:
* A - toggle - Put the visualiser into "Arm controls 3d model" mode
* Q - toggle - Put the visualiser into "3d model controls arm" mode
* Right - Extends tool point
* Left - Retracts tool point
* Up - Tool point up
* Down - Tool point down
* Home - Attack angle down
* PageUp - Attack angle up
* PageDown - Claw close
* END - Claw open
* Delete - Attack distance out
* Backspace - Attack distance in
* CTRL_Left - Slew left
* CTRL_Right - Slew right
* CTRL_END - Read from arm
* CTRL_HOME - Write to arm

### Mouse Controls
* Left click drag: Rotates model by X/Y axis
* Shift + Left click drag: Rotates model by X/Z axis
* Right click drag: Pans the model around
* Scroll wheel: Zoom

### Experimental Controls
* D - Record position to current sequence in memory
* E - Force current position to be current sequence element
* S - cycle sequence toward the end (wraps)
* W - Cycle sequence toward the start (wraps)
* Z - Play sequence currently loaded
