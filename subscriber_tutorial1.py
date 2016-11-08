from environment import Simulation
import pygame

# This will be your subscriber node.
# You will need to create a callback function.
# You will need to move sim.move(command) inside the callback function.
# command can only be one of the following "south", "north", "west", "east".
# Remember to initiate a ROS node and subscribe to the topic /cmd.

def main():

    sim = Simulation("config.txt")

    done = False

    while not done:

        done, state = sim.move(["south"]) #main call



main()
