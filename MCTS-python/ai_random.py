#!/usr/bin/env python3

# A random decision-making agent

import random
from class_support import Actions
from ai_interface import AI_interface

class randomAI(AI_interface):
	"""Random decision-making agent"""
	def __init__(self, nickname):
		super(randomAI, self).__init__(nickname)
		return

	def chooseStarter(self):
		return random.choice(tuple(self.state.getPlayers()))
		
	def chooseAction(self, reachableCells, buildableCells, canPlaceWorker, canPass):
		# Selects a random action
		actionList = []
		if(canPlaceWorker):	
			actionList.append(Actions.PLACE)
		if(reachableCells is not None
				and (len(reachableCells) > 0 
				and len(reachableCells[0][1]) > 0
				or (len(reachableCells) > 1 and len(reachableCells[1][1]) > 0 ))):
			actionList.append(Actions.MOVE)
		if(buildableCells is not None
				and (len(buildableCells) > 0 
				and len(buildableCells[0][1]) > 0
				# or (reachableCells is not None and len(reachableCells) > 1 and len(buildableCells[1][1]) > 0 ))):
				or (len(buildableCells) > 1 and len(buildableCells[1][1]) > 0 ))):
			actionList.append(Actions.BUILD)
		if(canPass):
			actionList.append(Actions.PASS)

		try:
			action = random.choice(actionList)
		except IndexError:
			return Actions.LOSE, None

		data = None
		if(action == Actions.PLACE):		
			data = self.placeWorker()
		elif(action == Actions.MOVE):
			data = self.moveWorker(reachableCells)
		elif(action == Actions.BUILD):
			data = self.build(buildableCells)

		return action, data

	def placeWorker(self):
		placeable = self.state.getPlaceableWorkers(self.getNickname())
		
		newWorker = random.choice(tuple(placeable))
				
		# Finds an empty cell
		row = random.randint(0, self.state.getNrows() - 1)
		column = random.randint(0, self.state.getNcols() - 1)
		while(not self.state.isEmpty(row, column)):
			row = random.randint(0, self.state.getNrows() - 1)
			column = random.randint(0, self.state.getNcols() - 1)
		
		return {"id": newWorker, "row": row, "column": column}

	def moveWorker(self, reachableCells):
		chosenWorkerObj = random.choice(reachableCells)
		workerCoordinates = chosenWorkerObj[0]
		
		while(len(chosenWorkerObj[1]) == 0):
			chosenWorkerObj = random.choice(reachableCells)
			workerCoordinates = chosenWorkerObj[0]

		destination = random.choice(chosenWorkerObj[1])

		return {"src_row": workerCoordinates['row'], "src_col": workerCoordinates['column'], 
			"dst_row": destination['row'], "dst_col": destination['column']}

	def build(self, buildableCells):
		chosenWorkerObj = random.choice(buildableCells)
		workerCoordinates = chosenWorkerObj[0]
		
		while(len(chosenWorkerObj[1]) == 0):
			chosenWorkerObj = random.choice(buildableCells)
			workerCoordinates = chosenWorkerObj[0]
		
		destination = random.choice(chosenWorkerObj[1])
		level = random.choice(destination[1])

		return {"src_row": workerCoordinates['row'], "src_col": workerCoordinates['column'], 
			"dst_row": destination[0]['row'], "dst_col": destination[0]['column'], "level": level}
