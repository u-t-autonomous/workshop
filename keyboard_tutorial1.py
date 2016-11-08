from environment import Simulation
import pygame

def make_move():
    key_input = raw_input("What's your move? ")
    done, state = sim.move([key_input]) #main call

def main():
    done = False
    while not done:
        make_move()


if __name__ == '__main__':
    sim = Simulation("config.txt") # absolute path is better
    main()
