import os, sys, string
import subprocess
from consolemsg import step, fail, success, error, warn, printStdError, color

def printcolor(colorcode, message):
	printStdError(color(colorcode, message))

from . import diffaudio
from . import difftext
diff_for_type = {
	".wav" : diffaudio.differences,
	".txt" : difftext.differences,
	".clamnetwork" : difftext.differences,
	".xml" : difftext.differences,
	".ttl" : difftext.differences,
}

try:
    FileNotFoundError
except NameError:
    FileNotFoundError=IOError


def diff_files(expected, result, diffbase) :
	if not os.access(result, os.R_OK):
		error("Result file not found: {}".format(result))
		return ["Result was not generated: '%s'"%result]
	if not os.access(expected, os.R_OK):
		error("Expectation file not found for: {}".format(result))
		return ["No expectation for the output. First run? Check the results and accept them with the --accept option."]
	extension = os.path.splitext(result)[-1]

	diff = diff_for_type.get(extension, difftext.differences)
	return diff(expected, result, diffbase)


def archSuffix() :
	return os.popen('uname -m').read().strip()

def expectedArchName(base, extension='.wav') :
	suffix_arch = archSuffix()
	return base+'_expected_' + suffix_arch + extension

def expectedName(base, extension) :
	"""Returns the expected wav name.
	If an architecture specific output already exists, it will use it.
	"""
	expected = expectedArchName(base, extension)
	if os.access(expected,os.R_OK): return expected

	return base+'_expected'+extension

def badResultName(base, extension = '.wav') :
	return base+'_result'+extension

def diffBaseName(base) :
	return base+'_diff'

def prefix(datapath, case, output) :
	outputBasename = os.path.splitext(os.path.basename(output))[0]
	return os.path.join(datapath, case + '_' + outputBasename )

def accept(datapath, back2BackCases, archSpecific=False, cases=[]) :
	remainingCases = cases[:]
	for case, command, outputs in back2BackCases :
		if cases and case not in cases : continue
		if cases : remainingCases.remove(case)
		for output in outputs :

			extension = os.path.splitext(output)[-1]
			base = prefix(datapath, case, output)
			badResult = badResultName(base, extension)
			if not os.access(badResult, os.R_OK) : continue
			warn("Accepting {}".format(badResult))

			if archSpecific :
				os.rename(badResult, expectedArchName(base, extension))
			else :
				os.rename(badResult, expectedName(base, extension))
	if remainingCases :
		warn("No such test cases: {}".format(
			", ".join("'%s'"%case for case in remainingCases)))

def removeIfExists(filename) :
	try: os.remove(filename)
	except: pass

def passB2BTest(datapath, case, command, outputs):
	step("Test: %s Command: '%s'"%(case,command))
	for output in outputs :
		removeIfExists(output)
	try :
		commandError = subprocess.call(command, shell=True)
		if commandError :
			return ["Command failed with return code %i:\n'%s'"%(commandError,command)]
	except OSError as e :
		return ["Unable to run command: '%s'"%(command)]
	failures = []
	for output in outputs :
		extension = os.path.splitext(output)[-1]
		base = prefix(datapath, case, output)
		expected = expectedName(base, extension)
		diffbase = diffBaseName(base)
		difference = diff_files(expected, output, diffbase)
		#diffbase = diffbase+'.wav'
		diffbase = diffbase + extension

		if not difference:
			printcolor('32;1', " Passed")
			removeIfExists(diffbase)
			removeIfExists(diffbase+'.png')
			removeIfExists(badResultName(base,extension))
		else:
			printcolor('31;1', " Failed")
			os.system('cp %s %s' % (output, badResultName(base,extension)) )
			failures.append("Output '%s':\n%s"%(base, '\n'.join(['\t- %s'%item for item in difference])))
		removeIfExists(output)
		return failures

def passB2BTests(datapath, back2BackCases) :
	failedCases = []
	for case, command, outputs in back2BackCases :
		failures = passB2BTest(datapath, case, command, outputs)
		if not failures: continue
		failedCases+=[(case, failures)]

	sys.stderr.write("Summary:\n")
	printcolor('32;1', '%i passed cases'%(len(back2BackCases)-len(failedCases)))

	if not failedCases : return True

	printcolor('31;1', '%i failed cases!'%len(failedCases))
	for case, msgs in failedCases :
		sys.stderr.write(case + " :\n")
		for msg in msgs :
			sys.stderr.write( "\t%s\n"%msg)
	return False

help ="""
To run the tests call this script without parameters.
	./back2back

Failed cases will generate *_result.wav and *_diff.wav
files for each missmatching output, containing the
obtained output and the difference with the expected one.

If some test fail but you want to accept the new results
just call:
	./back2back --accept case1 case2
where case1 and case2 are the cases to be accepted.

To know which are the available cases:
	./back2back --list

To accept any failing cases (USE IT WITH CARE) call:
	./back2back --acceptall

To accept some results but just for a given architecture,
due to floating point missmatches, use:
	./back2back --arch --accept case1 case2
"""

def _caseList(cases) :
	return "".join(["\t"+case+"\n" for case in cases])


def makeB2bTestCase(testCaseName, id) :
	def b2bTestCase(self):
		self.maxDiff = None
		resultFilename = os.path.join('b2bdata',testCaseName+'-result.html')
		expectedFilename = os.path.join('b2bdata',testCaseName+'-expected.html')
		if os.access(resultFilename, os.R_OK) :
			os.unlink(resultFilename)

		output = renderMako(self.fixture.template, self.fixture.model, id)

		try:
			with codecs.open(expectedFilename,'r', 'utf8') as expectedfile:
				expected = expectedfile.read()
		except:
			expected = None

		if expected != output :
			with codecs.open(resultFilename,'w', 'utf8') as outputfile:
				outputfile.write(output)

		if expected is None :
			self.fail(
				"No expectation for the testMethod, use the 'accept' "
				"subcommand to accept the current result as good '{}'"
				.format(resultFilename))

		self.assertMultiLineEqual(expected, output,
			"B2B data missmatch, use the 'accept' "
			"subcommand to accept the current result as good '{}'"
			.format(resultFilename))

	return b2bTestCase


def addDataDrivenTestCases():
	for testCase, fixture in testcases.items() :
		klassname = 'Test_B2B_{0}'.format(testCase)
		# Dynamically create a TestCase Subclass with all the test
		testMethods = dict([
			('test_{0}'.format(testMethod),
				makeB2bTestCase(
					testCase+'.'+testMethod, data))
			for testMethod, data in fixture.cases.items()
			]+[
				('longMessage', True),
				('fixture', fixture),
			])

		globals()[klassname] = type( klassname, (unittest.TestCase,), testMethods)

#addDataDrivenTestCases()

def assertProgramOutputsB2B(self, command, *outputs, **kwd):
	"""Runs the command and asserts the outputs are equal to the expected ones."""
	# TODO


def runBack2BackProgram(datapath, argv, back2BackCases, help=help) :

	"--help" not in sys.argv or fail(help, 0)

	architectureSpecific = "--arch" in argv
	if architectureSpecific : argv.remove("--arch")

	os.access( datapath, os.X_OK ) or fail(
		"Datapath at '%s' not available. "%datapath +
		"Check the back 2 back script on information on how to obtain it.")

	availableCases = [case for case, command, outputs in back2BackCases]

	if "--list" in argv :

		for case in availableCases :
			sys.stdout.write(case)
		sys.exit()

	if "--accept" in argv :
		cases = argv[argv.index("--accept")+1:]
		cases or fail("Option --accept needs a set of cases to accept.\nAvailable cases:\n"+"\n".join(["\t"+case for case, command, outputs in back2BackCases]))
		unsupportedCases = set(cases).difference(set(availableCases))
		if unsupportedCases:
			fail("The following specified cases are not available:\n" + _caseList(unsupportedCases) + "Try with:\n" + _caseList(availableCases))
		accept(datapath, back2BackCases, architectureSpecific, cases)
		sys.exit()

	if "--acceptall" in argv :
		warn("Accepting any faling case")
		accept(datapath, back2BackCases, architectureSpecific)
		sys.exit()

	passB2BTests(datapath, back2BackCases) or fail("Tests not passed")

def assertB2BEqual(self, result, expectedFile=None, resultFile=None):

	def safeRemove(filename):
		try: os.unlink(filename)
		except: pass

	def read(filename):
		with open(filename) as f:
			return f.read()

	def write(filename, content):
		with open(filename,'w') as f:
			f.write(content)

	if resultFile is None:
		try: os.makedirs(self.b2bdatapath)
		except OSError: pass
		resultFile = os.path.join(
			self.b2bdatapath,
			self.id()+"-result",
			)
	if expectedFile is None:
		expectedFile = os.path.join(
			self.b2bdatapath,
			self.id()+"-expected",
			)

	accepting = hasattr(self, 'acceptMode') and self.acceptMode
	try:
		expectation = read(expectedFile)
	except IOError as error:
		if accepting:
			write(expectedFile, result)
			safeRemove(resultFile)
			raise Warning("Accepting new data for '{}'"
				.format(expectedFile))
		else:
			write(resultFile, result)
			self.fail("No expectation found, please, check and accept '{}'"
				.format(resultFile))
	try:
		self.assertMultiLineEqual(result, expectation)
	except AssertionError:
		if accepting:
			write(expectedFile, result)
			safeRemove(resultFile)
			raise Warning("Accepting new data for '{}'"
				.format(expectedFile))
		else:
			write(resultFile, result)
		raise
	safeRemove(resultFile)

	return

    # old code non-tdd
	accepting = hasattr(self, 'acceptMode') and self.acceptMode

	def generateExpectation():
		if accepting:
			write(expectedFile, result)
			safeRemove(resultFile)
			raise Warning("Accepting new data for '{}'"
				.format(expectedFile))
		write(resultFile, result)

	try:
		expectation = read(expectedFile)
	except (FileNotFoundError, IOError):
		generateExpectation()

	try:
		self.assertMultiLineEqual(result,expectation)
	except (AssertionError):
		generateExpectation()
		raise
	else:
		safeRemove(resultFile)

import unittest
unittest.TestCase.assertB2BEqual = assertB2BEqual


#vim: noet sw=4 ts=4
