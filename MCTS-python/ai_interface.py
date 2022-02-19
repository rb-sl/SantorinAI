#!/usr/bin/env python3

# Decision agent interface

from game_model import Model
from state import State
import random
from datetime import datetime
import copy

from numpy import mod
from class_support import Actions
import state

class AI_interface:
	def __init__(self, nickname):
		self.nickname = nickname
		return

	def createState(self, model: Model):
		"""Creates the current game's state for the agent"""
		self.state = state.State(model)
		random.seed(datetime.now())
		return

	def setState(self, state: State):
		"""Sets the current game's state for the agent"""
		self.state = copy.deepcopy(state)
		random.seed(datetime.now())
		return

	def updateState(self, model: Model):
		"""Updates the internal state using the given model"""
		self.state.updateFromModel(model)
		return

	def chooseStarter(self) -> str:
		"""Method to return the chosen starter"""
		pass

	def chooseAction(self, reachableCells: list, buildableCells: list, canPlaceWorker: bool, canPass: bool):
		"""Decision-making method for the game"""
		pass

	def getNickname(self):
		return self.nickname