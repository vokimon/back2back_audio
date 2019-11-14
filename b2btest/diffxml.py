from  unittest import TestCase
import os

def assertXmlEqual(self, got, want):
	from lxml.doctestcompare import LXMLOutputChecker
	from doctest import Example

	checker = LXMLOutputChecker()
	if checker.check_output(want, got, 0):
		return
	message = checker.output_difference(Example("", want), got, 0)
	raise AssertionError(message)

TestCase.assertXmlEqual = assertXmlEqual

def differences(expected, result, diffbase):
	extension = os.path.splitext(result)[-1]
	difftxt = diffbase+extension

	with open(expected) as f:
		expectedContent = f.read()

	with open(result) as f:
		resultContent = f.read()

	try:
		assertXmlEqual(None, resultContent, expectedContent)
		return []
	except AssertionError as e:
		result = e.args
	return result

differences.extensions = [
	'.xml',
	]

def main():
	import sys
	diffs = differences(*sys.argv[1:])
	if not diffs : sys.stdout.write("Ok\n"); sys.exit(0)
	for d in diffs :
		print >> sys.stderr, d



