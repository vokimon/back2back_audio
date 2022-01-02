from b2btest import runBack2BackProgram
import sys

datapath = "data" # Point it to the directory containing your reference data

runBack2BackProgram(datapath, sys.argv, [
	('Generate1KHzSine',
		'sox -n sine.wav synth 1.0 sine  1000.0', [
			'sine.wav',
		]),

])


