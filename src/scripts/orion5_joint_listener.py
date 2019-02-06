#!/usr/bin/env python

import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import serial.tools.list_ports
from math import pi
from math import degrees, radians
# import Orion5
import orion5
from orion5 import orion5_math
import time


NUM_JOINTS = 5
joints = {'base_servo':0, 'shoulder':1, 'elbow': 2, 'wrist': 3, 'claw': 4}


class joint_state_publisher():
    pub = rospy.Publisher('joint_vals', JointState, queue_size=10)
    # Create a JointState variable
    pose = JointState()
    pose.header = Header()
    pose.name = ['base_servo', 'shoulder', 'elbow', 'wrist', 'claw']
    pose.velocity = []
    pose.effort = []
    # Publish message and wait 5 second for the robot to run
    def publishJointState(self):
        joint_values = orion.getAllJointsPosition()
        for i in range(len(joints)):
            joint_values[i] = radians(joint_values[i])
        joint_values[joints['claw']] = (joint_values[joints['claw']])/10000 + 0.01
        self.pose.position = joint_values
        self.pose.header.stamp = rospy.Time.now()
        self.pub.publish(self.pose)

def pub_callback(data):
    publisher.publishJointState()


def callback(data):

    r = rospy.Rate(1) # 10hz

    try:
        # fires when the subscribed node hears the message

        names = data.name
        position = data.position

	'''

        print('Base servo: {}'.format(position[joints['base_servo']]))
        print('Shoulder: {}'.format(position[joints['shoulder']]))
        print('Elbow: {}'.format(position[joints['elbow']]))
        print('Wrist: {}'.format(position[joints['wrist']]))
        print('Claw: {}'.format(position[joints['claw']]))
        print('\n')
	'''

        #print(orion)


        # Set the base servo
        # Map [0,6.28] to interval [0,360]
        base_servo_position = degrees(position[joints['base_servo']])
        # orion.setJointPosition(orion.BASE,base_servo_position)

        # Set the Shoulder
        # Note: the shoulder joint limits are [3.5,122.5] degrees.
        # But the shoulder joint has a gearbox which changes the actual
        # angle that the servomotor will reach. (perhaps this is to mitigate
        # the large torques exerted on the bicep link?)
        # SO the actual angles that are sent to the shoulder joint should be
        # mapped from [3.5,122.5] degrees to [10,350] degrees.
        shoulder_servo_position = degrees(position[joints['shoulder']])
        # orion.setJointPosition(orion.SHOULDER, shoulder_servo_position)

        # Set the elbow servo
        elbow_servo_position = degrees(position[joints['elbow']])
        # orion.setJointPosition(orion.ELBOW, elbow_servo_position)

        # Set the wrist servo
        wrist_servo_position = degrees(position[joints['wrist']])
        # orion.setJointPosition(orion.WRIST, wrist_servo_position)

        # Set the claw servo
        # The urdf model uses a prismatic joint for the claw.
        # Need to convert from distance in metres [0.01,0.04]
        # to degrees [20, 359]
        # Need f(x) such that f(0.01) = 20 and f(0.04) = 359
        # f' = (359-20)/(0.04-0.01) = 11300
        # so phi = 11300x + C
        # For x = 0.01: 20 = 11300*0.01 + C -> C = 20 - 11300*0.01 = -93
        # So f(x) = 11300*x - 93

        claw_servo_position = 70 + 5000*position[joints['claw']]
        # orion.setJointPosition(orion.CLAW, claw_servo_position)
        jointValues = [
                    base_servo_position,
                    shoulder_servo_position,
                    elbow_servo_position,
                    wrist_servo_position,
                    claw_servo_position
                  ]

        orion.setAllJointsPosition(jointValues)
    except KeyboardInterrupt:

        rospy.signal_shutdown('Keyboard interrupt')
        quit()

def listener():
    while not rospy.is_shutdown():
        try:
            rospy.init_node('orion5_joint_listener', anonymous=True)
            rospy.Subscriber('joint_goal', JointState, callback)
            rospy.Timer(rospy.Duration(0.1), pub_callback)
            publisher.publishJointState()
            rospy.spin()

        except KeyboardInterrupt:

            rospy.signal_shutdown('Keyboard interrupt')
            quit()


if __name__ == '__main__':


    global orion
    global publisher
    print("Initialising")
    time.sleep(5)

    orion = orion5.Orion5()
    publisher = joint_state_publisher()
    print('running listener')

    listener()
