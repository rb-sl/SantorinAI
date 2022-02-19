#!/usr/bin/env python3

# State representation from the model

import numpy as np
import copy

class State:
	"""Abstraction of the model"""
	def __init__(self, model = None):
		# Controls the initialization, that can come from the model or,
		# if in simulated state, from another state
		if(model is not None):
			self.updateFromModel(model)
		return

	def updateFromModel(self, model):
		self.model = model
		# Copies model elements in order to modify them
		self.workers = copy.deepcopy(self.model.getWorkers())
		self.board = np.array(self.model.getBoard().getCells())

		self.stateReduce()
		
		return

	def stateReduce(self):
		"""State reducer based on symmetries"""

		selfWorkers = self.workers.get(self.model.getNickname())

		if(selfWorkers is None):
			return

		a = selfWorkers.get("M")
		b = selfWorkers.get("F")

		if(a is None or b is None):
			return

		# Worker wrt which the board is rotated; legal final positions,
		# both theoretical and in representation:
		# 4 X X X X X    0 _ _ _ X X
		# 3 X X X X X    1 _ _ _ X X
		# 2 _ _ _ X X => 2 _ _ _ X X
		# 1 _ _ _ X X    3 X X X X X
		# 0 _ _ _ X X    4 X X X X X
		#   0 1 2 3 4	   0 1 2 3 4
		w1 = a

		# Worker wrt which the board is mirrored; legal final positions,
		# both theoretical and in representation:
		# 4 X X X X _    0 _ _ _ _ _
		# 3 X X X _ _    1 X _ _ _ _
		# 2 X X _ _ _ => 2 X X _ _ _
		# 1 X _ _ _ _    3 X X X _ _
		# 0 _ _ _ _ _    4 X X X X _
		#   0 1 2 3 4      0 1 2 3 4
		w2 = b

		# If a worker is in the center both conditions are applied
		# to the other
		if(w1['row'] == w1['column'] == 2):
			w1 = b
		elif(w2['row'] == w2['column'] == 2):
			w2 = a

		# Rotations wrt the first worker
		while(w1['row'] > 2 or w1['column'] > 2):
			self.board = np.rot90(self.board)
			for player in self.workers.values():
				for worker in player.values():
					# Updates workers by taking the rotation of rows and columns;
					# due to the representation the 4- is on new rows
					worker['row'], worker['column'] = 4 - worker['column'], worker['row']
		
		# Mirroring wrt the second worker
		if(w2['column'] < w2['row']):
			self.reflectDiag()

		# Further symmetry check on axis 
		symX = False
		symY = False
		symXY = False
		if(w1['row'] == w2['row'] == 2):
			symX = True
		elif(w1['column'] == w2['column'] == 2):
			symY = True
		elif(w1['row'] == w1['column'] and w2['row'] == w2['column']):
			symXY = True
		
		# If w1 and w2 do not define a symmetry axis the state is unique
		if(not symX and not symY and not symXY):
			return
		
		# Otherwise, further checks are performed on the opponent's workers
		opponent = (set(self.getPlayers()) - {self.model.getNickname()}).pop()
		opponentWorkers = self.workers.get(opponent)

		if(opponentWorkers is None):
			return
		
		w3 = opponentWorkers.get("M")
		w4 = opponentWorkers.get("F")

		# If w3 is not valid w4 is used; if it isn't either,
		if(w3 is None or
				symX and w3['row'] == w1['row'] or
				symY and w3['column'] == w1['column'] or
				symXY and w3['row'] == w3['column']):
			if(w4 is None or
					symX and w4['row'] == w1['row'] or
					symY and w4['column'] == w1['column'] or
					symXY and w4['row'] == w4['column']):
				# Final check for building symmetry
				if(symX):
					for i in range(0, 2): # Avoids repeating checks
						for j in range(0, 5):
							if(self.board[i][j].getTopLevel() > self.board[4 - i][j].getTopLevel()):
								self.reflectX()
								return
				elif(symY):
					for i in range(0, 5):
						for j in range(0, 2): # Avoids repeating checks
							if(self.board[i][j].getTopLevel() > self.board[i][4 - j].getTopLevel()):
								self.reflectY()
								return
				elif(symXY):
					for i in range(0, 5):
						for j in range(i + 1, 5): # Avoids repeating checks
							if(self.board[i][j].getTopLevel() > self.board[j][i].getTopLevel()):
								self.reflectDiag()
								return
				return
			else:
				wCheck = w4
		else:
			wCheck = w3

		if(symX and wCheck['column'] > 2):
			self.reflectX()
		elif(symY and wCheck['row'] > 2):
			self.reflectY()
		elif(symXY and wCheck['column'] < wCheck['row']):
			self.reflectDiag()
		return

	# Transform functions; symmetries are based on axis
	#     y    D
	# C C | C /
	# C C | / C
	# --------- x
	# C / | C C
	# / C | C C
	def reflectX(self):
		"""Reflection function for rows"""
		self.board = np.flipud(self.board)
		# Worker rows are updated to reflect the change
		for player in self.workers.values():
			for worker in player.values():
				worker['row'] = 4 - worker['row']
		return
	
	def reflectY(self):
		"""Reflection function for columns"""
		self.board = np.fliplr(self.board)
		# Worker columns are updated to reflect the change
		for player in self.workers.values():
			for worker in player.values():
				worker['column'] = 4 - worker['column']
		return

	def reflectDiag(self):
		"""Reflection function over the diagonal"""
		self.board = np.rot90(np.fliplr(self.board))
		# Updates workers by swapping rows and columns
		for player in self.workers.values():
			for worker in player.values():
				worker['row'], worker['column'] = worker['column'], worker['row']
		return
	
	def isEmpty(self, abstractRow, abstractColumn):
		"""Checks if the cell has no worker nor dome"""
		cell = self.board[abstractRow][abstractColumn]
		return (cell.getOwner() is None) and (4 not in cell.getLevelList())

	def getPlaceableWorkers(self, nickname):
		"""Obtains the Ids of workers that can be placed"""
		placeable = copy.copy(self.getWorkerList())
		placed = self.workers.get(nickname)
		if(placed is None):
			return placeable

		for key in placed.keys():
			placeable.remove(key)
		return placeable

	def getWorkers(self):
		return self.workers

	def getPhysicalCoordinates(self, virtualCoord):
		"""Obtains the cell corresponding to the transformed coordinates"""
		cell = self.board[virtualCoord['row']][virtualCoord['column']]

		return {"row": cell.getRow(), "column": cell.getColumn()}

	def getCell(self, coord):
		return self.board[coord['row']][coord['column']]

	def getBoard(self):
		return self.board

	# Passing model parameters
	def getModel(self):
		return self.model

	def getPlayers(self):
		return self.model.getPlayerList()
	
	def getWorkerList(self):
		return self.model.getWorkerList()

	def getNrows(self):
		return self.model.getNrows()

	def getNcols(self):
		return self.model.getNcols()
	