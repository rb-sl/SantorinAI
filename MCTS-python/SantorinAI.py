#!/usr/bin/env python3

# Infrastructure for AIs playing the Santorini game
from ai_monteCarlo import monteCarloAI
import socket
import threading
import time
import queue
import logging
import json
import re

import game_model
from ai_random import randomAI
from class_support import Color, Actions

# Name taken by the agent during the game
NICKNAME = "SantorinAI"

# Agent object
ai = randomAI(NICKNAME)
# ai = monteCarloAI(NICKNAME)

# Information displaying
# logging.basicConfig(level = logging.DEBUG, format = '(%(threadName)-9s) %(message)s')

# Socket definition
HOST = "192.168.1.101"
# HOST = "127.0.0.1"
PORT = 49153
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)

# Game model
model = None

# Flag to signal the ending game
endGame = False

# Regex used to clean json before and after the object
regex_clean = re.compile(r'^.*?\{\"|\}[^}]*?$', re.DOTALL) 
# Regex used to split messages in case they contains multiple
# objects and remove internal noise
regex_split = re.compile(r'\}[^\{\},]+?\{\"', re.DOTALL)
	
# ----------------------------------------
# Messages
# Broken to allow the insert of parameters
# ----------------------------------------

# Ping
pingMessage = '{"type":"PING","message":"{\\"message\\":\\"AIping\\"}"}'

# Game initialization or join (if a game already exists)
initMessageA = '{"type":"REGISTER","message":"{\\"nickname\\":\\"' + NICKNAME + '\\",\\"nPlayers\\":2,\\"gods\\":false}"}'
initMessageB = '{"type":"REGISTER","message":"{\\"nickname\\":\\"' + NICKNAME + '\\"}"}'

# Choice of the starter player
starterMessage_1 = '{"type":"CHOSESTARTER","message":"{\\"player\\":\\"' + NICKNAME + '\\",\\"starter\\":\\"'
starterMessage_2 = '\\"}"}'

# Choice of placement of a worker
workerInitMessage_1 = '{"type":"WORKERINIT","message":"{\\"player\\":\\"' + NICKNAME + '\\",\\"coordinates\\":{\\"row\\":'
workerInitMessage_2 = ',\\"column\\":'
workerInitMessage_3 = '},\\"sex\\":\\"'
workerInitMessage_4 = '\\"}"}'

# Movement of worker
moveMessage_1 = '{"type":"MOVE","message":"{\\"source\\":{\\"row\\":'
moveMessage_2 = ',\\"column\\":'
moveMessage_3 = '},\\"destination\\":{\\"row\\":'
moveMessage_4 = ',\\"column\\":'
moveMessage_5 = '},\\"player\\":\\"' + NICKNAME + '\\"}"}'

# Build of a level
buildMessage_1 = '{"type":"BUILD","message":"{\\"source\\":{\\"row\\":'
buildMessage_2 = ',\\"column\\":'
buildMessage_3 = '},\\"destination\\":{\\"row\\":'
buildMessage_4 = ',\\"column\\":'
buildMessage_5 = '},\\"level\\":'
buildMessage_6 = ',\\"player\\":\\"' + NICKNAME + '\\"}"}'

# Turn pass
passMessage = '{"type":"PASS","message":"{\\"player\\":\\"' + NICKNAME + '\\"}"}'

# Game lost
loseMessage = '{"type":"LOSE","message":"{\\"player\\":\\"' + NICKNAME + '\\"}"}'

# Buffer for messages
messageQ = queue.Queue()

# Keeps the serverState if needed
lastServerState = None

# ----------------------------------------
# Threads and communication
# ----------------------------------------

def delay(sec = 1):
	"""Delay function to avoid saturating the server"""
	time.sleep(sec)

# Variable used to keep threads going
keepAlive = True

def sendData(message):
	"""Function to send a message over the socket"""
	s.sendall((message + '\n').encode())   
	if(message != pingMessage):
		logging.debug("Sent: " + message)

class Pinger(threading.Thread):
	"""Heartbeat thread to keep the connection active"""
	def __init__(self, target = None, name = None):
		super(Pinger, self).__init__()
		self.target = target
		self.name = name

	def run(self):
		global keepAlive

		while keepAlive:
			# Disconnection handling
			try:
				sendData(pingMessage)
			except:
				print(Color.RED + "(" + self.name + ") Server connection interrupted. Terminating." + Color.END)
				keepAlive = False
				return
			time.sleep(0.5)

		print(Color.GREEN + "(" + self.name + ") Stopped correctly." + Color.END)
		return

class MessageProducer(threading.Thread):
	"""Thread to read messages from network"""
	def __init__(self, target = None, name = None):
		super(MessageProducer, self).__init__()
		self.target = target
		self.name = name

	def run(self):
		global keepAlive
		global endGame

		while keepAlive:
			# Disconnection handling
			try:
				data = s.recv(1024)
			except:
				print(Color.RED + "(" + self.name + ") Server connection interrupted. Terminating." + Color.END)
				keepAlive = False
				return

			if(data):
				decoded = data.decode("utf8", "ignore")
				# Removes noise on start and end of message (and also brackets)
				cleaned = regex_clean.sub('', decoded)
				# Splits multiple messages by removing internal noise
				messages = regex_split.split(cleaned)
				
				try:
					for msg in messages:
						envelope = json.loads('{"' + msg + '}')
						
						# Sends messages to consumer
						if(envelope["type"] != "PING"):
							if(envelope["type"] == "ENDGAME"):
								endGame = True
							messageQ.put(envelope)
							logging.debug("Received " + envelope['type'])
				except Exception as e:
					if(decoded != 'y'):
						logging.debug(repr(e) + "\n>> " + repr(decoded) + "\n>> " + repr(messages))

		print(Color.GREEN + "(" + self.name + ") Stopped correctly." + Color.END)
		return

class MessageConsumer(threading.Thread):
	"""Thread to read enqueued messages and route them to the correct handler"""
	def __init__(self, target = None, name = None):
		super(MessageConsumer, self).__init__()
		self.target = target
		self.name = name
		return

	def run(self):
		global keepAlive
		global NICKNAME

		while keepAlive:
			# Blocking read
			try:
				envelope = messageQ.get(True, 5)
			except:
				continue

			type = envelope['type']
			message = json.loads(envelope['message'])
			logging.debug("Processing message: " + type + " >> " + repr(message))

			# Routes messages to their functions
			if(type == "SERVERSTATE"):
				keepAlive = startGame(message)
			elif(type == "INFO"):
				print(Color.RED + NICKNAME + " is already playing. Terminating." + Color.END)
				keepAlive = False
			elif(type == "PLAYERSMESSAGE"):
				keepAlive = handlePlayersMessage(message)
			elif(type == "UPDATE"):
				handleUpdate(message)
			elif(type == "ENDGAME"):
				endgame(message)
		
		print(Color.GREEN + "(" + self.name + ") Stopped correctly." + Color.END)
		return

def startGame(message):
	"""Function to create a new game or join an existing one"""
	global lastServerState
	global endGame 
	endGame = False

	if(not message['open'] and message['active']):
		print(Color.RED + "Game not available. Terminating." + Color.END)
		return False
	
	lastServerState = message

	delay()
	if(not message['active']):
		sendData(initMessageA)
		print(Color.CYAN + "Game created, waiting for another player..." + Color.END)
	else:
		sendData(initMessageB)
		print(Color.CYAN + "Joining game..." + Color.END)

	return True

def handlePlayersMessage(message):
	"""Function to start a game and choose the starter"""
	global model

	print("Players: " + repr(message['players']) + " Challenger: " + message['player'])

	# Model creation
	try:
		model = game_model.Model(NICKNAME, message['players'])
		ai.createState(model)
	except ValueError as e:
		print(Color.RED + e.args[0] + "\nUnable to create model. Terminating" + Color.END)
		return False
	print("Local model of the game created.")

	# Challenger actions
	if(message['player'] == NICKNAME):
		starter = ai.chooseStarter()
		print("Chosen starter player: "  + starter)
		delay()
		sendData(starterMessage_1 + starter + starterMessage_2)        
	else:
		print("Waiting for challenger to choose the starter...")

	return True

def handleUpdate(message):
	"""Function to update the internal model and choose an action"""
	global model
	global endGame

	# Board update
	model.update(message['boardUpdate'], message['player'])
	ai.updateState(model)
	model.printBoard()

	if(message['player'] != NICKNAME):
		print("Waiting for turn...")
		return

	# Action
	action, data = ai.chooseAction(message['reachableCells'], message['buildableCells'], 
			message['canPlaceWorker'], message['canPass'])

	print("Chosen action: " + action + " => " + repr(data))

	delay()
	if(endGame):
		return

	if(action == Actions.PLACE):
		sendData(workerInitMessage_1 + repr(data['row']) + workerInitMessage_2 
				+ repr(data['column']) + workerInitMessage_3 + data['id'] + workerInitMessage_4)
	elif(action == Actions.MOVE):
		sendData(moveMessage_1 + repr(data['src_row']) + moveMessage_2 + repr(data['src_col']) 
				+ moveMessage_3 + repr(data['dst_row']) + moveMessage_4 + repr(data['dst_col']) + moveMessage_5)
	elif(action == Actions.BUILD):
		sendData(buildMessage_1 + repr(data['src_row']) + buildMessage_2 + repr(data['src_col']) 
				+ buildMessage_3 + repr(data['dst_row']) + buildMessage_4 + repr(data['dst_col']) 
				+ buildMessage_5 + repr(data['level']) + buildMessage_6)
	elif(action == Actions.PASS):
		sendData(passMessage)
	elif(action == Actions.LOSE):
		sendData(loseMessage)
		endgame()
	return

def endgame(message = None):
	"""Function handling the end game messages, stops the execution"""
	global model
	global keepAlive

	model = None
	if(message is not None):
		if(not message['isWinner']):
			print(Color.CYAN + "Game terminated due to " + message['player'] + "'s disconnection." + Color.END)
		else:
			print(Color.CYAN + "Game terminated; winner: " + message['player'] + "." + Color.END)
		print("\n\n\n")
	else:
		print(Color.CYAN + "Unable to move: game terminated." + Color.END)
		keepAlive = False

	return

# ------------------
# Main
# ------------------

print(Color.GREEN + NICKNAME + " started." + Color.END)

print("Connecting to server at " + HOST + ":" + repr(PORT) + "...")
try:
	s.connect((HOST, PORT))
except:
	print(Color.RED + "Server at " + HOST + ":" + repr(PORT) + " unavailable. Terminating." + Color.END)
	exit(0)

# Starts threads
producer = MessageProducer(name = "MessageProducer")
producer.start()

pinger = Pinger(name = "Pinger")
pinger.start()

consumer = MessageConsumer(name = "MessageConsumer")
consumer.start()

# Waits for threads' termination and exits
producer.join()
consumer.join()
pinger.join()

s.close()
exit(0)
