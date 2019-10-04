#!/usr/bin/env python

import unittest
import b2btest
import datetime
import os

class B2BTest_Test(unittest.TestCase):
	def setUp(self):
		self.toDelete=[]
		self.b2bdatapath='b2bdata'
		self.acceptMode=False
		del self.acceptMode
		try: os.makedirs(self.b2bdatapath)
		except OSError: pass
		for f in os.listdir(self.b2bdatapath):
			os.unlink(os.path.join(self.b2bdatapath, f))

	def tearDown(self):
		for f in self.toDelete:
			try: os.unlink(f)
			except: pass
		self.assertEqual(os.listdir(self.b2bdatapath), [])
		for f in os.listdir(self.b2bdatapath):
			os.unlink(os.path.join(self.b2bdatapath, f))

	def deleteLater(self, filename):
		self.toDelete.append(filename)

	def read(self, filename):
		with open(filename) as f:
			return f.read()

	def write(self, filename, content):
		with open(filename,'w') as f:
			f.write(content)

	def setResult(self, content):
		self.write(self.resultFile(), content)

	def setExpected(self, content):
		self.write(self.expectedFile(), content)

	def resultFile(self):
		return os.path.join(self.b2bdatapath,self.id()+'-result')

	def expectedFile(self):
		return os.path.join(self.b2bdatapath,self.id()+'-expected')

	def assertExpectedEquals(self, expectation):
		self.deleteLater(self.expectedFile())
		self.assertEqual(self.read(self.expectedFile()), expectation)

	def assertResultEquals(self, result):
		self.deleteLater(self.resultFile())
		self.assertEqual(self.read(self.resultFile()), result)

	def test_assertB2BEqual_whenNoExpectation_generatesResultsAndFails(self):

		with self.assertRaises(AssertionError) as ass:
			self.assertB2BEqual('data')

		self.assertEqual(ass.exception.args[0],
			"No expectation found, please, check and accept '{}'"
			.format(self.resultFile()))
 
		self.assertResultEquals('data')

	def test_accepting_withNoExpectation_generatesItAndClearsResults(self):
		self.acceptMode=True
		self.setResult('data')

		with self.assertRaises(Warning) as ass:
			self.assertB2BEqual('data')
		self.assertEqual(ass.exception.args[0],
			"Accepting new data for '{}'".format(self.expectedFile()))

		self.assertExpectedEquals('data')

	def test_assertB2BEqual_differentResult_generatesExpectationAndFails_hitravis(self):
		self.setExpected('data')
		with self.assertRaises(AssertionError) as ass:
			self.assertB2BEqual('differentData')

		self.assertEqual(ass.exception.args[0],
			"Differing content: '{}'".format(self.resultFile())
			)

		self.assertExpectedEquals('data')
		self.assertResultEquals('differentData')

	def test_assertB2BEqual_matchingClearsAnyFormerResult(self):
		self.setExpected('data')
		self.setResult('bad data')
		self.assertB2BEqual('data')

		self.assertExpectedEquals('data')

	def test_accepting_differentResult_generatesExpectationAndFails(self):
		self.setExpected('data')
		self.setResult('previous data')
		self.acceptMode = True

		with self.assertRaises(Warning) as ass:
			self.assertB2BEqual('differentData')
		self.assertEqual(ass.exception.args[0],
			"Accepting new data for '{}'".format(self.expectedFile()))

		self.assertExpectedEquals('differentData')

class ProgramB2B_Test(unittest.TestCase):
	def test_noOutput_whenFails(self):
		with self.assertRaises(AssertionError) as ass:
			self.assertCommandB2BEqual(
				"false",
			)
		self.assertMultiLineEqual(ass.exception.args[0],
			"Command failed with return code 1:\n"
			"'false'")

	def test_noOutput_whenSucceds(self):
		self.assertCommandB2BEqual(
			"true",
		)

	def test_noOutput_whenBadCommand(self):
		with self.assertRaises(AssertionError) as ass:
			self.assertCommandB2BEqual(
				"badCommand",
			)
		self.assertEqual(ass.exception.args[0],
			"Command failed with return code 127:\n"
			"'badCommand'")

	def test_singleOutput(self):
		# TODO: in progress
		self.assertCommandB2BEqual(
			"echo data > output",
			"output",
			)



unittest.TestCase.__str__ = unittest.TestCase.id


if __name__ == '__main__':
	unittest.main()

#vim: noet sw=4 ts=4
