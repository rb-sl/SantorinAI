#!/usr/bin/env python3

# Classes to be used across files

from enum import Enum

# Colors for output
class Color():
	CYAN = '\033[96m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	END = '\033[0m'

# Agent actions
class Actions():		
	PLACE = "Place worker"
	MOVE = "Move"
	BUILD = "Build"
	PASS = "Pass"
	LOSE = "Lose"
