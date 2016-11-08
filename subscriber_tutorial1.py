#!/usr/bin/env python
from environment import Simulation
from std_msgs.msg import String
import pygame
import rospy

# This will be your subscriber node.
# You will need to create a callback function.
# You will need to move sim.move(command) inside the callback function.
# command can only be one of the following "south", "north", "west", "east".
# Remember to initiate a ROS node and subscribe to the topic /cmd.

def callback(msg):
	done, state = sim.move([msg.data])

def main():
    rospy.init_node('subs', anonymous=True)
    pub = rospy.Subscriber('cmd', String, callback)
    done = False
    while not done:
    	pass


if __name__ == '__main__':
	sim = Simulation("/home/sahabi/catkin_ws/src/wiald/src/config.txt") # absolute path is better
	main()
