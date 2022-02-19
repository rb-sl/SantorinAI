import threading
from numba.core.types.scalars import Boolean
from numpy.lib.function_base import copy
from game_model import Model
from state_simulator import simulatedState

import time
from threading import Thread, Lock
import numpy as np
from ai_random import randomAI
import random
import copy
from class_support import Actions, Color
from ai_interface import AI_interface

from numba import jit, njit

N_ITERATIONS = 10000
N_ROLLOUT = 33
EXPLORATION = np.sqrt(2)

DEPTH_CHECK = 4

global score

class monteCarloAI(AI_interface):
	"""Decision-making agent based on a pure Monte-Carlo approach"""
	def __init__(self, nickname):
		super(monteCarloAI, self).__init__(nickname)
		
		# self.actionBuffer = []

		# To keep between updates
		self.movedWorker = None
		self.opponentActions = []
		return
	
	def createState(self, game):
		super().createState(game)
		self.root = Node(simulatedState(self.state, self.getNickname()))
		self.superRoot = self.root

		global score
		score = {}

		players = self.state.getPlayers()
		nickname = self.getNickname()
		players.remove(nickname)
		opponent = players.pop()
		self.selfAgent = randomAI(nickname)
		self.opponentAgent = randomAI(opponent)
		return 

	def updateState(self, model: Model):
		super().updateState(model)
				
		candidateRoot = Node(simulatedState(self.state, model.getActivePlayer())) # Would be good to just shift
		if(model.getActivePlayer() == self.getNickname()):
			print(Color.YELLOW + "Opponent actions; ", end='')
			while(len(self.opponentActions) > 0):				
				action = self.opponentActions.pop()
				found = False
				for node in self.root.getChildren().keys():
					if(node.getState() == action.getState()):
						print(Color.YELLOW + "Opponent action found; ", end='')
						self.root = node
						found = True
						break
				if(not found):
					print(Color.YELLOW + "Opponent action added; ", end='')
					self.root.addChild(action)
					self.root = action
			
			print(Color.YELLOW + "\nSelf actions; ", end='')

			found = False
			for node in self.root.getChildren().keys():
				if(node.getState() == candidateRoot.getState()):
					self.root = node
					found = True
					print(Color.YELLOW + "Action found; ", end='')
					break
			if(not found):		
				self.root.addChild(candidateRoot)
				self.root = candidateRoot
				print(Color.YELLOW + "Action added; ", end='')
			print(Color.END)
		else:
			if(self.state != self.root.getState()):
				deleteAfter = None
				for a in self.opponentActions:
					# If the current state is found in might be an undo, so subsequent states are deleted
					if(a == self.state):
						deleteAfter = self.opponentActions.index(a)
						break
				if(deleteAfter is not None):
					self.opponentActions = self.opponentActions[:self.opponentActions.index(a) + 1]
				else:
					self.opponentActions.append(candidateRoot)
			else:
				# If the new state is equivalent to the old the list is deleted
				self.opponentActions.clear()
		
		# child = self.findChild(self.root, candidateRoot)

		# if(not child):
		# 	self.root = candidateRoot
		# 	print(Color.YELLOW + "Root not found, restarting" + Color.END)
		# else:
		# 	self.root = child
		# 	print(Color.YELLOW + "NEW ROOT FOUND" + Color.END)

		self.root.getState().setMovedWorker(self.movedWorker)
		return 

	def findChild(self, node, query, depth = 1):
		if(depth > DEPTH_CHECK):
			return None
		
		for child in node.children:
			if(child == query):
				return child

		for child in node.children:
			return self.findChild(child, query, depth+1)

	def chooseStarter(self):
		return random.choice(tuple(self.state.getPlayers()))

	def chooseAction(self, reachableCells, buildableCells, canPlaceWorker, canPass):
		# Assuming a normal game, if the agent can pass, it will
		if(canPass):
			# self.actionBuffer.clear()
			self.movedWorker = None
			return Actions.PASS, None

		# threadList = []
		# for i in range(0, N_THREADS):
		# 	t = MCThread(self, name="MC"+repr(i))
		# 	threadList.append(t)
		# 	t.start()

		# for i in range(0, N_THREADS):
		# 	t.join()

		# maxValue = 0
		# for node in self.root.getChildren():
		# 	if(node.getNsim() == 0):
		# 		continue
		# 	value = node.getNwins() / node.getNsim()
		# 	if(value > maxValue):
		# 		chosenNode = node

		# try:
		# 	self.movedWorker = chosenNode.getState().getMovedWorker()
		# except UnboundLocalError as e:
		# 	print(Color.RED + repr(e.args) + Color.END)
		# 	return

		# If the best action was chosen by a previous iteration it is just sent
		# if(self.actionBuffer):
		# 	nextState = self.actionBuffer.pop()
		# 	return nextState.getAction(), nextState.getData()

		# All other action types will follow the classical MC approach
		for i in range (0, N_ITERATIONS):
			# print("\rIteration", repr(i + 1) + "/" + repr(N_ITERATIONS), end='') 
			leaf = self.MCselection()
			winner = leaf.getState().goalTest()
			if(winner is None):
				self.MCexpansion(leaf)
				try:
					toSimulate = random.choice(list(leaf.getChildren().keys()))
					reward = self.SimToJit(toSimulate)
					self.MCbackup(toSimulate, reward)
				except IndexError as e:
					print(Color.RED + repr(e.args) + Color.END)
					reward = 0
					self.MCbackup(leaf, reward)
			else:
				# print(". Terminal state", end='')
				if(winner == self.getNickname()):
					reward = N_ROLLOUT
				else:
					reward = 0
				self.MCbackup(leaf, reward)
			
			# print(". Result:", repr(reward) + "/" + repr(N_ROLLOUT))

		# maxValue = 0
		# for node in self.root.getChildren():
		# 	if(node.getNsim() == 0):
		# 		continue
		# 	value = node.getNwins() / node.getNsim()
		# 	if(value > maxValue):
		# 		chosenNode = node

		children = self.root.getChildren()
		best = []
		bestValue = -np.inf
		for node in children.keys():
			if(node.getNsim() == 0):
				continue

			value = node.getNwins() / node.getNsim()
			if(value > bestValue):
				bestValue = value
				best.clear()
			if(value >= bestValue):
				best.append(node)
		
		try:
			chosenNode = random.choice(best)
		except:
			return Actions.LOSE, None

		# chosenNode = max(self.root.getChildren(), key = self.root.getChildren().getNwins())
		# If the next action is still for the agent, it is cached and played immediately next
		# if(next(iter(chosenNode.getChildren().keys())).getState().getActivePlayer() == self.getNickname()):
		# 	nextNode = max(chosenNode.getChildren(), key = chosenNode.getChildren().get)
		# 	self.actionBuffer.append(nextNode)
		try:
			self.movedWorker = chosenNode.getState().getMovedWorker()
		except UnboundLocalError as e:
			print(Color.RED + repr(e.args) + Color.END)
			return

		# # Print tree
		print('-' * 100)
		print(repr(self.superRoot.getNwins()) + "/" + repr(self.superRoot.getNsim()))
		# self.printTree(self.superRoot)
		# # print('-' * 100)
		self.printTree(self.root)
		print('-' * 100)
		self.printLog(self.root)

		return chosenNode.getAction(), chosenNode.getData()

	def printTree(self, node, depth = 1):
		children = list(node.getChildren().keys())
		nChildren = len(children)
		try:
			print('\t' * (depth - 1) + '|---' + node.getState().getActivePlayer(), node.getAction(), repr(node.getNwins()) + "/" + repr(node.getNsim()))
			for i in range(0, nChildren):
				self.printTree(children[i], depth + 1)
		except Exception as e:
			print(e.args)
		return

	def printLog(self, node):
		parent = node.getParent()
		if(parent is None):
			depth = 1
		else:
			depth = self.printLog(parent)			
	
		print(' ' * (depth - 1) + node.getState().getActivePlayer(), node.getAction(), repr(node.getNwins()) + "/" + repr(node.getNsim()))
		return depth + 1

	def MCselection(self):
		"""Function to select the node for expansion using UCB1"""
		# Returns the unexplored leaf following the highest UCB1 values
		node = self.root
		while(node.hasChildren()):
			best = []
			bestValue = -np.inf

			children = node.getChildren()
			for n in children.keys():
				if(children[n] > bestValue):
					bestValue = children[n]
					best.clear()

				if(children[n] >= bestValue):
					best.append(n)
			
			node = random.choice(best)

			# node = max(node.getChildren(), key=node.getChildren().get)
		
		return node

	def MCexpansion(self, node):
		"""Expansion of the selected node through the available actions"""
		state = node.getState()
		# Placing workers will spawn (rows * columns - activeworkers) nodes
		placeable = state.getPlaceableWorkers(self.getNickname())
		if(placeable):
			id = placeable.pop()
			for i in range(0, 5):
				for j in range(0, 5):
					if(state.isEmpty(i, j)):
						physicalCoord = state.getPhysicalCoordinates({"row": i, "column": j})
						child = Node(node.getState().placeWorker(id, i, j), Actions.PLACE, 
								{"id": id, "row": physicalCoord['row'], "column": physicalCoord['column']})
						node.addChild(child)
			return

		# Checks for moving
		reachable = state.allReachableCells()
		if(len(reachable) > 0):
			for l in reachable:
				workerCoord = l[0]
				canReach = l[1]
				for coord in canReach:
					physicalSrc = state.getPhysicalCoordinates(workerCoord)
					physicalDst = state.getPhysicalCoordinates(coord)
					child = Node(node.getState().moveWorker(workerCoord['row'], workerCoord['column'], coord['row'], coord['column']),
							Actions.MOVE, {"src_row": physicalSrc['row'], "src_col": physicalSrc['column'], 
							"dst_row": physicalDst['row'], "dst_col": physicalDst['column']})
					node.addChild(child)
			return

		# checks for builds
		buildable = state.buildableCells()
		if(len(buildable) > 0):
			workerCoord = buildable[0][0]
			canBuild = buildable[0][1]
			for l in canBuild:
				coord = l[0]
				level = l[1][0]
				physicalSrc = state.getPhysicalCoordinates(workerCoord)
				physicalDst = state.getPhysicalCoordinates(coord)
				child = Node(node.getState().build(coord['row'], coord['column'], level), Actions.BUILD, 
						{"src_row": physicalSrc['row'], "src_col": physicalSrc['column'], 
						"dst_row": physicalDst['row'], "dst_col": physicalDst['column'], "level": level})
				node.addChild(child)
			return
		
		if(state.canPass()):
			node.addChild(Node(node.getState().passTurn(), Actions.PASS, None))

		return

	def SimToJit(self, node):
		board = self.getSimpleBoard(node.getState().getBoard())
		# print(repr(board))
		selfWorkers, opponentWorkers = self.getSimpleWorkers(node.getState().getWorkers())
		# print(repr(selfWorkers), repr(opponentWorkers))

		return jit_MCsimulation(board, selfWorkers, opponentWorkers)

	def getSimpleBoard(self, cellBoard):
		"""Creates a matrix of heights"""
		board = []
		for row in cellBoard:
			temp = []
			for cell in row:
				temp.append(cell.getTopLevel())
			board.append(np.array(temp))
		return np.array(board)

	def getSimpleWorkers(self, stateWorkers):
		"""Creates an array of workers where [[self.M, self.F], [opp.M, opp.F]], p.id=[x,y]"""
		selfWorkers = np.full((2, 2), -1)
		opponentWorkers = np.full((2, 2), -1)
		for owner in stateWorkers:
			for id in stateWorkers[owner]:
				if(id == 'M'):
					w = 0
				else:
					w = 1
				if(owner == self.nickname):
					selfWorkers[w, 0] = stateWorkers[owner][id]['row']
					selfWorkers[w, 1] = stateWorkers[owner][id]['column']
				else:
					opponentWorkers[w, 0] = stateWorkers[owner][id]['row']
					opponentWorkers[w, 1] = stateWorkers[owner][id]['column']

		return selfWorkers, opponentWorkers

	def MCsimulation(self, node):
		"""Roll-out phase through random agents"""
		score = 0
		# threadList = []
		# for i in range(0, N_THREADS):
		# 	score["Sim"+repr(i)+threadName] = 0

		# for i in range(0, N_THREADS):
		# 	t = Simulator(node, N_ROLLOUT_PER_THREAD, self.selfAgent, self.opponentAgent, name="Sim"+repr(i)+threadName)
		# 	threadList.append(t)
		# 	t.start()
		
		# for i in range(0, N_THREADS):
		# 	threadList[i].join()

		# print(threadName + repr(score))

		for i in range(0, N_ROLLOUT):
			print("Rollout", repr(i) + "/" + repr(N_ROLLOUT))
			state = copy.deepcopy(node.getState())
			activeAgent = self.selfAgent
			waitingAgent = self.opponentAgent

			while(state.goalTest() is None and not state.hasLost):
				activeAgent.setState(state)
				nick = activeAgent.getNickname()

				action, data = activeAgent.chooseAction(state.allReachableCells(), state.buildableCells(), 
					bool(state.getPlaceableWorkers(nick)), state.canPass())

				if(action == Actions.PLACE):
					state = state.placeWorker(data['id'], data['row'], data['column'])
				elif(action == Actions.MOVE):
					state = state.moveWorker(data['src_row'], data['src_col'], data['dst_row'], data['dst_col'])
				elif(action == Actions.BUILD):
					state = state.build(data['dst_row'], data['dst_col'], data['level'])
				elif(action == Actions.PASS):
					activeAgent, waitingAgent = waitingAgent, activeAgent
					state.newTurn(activeAgent.getNickname())
				elif(action == Actions.LOSE):
					state.hasLost = True

			# aiColor = Color.CYAN
			# oppColor = Color.RED
			# endColor = Color.END
			# for row in range(0, 5):
			# 	for col in range(0, 5):
			# 		cell = state.board[row][col]
			# 		owner = cell.getOwner()
					
			# 		if(owner == 'SantorinAI'):
			# 			print(aiColor, end = '')
			# 		elif(owner is not None):
			# 			print(oppColor, end = '')
			# 		print(repr(cell.getTopLevel()) + endColor + " ", end = '')
			# 	print()
			# print()
							
			if(state.goalTest() == self.selfAgent.getNickname()):
				score += 1

		return score

	def MCbackup(self, node, reward):
		"""Update of previous nodes"""
		node.acquire()
		node.nSimulations += N_ROLLOUT
		if(node.getState().getActivePlayer() == self.getNickname()):
			node.nWins += reward
		else:
			node.nWins += N_ROLLOUT - reward
		
		parent = node.getParent() 
		if(parent is not None):
			# Updates the score in the parent
			self.MCbackup(parent, reward)
			children = parent.getChildren()
			for child in children:
				children[child] = child.UCB1()
		
		node.release()
		return

@njit(parallel=True)
def jit_MCsimulation(board, selfWorkers, opponentWorkers):
	score = 0
	for i in np.arange(0, N_ROLLOUT):
		turn = 0 # active self player
		movedWorker = None
		hasBuilt = False
		hasPlaced = False
		hasLost = False

		currBoard = np.copy(board)
		currSelfWorkers = np.copy(selfWorkers)
		currOppWorkers = np.copy(opponentWorkers)
		activeWorkers = currSelfWorkers

		goOn = True
		while(goOn):
			# Check if has won
			for w in currSelfWorkers:
				if(currBoard[w[0]][w[1]] == 3):
					score += 1
					goOn = False
					break
			for w in currOppWorkers:
				if(currBoard[w[0]][w[1]] == 3):
					goOn = False
					break
			
			# When the player can't move
			if(hasLost):
				if(turn == 0):
					score += 1
				goOn = False
				break
			
			# Selects action

			# Place
			for coord in activeWorkers:
				if(coord[0] == -1):
					row = np.random.randint(0, 5)
					col = np.random.randint(0, 5)

					while(not jit_isEmpty(currBoard, currSelfWorkers, currOppWorkers, row, col)):
						row = np.random.randint(0, 5)
						col = np.random.randint(0, 5)
					
					coord[0] = row
					coord[1] = col
					hasPlaced = True
					break
					
			# Move
			if(not hasPlaced and movedWorker is None):
				candidate = np.random.randint(0, 2)
				reachable = jit_reachable(currBoard, currSelfWorkers, currOppWorkers, activeWorkers[candidate])
				if(reachable is None or reachable.size == 0):
					candidate = (candidate + 1) % 2
					reachable = jit_reachable(currBoard, currSelfWorkers, currOppWorkers, activeWorkers[candidate])
					# If no worker can move, the game is lost
					if(reachable is None or reachable.size == 0):
						hasLost = True
						continue
				
				dst = np.random.randint(0, reachable.shape[0])
								
				activeWorkers[candidate][0] = reachable[dst][0]
				activeWorkers[candidate][1] = reachable[dst][1]
				
				movedWorker = activeWorkers[candidate]
			elif(not hasPlaced and not hasBuilt):
				buildable = jit_buildable(currBoard, currSelfWorkers, currOppWorkers, movedWorker)
				# Cannot be empty (cell left from moving)
				dst = np.random.randint(0, buildable.shape[0])
				currBoard[buildable[dst][0]][buildable[dst][1]] += 1
				hasBuilt = True
			else:
				# Passing				
				turn = (turn + 1) % 2
				if(turn == 0):
					activeWorkers = currSelfWorkers
				else:
					activeWorkers = currOppWorkers

				movedWorker = None
				hasBuilt = False
				hasPlaced = False

		# print("----")
		# print(currBoard)
		# print(currSelfWorkers)
		# print(currOppWorkers)
		# print()
	return score

@njit
def jit_isEmpty(board, workers1, workers2, x, y):
	if(board[x][y] == 4):
		return False
	for w in workers1:
		if(w[0] == x and w[1] == y):
			return False
	for w in workers2:
		if(w[0] == x and w[1] == y):
			return False

	return True

@njit
def jit_reachable(board, workers1, workers2, src):
	reach = []
	src_row = src[0]
	src_col = src[1]
	for i in np.arange(src_row - 1, src_row + 2):
		if(i < 0 or i > 4):
			continue
		for j in np.arange(src_col - 1, src_col + 2):
			if(j < 0 or j > 4):
				continue
			if(jit_isEmpty(board, workers1, workers2, i, j) 
					and board[i][j] - board[src_row][src_col] < 2):
				reach.append([i, j])
	if(len(reach) > 0):
		return np.array(reach)
	return None

@njit
def jit_buildable(board, workers1, workers2, src):
	build = []
	src_row = src[0]
	src_col = src[1]

	for i in np.arange(src_row - 1, src_row + 2):
		if(i < 0 or i > 4):
			continue
		for j in np.arange(src_col - 1, src_col + 2):
			if(j < 0 or j > 4):
				continue
			if(jit_isEmpty(board, workers1, workers2, i, j)):
				build.append([i, j])

	return np.array(build)

class Node:
	"""Node for the tree"""
	def __init__(self, state, action = None, data = None):
		self.activePlayer = state.getActivePlayer()
		self.state = state

		self.lock = Lock()

		self.action = action
		self.data = data

		self.parent = None
		self.children = {}
		
		self.nWins = 0
		self.nSimulations = 0
		return

	def acquire(self):
		self.lock.acquire()
		return

	def release(self):
		self.lock.release()
		return

	def locked(self):
		return self.lock.locked()

	def getState(self):
		return self.state

	def getAction(self):
		return self.action

	def getData(self):
		return self.data

	def setParent(self, parent):
		self.parent = parent
		return

	def getParent(self):
		return self.parent

	def hasChildren(self):
		return bool(self.children)

	def addChild(self, node):
		node.setParent(self)
		self.children[node] = node.UCB1()
		return

	def getChildren(self):
		return self.children

	def setChildren(self, children):
		self.children = children
		return

	def getNwins(self):
		return self.nWins
	
	def getNsim(self):
		return self.nSimulations

	def UCB1(self): # might consider have log sum all parents if expanded
		if(self.nSimulations == 0):
			return np.inf
		
		return self.nWins / self.nSimulations + EXPLORATION * np.sqrt(np.log(self.parent.getNsim()) / self.nSimulations)

class MCThread(Thread):
	def __init__(self, ai, target = None, name = None):
		super(MCThread, self).__init__()
		self.target = target
		self.name = name
		self.ai = ai
		return

	def run(self):
		for i in range (0, N_ITERATIONS_PER_THREAD):
			print() 
			leaf = self.ai.MCselection()
			winner = leaf.getState().goalTest()
			if(winner is None):
				self.ai.MCexpansion(leaf)
				try:
					toExpand = random.choice(list(leaf.getChildren().keys()))
				except IndexError as e:
					print(Color.RED + repr(e.args) + Color.END)
					continue
				reward = self.ai.MCsimulation(toExpand, self.name)
			else:
				if(winner == self.ai.getNickname()):
					reward = N_ROLLOUT_PER_THREAD * N_THREADS
				else:
					reward = 0
			
			print(self.name, "Iteration", repr(i + 1) + "/" + repr(N_ITERATIONS_PER_THREAD) + ": ", repr(reward) + "/" + repr(N_ROLLOUT_PER_THREAD * N_THREADS))

			self.ai.MCbackup(leaf, reward)		
		return

class Simulator(Thread):
	def __init__(self, node, nRollout, agent, opponent, target = None, name = None):
		super(Simulator, self).__init__()
		self.target = target
		self.name = name
		self.node = node
		self.nRollout = nRollout
		self.selfAgent = copy.deepcopy(agent)
		self.opponentAgent = copy.deepcopy(opponent)

		return

	def run(self):
		global score
		state = self.node.getState()
		activeAgent = self.selfAgent
		waitingAgent = self.opponentAgent

		for i in range(0, int(N_ROLLOUT_PER_THREAD)):
			while(state.goalTest() is None and not state.hasLost):
				activeAgent.setState(state)
				nick = activeAgent.getNickname()

				# greedy = False
				# toDelete = []
				# ### Here a semi-random agent that chooses the terminal state
				reachable = state.allReachableCells()
				# if(len(reachable) > 0):
				# 	for l in reachable:
				# 		if(greedy):
				# 			break
				# 		src = l[0]
				# 		for dst in l[1]:
				# 			test = state.moveWorker(src['row'], src['column'], dst['row'], dst['column'])
				# 			winner = test.goalTest()
				# 			if(winner == activeAgent.getNickname()):
				# 				state = test
				# 				greedy = True
				# 				break
				# 			elif(winner == waitingAgent.getNickname()):
				# 				toDelete.append(l)
				# 				break
				# 	if(greedy):
				# 		continue
				# 	while(len(toDelete) > 0):
				# 		toDel = toDelete.pop()
				# 		reachable.remove(toDel) 

				action, data = activeAgent.chooseAction(reachable, state.buildableCells(), 
					bool(state.getPlaceableWorkers(nick)), state.canPass())
				
				if(action == Actions.PLACE):
					state = state.placeWorker(data['id'], data['row'], data['column'])
				elif(action == Actions.MOVE):
					state = state.moveWorker(data['src_row'], data['src_col'], data['dst_row'], data['dst_col'])
				elif(action == Actions.BUILD):
					state = state.build(data['dst_row'], data['dst_col'], data['level'])
				elif(action == Actions.PASS):
					activeAgent, waitingAgent = waitingAgent, activeAgent
					state.newTurn(activeAgent.getNickname())
				elif(action == Actions.LOSE):
					state.hasLost = True

				# for row in range(0, 5):
				# 	for col in range(0, 5):
				# 		cell = state.board[row][col]
				# 		owner = cell.getOwner()
						
				# 		if(owner is not None):
				# 			print(aiColor, end = '')
				# 		print(repr(cell.getTopLevel()) + endColor + " ", end = '')
				# 	print()

				# state.getBoard().printBoard()

			if(state.goalTest() == self.selfAgent.getNickname()):
				# self.scoreLock.acquire()
				try:
					score[self.name] += 1
				except:
					score[self.name] = 1
				# self.scoreLock.release()
		return

