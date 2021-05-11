# mlLearningAgents.py
# parsons/27-mar-2017
#
# A stub for a reinforcement learning agent to work with the Pacman
# piece of the Berkeley AI project:
#
# http://ai.berkeley.edu/reinforcement.html
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here was written by Simon Parsons, based on the code in
# pacmanAgents.py
# learningAgents.py

from pacman import Directions
from game import Agent
import random
import game
import util


# QLearnAgent
#
class QLearnAgent(Agent):

    # Constructor, called when we start running the
    def __init__(self, alpha=0.2, epsilon=0.05, gamma=0.8, numTraining=10):
        # alpha       - learning rate
        # epsilon     - exploration rate
        # gamma       - discount factor
        # numTraining - number of training episodes
        #
        # These values are either passed from the command line or are
        # set to the default values above. We need to create and set
        # variables for them
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.gamma = float(gamma)
        self.numTraining = int(numTraining)
        # Count the number of games we have played
        self.episodesSoFar = 0

        # Track score of a game (used to find reward of states)
        self.score = 0

        # Initialise Q-value dict of {(state,action) : Qvalue}
        # Counter object is a useful way of initialising all state-action pairs as 0
        self.q_values = util.Counter()

        # To be able to update the Q value of states we need to store
        # a history the previous state visited and previous action performed
        self.previous_state = None
        self.previous_action = None

    # Accessor functions for the variable episodesSoFars controlling learning
    def incrementEpisodesSoFar(self):
        self.episodesSoFar += 1

    def getEpisodesSoFar(self):
        return self.episodesSoFar

    def getNumTraining(self):
        return self.numTraining

    # Accessor functions for parameters
    def setEpsilon(self, value):
        self.epsilon = value

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, value):
        self.alpha = value

    def getGamma(self):
        return self.gamma

    def getMaxAttempts(self):
        return self.maxAttempts

    def updateQvalue(self, state, action, reward, q_max):
        # Current Q value of (state, action) which we want to update
        qvalue = self.q_values[(state, action)]

        # Q learning update rule
        self.q_values[(state, action)] = qvalue + self.alpha * (reward + self.gamma*q_max - qvalue)

    # Update memory of the current state and action
    def updateMemory(self, new_state, new_action, new_score):
        self.previous_state = new_state
        self.previous_action = new_action
        self.score = new_score

    # Clear memory for the next game
    def resetMemory(self):
        self.previous_state = None
        self.previous_action = None
        self.score = 0

    # getAction
    #
    # The main method required by the game. Called every time that
    # Pacman is expected to move
    def getAction(self, state):

        # Remove STOP from legal actions
        legal = state.getLegalPacmanActions()
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # Find best Q value for current state
        moves = {}
        for act in legal:
            moves[act] = self.q_values[(state, act)]
        bestQ = max(moves.values())

        # Apply one step look-back Q learning update (if not in first step of game)
        if self.previous_state != None:
            # Find reward of previous state
            reward = float(state.getScore() - self.score)
            # Update the previous (state,action) pair with Q learning update
            self.updateQvalue(self.previous_state, self.previous_action, reward, bestQ)

        # Pick what action to take using epsilon greedy selection
        if random.random < self.epsilon:
            pick = random.choice(legal)
        else:
            # Move with max Q value
            pick = max(moves, key=moves.get)

        # Update all necessary items from this step to memory
        score = state.getScore()
        self.updateMemory(state, pick, score)

        return pick

    # Handle the end of episodes
    #
    # This is called by the game after a win or a loss.
    def final(self, state):

        # Still need to perform Q update of final state before endgame.
        # Get reward
        reward = state.getScore() - self.score
        # Now update this (state,action) pair. Q value of next state
        # is 0 since the game is over in next state.
        self.updateQvalue(self.previous_state, self.previous_action, reward, 0)

        # Reset memory for the next game
        self.resetMemory()

        # Keep track of the number of games played, and set learning
        # parameters to zero when we are done with the pre-set number
        # of training episodes
        self.incrementEpisodesSoFar()
        if self.getEpisodesSoFar() == self.getNumTraining():
            msg = 'Training Done (turning off epsilon and alpha)'
            print '%s\n%s' % (msg, '-' * len(msg))
            self.setAlpha(0)
            self.setEpsilon(0)
