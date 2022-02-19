from hashlib import new
from threading import active_count

from numpy.lib.function_base import append
from state import State
import copy
import numpy as np

class simulatedState(State):
	"""Class to simulate a state playout"""
	def __init__(self, state, activePlayer = None):
		super(simulatedState, self).__init__()

		self.model = state.getModel()
		self.workers = copy.deepcopy(state.getWorkers())
		self.board = copy.deepcopy(state.getBoard())

		if(activePlayer is None):
			activePlayer = state.activePlayer

		self.activePlayer = activePlayer
		self.inactivePlayer = (set(state.getPlayers()) - {activePlayer}).pop()
		self.nPlaced = 0
		self.movedWorker = None
		self.hasBuilt = False
		self.hasLost = False
		return

	def goalTest(self):
		if(self.hasLost):
			return self.inactivePlayer

		for player in self.workers:
			for worker in self.workers[player]:
				cell = self.getCell(self.workers[player][worker])
				if(cell.getTopLevel() == 3):
					return player
		return None

	def placeWorker(self, id, row, column):
		"""Returns a new state with a new worker in the given coordinates"""
		newState = simulatedState(self)
		
		newState.board[row][column].setOwner(self.activePlayer)
		newState.board[row][column].setId(id)
		try:
			newState.workers[self.activePlayer][id] = {"row": row, "column": column}
		except Exception as e:
			newState.workers[self.activePlayer] = {id: {"row": row, "column": column}}

		newState.nPlaced = self.nPlaced + 1
		newState.stateReduce()
		return newState

	def allReachableCells(self):
		"""Returns the list of all cells reachable from the state"""
		cells = []
		workers = self.getWorkers().get(self.activePlayer)
		
		if(workers is not None and not self.hasBuilt):
			for worker in workers:
				c = self.reachableCells(workers[worker]['row'], workers[worker]['column'])
				if(c is not None):
					cells.append(c)
		
		return cells

	def reachableCells(self, src_row, src_col):
		"""Returns the list of cells that can be reached from row/col"""
		if(self.movedWorker is not None):
			return None
		
		reach = []
		current = self.board[src_row][src_col]
		for i in range(max(src_row - 1, 0), min(src_row + 2, 5)):
			for j in range(max(src_col - 1, 0), min(src_col + 2, 5)):
				row = self.board[i]
				if(row is not None):
					cell = row[j]
					if(cell is not None 
							and cell.getTopLevel() - current.getTopLevel() < 2
							and cell.isFree()):
						reach.append({"row": i, "column": j})

		return [{"row": src_row, "column": src_col}, reach]

	def moveWorker(self, src_row, src_col, dst_row, dst_col):
		"""Returns a new state with the worker in src moved to dst"""
		newState = simulatedState(self)

		# Frees the old cell
		src = newState.board[src_row][src_col]
		owner = src.getOwner()
		id = src.getId()

		src.setOwner()
		src.setId()

		# Sets the worker on the new cell
		dst = newState.board[dst_row][dst_col]
		dst.setOwner(owner)
		dst.setId(id)
		newState.workers[owner][id] = {"row": dst_row, "column": dst_col}
		
		# Updates state info
		newState.movedWorker = id

		newState.stateReduce()
		return newState

	def buildableCells(self):
		build = []
		workers = self.workers.get(self.activePlayer)
		if(workers is None or self.movedWorker is None):
			return []

		coord = workers.get(self.movedWorker)
		for i in range(max(coord["row"] - 1, 0), min(coord["row"] + 2, 5)):
			for j in range(max(coord["column"] - 1, 0), min(coord["column"] + 2, 5)):
				row = self.board[i]
				if(row is not None):
					cell = row[j]
					if(cell is not None and cell.isFree()):
						build.append([{"row": i, "column": j}, [cell.getTopLevel() + 1]])
		return [[coord, build]]

	def build(self, dst_row, dst_col, level):
		"""Returns a new state with a new building in dst"""
		newState = simulatedState(self)
		newState.board[dst_row][dst_col].addLevel(level)

		newState.hasBuilt = True

		newState.stateReduce()
		return newState

	def canPass(self):
		return self.hasBuilt or self.nPlaced == 2

	def passTurn(self):
		# if(self.activePlayer == "SantorinAI"):
		# 	next = 
		# else:
		newstate = simulatedState(self)
		newstate.activePlayer, newstate.inactivePlayer = newstate.inactivePlayer, newstate.activePlayer
		return newstate

	# def newTurn(self, nickname = None):
	# 	if(nickname is not None):
	# 		nickname = (set(self.getPlayers()) - set(self.activePlayer)).pop()
	# 	self.activePlayer = nickname
	# 	self.nPlaced = 0
	# 	self.movedWorker = None
	# 	self.hasBuilt = False

	def getMovedWorker(self):
		return self.movedWorker

	def setMovedWorker(self, worker):
		self.movedWorker = worker

	def getActivePlayer(self):
		return self.activePlayer

	def __eq__(self, s: object) -> bool:
		"""Override for equality comparison of states"""
		# If the two are the same object they are the same
		# if(super().__eq__(s)):
		# 	return True
		
		# Checks for attribute equality
		# if(self.activePlayer != s.activePlayer or self.nPlaced != s.nPlaced
		# 		or self.movedWorker != s.movedWorker or self.hasBuilt != s.hasBuilt
		# 		or self.hasLost != s.hasLost):
		# 	return False

		workers2 = s.getWorkers()

		# If the players are different the states are too
		if(set(self.workers.keys()) != set(workers2.keys())):
			return False

		for player in set(self.workers).union(set(workers2)):
			# Checks they have the same workers
			if(set(self.workers[player].keys()) != set(workers2[player].keys())):
				return False
			
			# Checks for same coordinates of workers
			for id in self.workers[player]:
				if(self.workers[player][id]['row'] != workers2[player][id]['row']
						or self.workers[player][id]['column'] != workers2[player][id]['column']):
					return False

		# Checks for equality of build levels
		for i in range(0, 5):
			for j in range(0, 5):
				if(self.getBoard()[i][j].getTopLevel() != s.getBoard()[i][j].getTopLevel()):
					return False
			
		return True