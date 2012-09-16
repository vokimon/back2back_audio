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

	import sys
	if '--test' not in sys.argv :
		diffs = differences(*sys.argv[1:])
		if not diffs : print "Ok"; sys.exit(0)
		for d in diffs :
			print >> sys.stderr, d

		sys.exit(-1)

	sys.argv.remove('--test')
	import unittest
	import numpy as np
	from numpy.testing import assert_equal as np_assert_equal

	class MultiChannelDiffTests(unittest.TestCase) :
		def test_hopMax(self) :
			a1 = np.array([
				[ 1, 1],
				[10, 1],
				[ 1, 1],
				[ 1,30],
				[ 1, 1],
				])
			max, maxarg = hopMax(a1)
			np_assert_equal( max, np.array([10.,30.]) )
			np_assert_equal( maxarg, np.array([1,3]) )

		def test_hopMax_withOffset(self) :
			a1 = np.array([
				[ 1, 1],
				[10, 1],
				[ 1, 1],
				[ 1,30],
				[ 1, 1],
				])
			max, maxarg = hopMax(a1, 100)
			np_assert_equal( max, np.array([10.,30.]) )
			np_assert_equal( maxarg, np.array([101,103]) )

		def test_hopMax_negative(self) :
			a1 = np.array([
				[  1, 1],
				[-10, 1],
				[  1, 1],
				[  1,30],
				[  1, 1],
				])
			max, maxarg = hopMax(a1)
			np_assert_equal( max, np.array([10.,30.]) )
			np_assert_equal( maxarg, np.array([1,3]) )

		def test_hopMax_nan(self) :
			nan=np.NaN
			a1 = np.array([
				[  1, 1],
				[nan, 1],
				[  1, 1],
				[  1,30],
				[  1, 1],
				])
			max, maxarg = hopMax(a1)
			np_assert_equal( max, np.array([nan,30.]) )
			np_assert_equal( maxarg, np.array([1,3]) )

		def test_hopMax_inf(self) :
			inf=np.inf
			a1 = np.array([
				[  1, 1],
				[-inf, 1],
				[  1, 1],
				[  1,30],
				[  1, 1],
				[  1, 1],
				])
			max, maxarg = hopMax(a1)
			np_assert_equal( max, np.array([inf,30.]) )
			np_assert_equal( maxarg, np.array([1,3]) )

		def test_hopMax_boolean(self) :
			a1 = np.array([
				[ False, False],
				[  True, False],
				[ False, False],
				[ False, False],
				[ False, False],
				])
			max, maxarg = hopMax(a1)
			np_assert_equal( max, np.array([True,False]) )
			np_assert_equal( maxarg, np.array([1,0]) )

		def test_joinHopMax_initial(self) :
			np_assert_equal( mergeHopMax(
				np.array([ 0., 0.]), np.array([ None, None]),
				np.array([ 3., 7.]), np.array([10,20]),
				),(
				np.array([ 3., 7.]), np.array([10,20]),
				))

		def test_joinHopMax(self) :
			np_assert_equal( mergeHopMax(
				np.array([ 5., 5.]), np.array([ 1, 2]),
				np.array([ 3., 7.]), np.array([10,20]),
				),(
				np.array([ 5., 7.]), np.array([ 1,20]),
				))

		def test_joinHopMax_nan(self) :
			nan = np.NaN
			np_assert_equal( mergeHopMax(
				np.array([ 5., 5.]), np.array([ 1, 2]),
				np.array([ 3., nan]), np.array([10,20]),
				),(
				np.array([ 5., 5.]), np.array([ 1,2]),
				))

		def test_joinHopMax_nan_after(self) :
			nan = np.NaN
			np_assert_equal( mergeHopMax(
				np.array([ 3., nan]), np.array([1,2]),
				np.array([ 5., 5.]), np.array([ 10, 20]),
				),(
				np.array([ 5., nan]), np.array([10,2]),
				))

		def test_joinHopMax_isInPlace(self) :
			old, oldPos = np.array([ 5., 5.]), np.array([ 1, 2]),
			new, newPos = np.array([ 3., 7.]), np.array([10,20]),
			mergeHopMax(old, oldPos, new, newPos)
			np_assert_equal(
				(old, oldPos),(
				np.array([ 5., 7.]), np.array([ 1,20]),
				))





		def savewav(self, data, filename, samplerate) :
			import os
			assert not os.access(filename, os.F_OK), "Test temporary file already existed: %s"%filename
			import sndfile
			with sndfile.WaveWriter(
					filename,
					samplerate=samplerate,
					channels=data.shape[1]
					) as writer :
				writer.write(data.ravel("C").reshape(data.shape))
			self.filestoremove.append(filename)

		def setUp(self) :
			self.filestoremove = []

		def tearDown(self) :
			import os
			for file in self.filestoremove :
				if os.access(file, os.F_OK) :
					os.remove(file)

		def display(self, file) :
			import os
			os.system("sweep '%s'"%file)

		def sinusoid(self, samples=400, f=440, samplerate=44100) :
			return np.sin( np.linspace(0, 2*np.pi*f*samples/samplerate, samples))[:,np.newaxis]

		def channels(self, *args) :
			return np.concatenate(args, axis=1)

		def stereoSinusoids(self, samples=400) :
			return self.channels(
				self.sinusoid(samples, 440),
				self.sinusoid(samples, 880),
				)

		# Structural difference

		def test_comparewaves_differentChannels(self) :
			data = self.stereoSinusoids()

			self.savewav(data[:,0:1],  "data1.wav", 44100)
			self.savewav(data,         "data2.wav", 44100)
			self.assertEquals([
				'Expected channels was 1 but got 2',
				], differences("data1.wav", "data2.wav"))

		def test_comparewaves_differentSampleRate(self) :
			data = self.stereoSinusoids()

			self.savewav(data, "data1.wav", 44100)
			self.savewav(data, "data2.wav", 48000)
			self.assertEquals([
				'Expected samplerate was 44100 but got 48000',
				], differences("data1.wav", "data2.wav"))

		def test_comparewaves_differentLenght(self) :
			data = self.sinusoid(400, 440, 44100)

			self.savewav(data,       "data1.wav", 44100)
			self.savewav(data[:200], "data2.wav", 44100)
			self.assertEquals([
				'Expected frames was 400 but got 200',
				], differences("data1.wav", "data2.wav"))

		# Helper assert for non-structural differences tests

		def assertReportEqual(self, data1, data2, expectedMessages) :
			self.savewav(data1, "data1.wav", 44100)
			self.savewav(data2, "data2.wav", 44100)
			self.assertEquals(expectedMessages,
				differences("data1.wav", "data2.wav"))

		# No differences

		def test_comparewaves_identicalMono(self) :
			data = self.sinusoid(1024, 440, 44100)

			self.assertReportEqual(data, data, [])

		def test_comparewaves_notAFullHop(self) :
			data = self.sinusoid(400, 440, 44100)

			self.assertReportEqual(data, data, [])

		def test_comparewaves_identicalStereo(self) :
			data = self.stereoSinusoids()

			self.assertReportEqual(data, data, [])

		def test_comparewaves_diferentValues(self) :
			data1 = self.stereoSinusoids()
			data2 = data1.copy()
			data2[50,1] = 0

			self.assertReportEqual(data1, data2, [
				"Value missmatch at channel 1, maximum difference of 0.001464 at sample 50",
				])

		def test_comparewaves_diferentValuesNextHops(self) :
			data1 = self.stereoSinusoids(samples=2000)
			data2 = data1.copy()
			data2[1025,1] = 0

			self.assertReportEqual(data1, data2, [
				"Value missmatch at channel 1, maximum difference of 0.225822 at sample 1025",
				])

		def test_comparewaves_missingNaN(self) :
			data1 = self.stereoSinusoids()
			data2 = data1.copy()
			data1[50,1] = np.NaN

			self.assertReportEqual(data1, data2, [
				"Nan missmatch at channel 1, first at sample 50",
				])

		def test_comparewaves_expectedNaN(self) :
			data1 = self.stereoSinusoids()
			data2 = data1.copy()
			data1[50,1] = np.NaN
			data2[50,1] = np.NaN

			self.assertReportEqual(data1, data2, [
				])

		def test_comparewaves_unexpectedNaN(self) :
			# TODO: Should the missingNaN and unexpectedNaN have different messages?
			data1 = self.stereoSinusoids()
			data2 = data1.copy()
			data2[50,1] = np.NaN

			self.assertReportEqual(data1, data2, [
				"Nan missmatch at channel 1, first at sample 50",
				])

		def test_comparewaves_missingNaNNextHops(self) :
			data1 = self.stereoSinusoids(samples=2000)
			data2 = data1.copy()
			data1[1025,1] = np.NaN

			self.assertReportEqual(data1, data2, [
				"Nan missmatch at channel 1, first at sample 1025",
				])

		def test_comparewaves_expectedPosInf(self) :
			data1 = self.stereoSinusoids()
			data2 = data1.copy()
			data1[50,1] = np.inf
			data2[50,1] = np.inf

			self.assertReportEqual(data1, data2, [])

		def test_comparewaves_missingPosInf(self) :
			data1 = self.stereoSinusoids()
			data2 = data1.copy()
			data1[50,1] = np.inf

			self.assertReportEqual(data1, data2, [
				"Positive infinite missmatch at channel 1, first at sample 50",
				])

		def test_comparewaves_unexpectedPosInf(self) :
			# TODO: Should the missingPostInf and unexpectedPosInf have different messages?
			data1 = self.stereoSinusoids()
			data2 = data1.copy()
			data2[50,1] = np.inf

			self.assertReportEqual(data1, data2, [
				"Positive infinite missmatch at channel 1, first at sample 50",
				])

		def test_comparewaves_expectedNegInf(self) :
			data1 = self.stereoSinusoids()
			data2 = data1.copy()
			data1[50,1] = -np.inf
			data2[50,1] = -np.inf

			self.assertReportEqual(data1, data2, [])

		def test_comparewaves_missingNegInf(self) :
			data1 = self.stereoSinusoids()
			data2 = data1.copy()
			data1[50,1] = -np.inf

			self.assertReportEqual(data1, data2, [
				"Negative infinite missmatch at channel 1, first at sample 50",
				])

		def test_comparewaves_unexpectedNegInf(self) :
			# TODO: Should the missingNegtInf and unexpectedNegInf have different messages?
			data1 = self.stereoSinusoids()
			data2 = data1.copy()
			data2[50,1] = -np.inf

			self.assertReportEqual(data1, data2, [
				"Negative infinite missmatch at channel 1, first at sample 50",
				])

	sys.exit(unittest.main())



