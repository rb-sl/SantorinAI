#!/usr/bin/env python3
import json
#import numpy as np

from class_support import Color

# -------------
# Parameters
# -------------

class Model:
	"""Class representing the game model"""

	godsPath = "config/gods.json"
	boardPath = "config/board.json"

	def __init__(self, nickname, players):
		self.nickname = nickname
		self.players = players
		self.nPlayers = len(players)
		self.workers = {}
		self.activePlayer = None
		
		# Reading configuration for board, raises exception
		# if format is wrong
		with open(self.boardPath, "r") as boardFile:
			# Check for JSON syntax
			try:
				boardConf = json.load(boardFile)
			except Exception as e:
				raise ValueError("JSON decode error for '" + self.boardPath + "': " + e.args[0])

			# Check for workers per playeer
			self.workersPerPlayer = boardConf['workersPerPlayer']
			if(self.workersPerPlayer <= 0):
				raise ValueError("Wrong workers per player: " + repr(self.workersPerPlayer) + " (Must be at least 1)")
			
			# Check for board dimensions
			self.columns = boardConf['nCol']
			self.rows = boardConf['nRow']
			if(self.columns <= 0 or self.rows <= 0 or self.columns * self.rows < self.workersPerPlayer * self.nPlayers):
				raise ValueError("Wrong board dimension: " + repr(self.columns) + "x" + repr(self.rows) 
								 + " and must be at least " + repr(self.workersPerPlayer * self.nPlayers) + " cells")
			
			# Check for worker ids
			self.workerList = boardConf['workerSex']
			if(len(self.workerList) != self.workersPerPlayer):
				raise ValueError("Number of workers per player and number of worker identifiers do not coincide: " 
								 + repr(self.workersPerPlayer) + " vs " + repr(len(self.workerList)) + " (Numbers must coincide)")

			# Check for id uniqueness
			if(len(self.workerList) != len(set(self.workerList))):
				raise ValueError("Duplicate Worker identifier (Worker identifiers must be unique)")

			# Board creation
			self.board = Board(self.nickname, self.players, self.rows, self.columns, self.workersPerPlayer)
		return

	def getNickname(self):
		return self.nickname

	def getPlayerList(self):
		"""Getter for the list of players"""
		return list(self.players.keys())

	def getNrows(self):
		"""Getter for the number of rows"""
		return self.rows

	def getNcols(self):
		"""Getter for the number of columns"""
		return self.columns

	def getWorkerList(self):
		"""Getter for the list of worker ids"""
		return self.workerList
	
	def getWorkers(self):
		"""Getter for the active workers"""
		return self.workers
	
	def addWorker(self, key, coordinates):
		"""Setter for a new worker"""
		self.workers[key] = coordinates
		return

	def getBoard(self):
		"""Getter for the board"""
		return self.board

	def update(self, updateMessage, activePlayer):
		"""Updates the board with the given cells"""
		self.activePlayer = activePlayer
		for list in updateMessage:
			self.board.setCell(list[0], list[1])

			# Updates the dict of workers if needed
			owner = list[1].get('workerOwner')
			if(owner is not None):
				id = list[1].get('workerSex')
				try:
					self.workers[owner][id] = list[0]
				except:
					self.workers[owner] = {id: list[0]}
		return
	
	def printBoard(self):
		"""Prints the board"""
		self.board.printCells()
		return
	
	def getActivePlayer(self):
		return self.activePlayer

class Board:
	"""Class for the game board"""

	def __init__(self, nickname, players, rows, columns, nWorkers):
		self.nickname = nickname
		self.players = players
		self.rows = rows
		self.columns = columns
		self.nWorkers = nWorkers

		# Assigning colors
		self.aiColor = Color.CYAN
		self.opponentColors = [Color.YELLOW, Color.RED]
		self.endColor = Color.END

		# Assigning colors to players
		self.playerColors = {nickname: self.aiColor}
		toMap = set(players) - set(nickname)
		while(len(toMap) > 0):
			opponent = toMap.pop()
			if(opponent != nickname):
				self.playerColors[opponent] = self.opponentColors[len(toMap) - 1]
			toMap = toMap - set(opponent)

		# Board initialization
		self.cells = [[Cell(i, j, [0]) for j in range(columns)] for i in range(rows)]

		return

	def setCell(self, coord, update):
		"""Gives properties to a cell"""
		self.cells[coord['row']][coord['column']].setLevels(update['levelList'])
		self.cells[coord['row']][coord['column']].setOwner(update.get('workerOwner'))
		self.cells[coord['row']][coord['column']].setId(update.get('workerSex'))
		return

	def getCells(self):
		"""Returns the matrix"""
		return self.cells

	def getCell(self, coordinates):
		return self.cells[coordinates['row']][coordinates['column']]

	def printCells(self):
		"""Prints the board"""
		for p in self.playerColors:
			print(self.playerColors[p] + p + self.endColor)

		for row in range(self.rows):
			for col in range(self.columns):
				cell = self.cells[row][col]
				owner = cell.getOwner()
				
				if(owner is not None):
					print(self.playerColors[owner], end = '')
				print(repr(cell.getTopLevel()) + self.endColor + " ", end = '')
			print()
		return

class Cell:
	"""Class for board cells"""
	def __init__(self, row, column, levelList, workerOwner = None, workerId = None):
		self.absoluteRow = row
		self.absoluteColumn = column
		self.levelList = levelList
		self.workerOwner = workerOwner
		self.workerId = workerId
		return

	def isFree(self):
		"""Returns true if the cell has not a dome nor a worker"""
		return self.getTopLevel() < 4 and not self.getOwner()

	def getTopLevel(self):
		"""Getter for the max level"""
		return max(self.levelList)

	def getLevelList(self):
		"""Getter for the list of levels"""
		return self.levelList

	def setLevels(self, levelList):
		"""Setter for the list of levels"""
		self.levelList = levelList
		return

	def addLevel(self, level):
		self.levelList.append(level)
 
	def getOwner(self):
		"""Getter for the worker owner"""
		return self.workerOwner

	def setOwner(self, owner = None):
		"""Setter for the worker owner"""
		self.workerOwner = owner
		return

	def getId(self):
		"""Getter for the worker id"""
		return self.workerId

	def setId(self, id = None):
		"""Setter for the worker id"""
		self.workerId = id
		return

	def getRow(self):
		"""Getter for the row"""
		return self.absoluteRow

	def getColumn(self):
		"""Getter for the column"""
		return self.absoluteColumn
		