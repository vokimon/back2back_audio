#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Copyright 2012 David García Garzón

This file is part of spherelab

spherelab is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

spherelab is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


extensions = [
	'wav',
	'ogg',
	'flac',
	'voc',
	'au',
]

def differences(expected, result) :
	import sndfile
	import numpy as np

	errors = []
	with sndfile.WaveReader(expected) as expectedReader :
		with sndfile.WaveReader(result) as resultReader :
			for attribute in [
				'samplerate',
				'channels',
				'frames',
				] :
				expectedAttribute = getattr(expectedReader, attribute)
				resultAttribute = getattr(resultReader, attribute)
				if expectedAttribute != resultAttribute :
					errors.append("Expected %s was %s but got %s"%(
						attribute,
						expectedAttribute,
						resultAttribute,
						))
			# Errors detected so far avoid further comparison
			if errors : return errors

			hopsize = 1024
			period = 0
			resultData = np.empty((hopsize, resultReader.channels), np.float64)
			expectedData = np.empty((hopsize, expectedReader.channels), np.float64)

			channels = expectedReader.channels

			maxdiff      = np.zeros((channels))
			maxdiffpos   = np.array([None]*channels)
			nanmiss      = np.array([False]*channels)
			nanmisspos   = np.array([None]*channels)
			pinfmiss     = np.array([False]*channels)
			pinfmisspos  = np.array([None]*channels)
			ninfmiss     = np.array([False]*channels)
			ninfmisspos  = np.array([None]*channels)
			while True :
				actualResultHop = resultReader.read(resultData)
				actualExpectedHop = expectedReader.read(expectedData)
				assert actualExpectedHop == actualExpectedHop, "Unexpected unbalanced hop in file readers"
				if actualExpectedHop == 0 : break # al file read

				resultData = resultData[:actualResultHop]
				expectedData = expectedData[:actualResultHop]

				def check(expected, result, predicate, misses, missesPos) :
					found_expected = predicate(expectedData)
					found_result   = predicate(resultData)
					currentMisses  = (found_expected != found_result)
					if currentMisses.any() :
						cummulativeCompare(misses, missesPos, currentMisses, period*hopsize)
						# remove conflictive values
						conflictive = found_result | found_expected
						resultData[conflictive] = 0
						expectedData[conflictive] = 0

				check(expectedData, resultData, np.isnan, nanmiss, nanmisspos)
				check(expectedData, resultData, np.isposinf, pinfmiss, pinfmisspos)
				check(expectedData, resultData, np.isneginf, ninfmiss, ninfmisspos)

				diffData = resultData - expectedData
				cummulativeCompare(maxdiff, maxdiffpos, diffData, period*hopsize)

				period += 1

			errors += [
				"Value missmatch at channel %i, maximum difference of %f at sample %i" %
					( channel, value, sample )
					for channel, (value, sample)
					in enumerate(zip(maxdiff, maxdiffpos))
					if value > 1e-15
					] + [
				"Nan missmatch at channel %i, first at sample %i" %
					( channel, sample )
					for channel, (value, sample)
					in enumerate(zip(nanmiss, nanmisspos))
					if value
					] + [
				"Positive infinite missmatch at channel %i, first at sample %i" %
					( channel, sample )
					for channel, (value, sample)
					in enumerate(zip(pinfmiss, pinfmisspos))
					if value
					] + [
				"Negative infinite missmatch at channel %i, first at sample %i" %
					( channel, sample )
					for channel, (value, sample)
					in enumerate(zip(ninfmiss, ninfmisspos))
					if value
					]

			return errors

def hopMax(channels, offset=0) :
	abschannels = abs(channels)
	return (
		abschannels.max(axis=0),
		abschannels.argmax(axis=0)+offset,
		)

def mergeHopMax(old, oldpos, new, newpos) :
	choser = old < new
	old[choser] = new[choser]
	oldpos[choser] = newpos[choser]
	return (old, oldpos)

def cummulativeCompare(values, pos, diff, offset) :
	newvalues, newpos = hopMax(diff, offset)
	values, pos = mergeHopMax(values, pos, newvalues, newpos)
	return values, pos


if __name__ == '__main__' :

	diffs = differences(*sys.argv[1:])
	if not diffs : print "Ok"; sys.exit(0)
	for d in diffs :
		print >> sys.stderr, d

	sys.exit(-1)



