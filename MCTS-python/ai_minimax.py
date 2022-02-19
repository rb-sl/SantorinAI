#!/usr/bin/env python3

# A decision-making agent based on minimax

import random
from class_support import Actions
from ai_interface import AI_interface

# ----------
# Parameters
# ----------

starter = 0.5

class miniMaxAI(AI_interface):
	def __init__(self, nickname):
		super(miniMaxAI, self).__init__(nickname)
		return

	def chooseStarter(self):
		return random.choice(tuple(self.model.getPlayerList()))

        
	def chooseAction(self, reachableCells, buildableCells, canPlaceWorker, canPass):
		
		return