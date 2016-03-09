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
		for f in os.listdir(self.b2bdatapath):
			os.unlink(os.path.join(self.b2bdatapath, f))

	def deleteLater(self, filename):
		self.toDelete.append(filename)

	def tearDown(self):
		for f in self.toDelete:
			try: os.unlink(f)
			except: pass
		self.assertEqual(os.listdir(self.b2bdatapath), [])
		for f in os.listdir(self.b2bdatapath):
			os.unlink(os.path.join(self.b2bdatapath, f))

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

	def test_assertB2BEqual_whenNoExpectation_generatesResultsAndFails(self):

		with self.assertRaises(AssertionError) as ass:
			self.assertB2BEqual('data')

		self.assertEqual(ass.exception.args[0],
			"No expectation found, please, check and accept '{}'"
			.format(self.resultFile()))
 
		self.assertEqual(self.read(self.resultFile()), 'data')
		self.deleteLater(self.resultFile())

	def test_accepting_withNoExpectation_generatesItAndClearsResults(self):
		self.acceptMode=True
		self.setResult('data')

		self.assertB2BEqual('data')

		self.assertEqual(self.read(self.expectedFile()), 'data')
		self.deleteLater(self.expectedFile())

	def test_assertB2BEqual_differentResult_generatesExpectationAndFails(self):
		self.setExpected('data')
		with self.assertRaises(AssertionError) as ass:
			self.assertB2BEqual('differentData')

		self.assertEqual(ass.exception.args[0],
			"'differentData' != 'data'\n"
			"- differentData\n"
			"+ data\n"
			"")

		self.deleteLater(self.expectedFile())
		self.assertEqual(self.read(self.expectedFile()), 'data')
		self.deleteLater(self.resultFile())
		self.assertEqual(self.read(self.resultFile()), 'differentData')

	def test_assertB2BEqual_matchingClearsAnyFormerResult(self):
		self.setExpected('data')
		self.setResult('bad data')
		self.assertB2BEqual('data')

		self.deleteLater(self.expectedFile())
		self.assertEqual(self.read(self.expectedFile()), 'data')

	def test_accepting_differentResult_generatesExpectationAndFails(self):
		self.setExpected('data')
		self.setResult('previous data')
		self.acceptMode = True

		with self.assertRaises(Warning) as ass:
			self.assertB2BEqual('differentData')
		self.assertEqual(ass.exception.args[0],
			"Accepting new data for '{}'".format(self.expectedFile()))

		self.deleteLater(self.expectedFile())
		self.assertEqual(self.read(self.expectedFile()), 'differentData')


unittest.TestCase.__str__ = unittest.TestCase.id


if __name__ == '__main__':
	unittest.main()

#vim: noet sw=4 ts=4
