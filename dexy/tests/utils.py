from StringIO import StringIO
from dexy.common import OrderedDict
from dexy.exceptions import InactiveFilter
from dexy.utils import char_diff
from dexy.wrapper import Wrapper
from nose.exc import SkipTest
import dexy.commands
import dexy.data
import dexy.metadata
import os
import re
import shutil
import sys
import tempfile

TEST_DATA_DIR = os.path.join(os.getcwd(), 'dexy', 'tests', 'data')

def create_ordered_dict_from_dict(d):
    od = OrderedDict()
    for k, v in d.iteritems():
        od[k] = v
    return od

class tempdir():
    def __enter__(self):
        self.tempdir = tempfile.mkdtemp()
        self.location = os.path.abspath(os.curdir)
        os.chdir(self.tempdir)

    def __exit__(self, type, value, traceback):
        os.chdir(self.location)
        shutil.rmtree(self.tempdir)

class wrap(tempdir):
    """
    Create a temporary directory and initialize a dexy wrapper.
    """
    def __enter__(self):
        self.tempdir = tempfile.mkdtemp()
        self.location = os.path.abspath(os.curdir)
        os.chdir(self.tempdir)
        wrapper = Wrapper()
        wrapper.setup_run(setup_docs=False)
        return wrapper

class runfilter(tempdir):
    """
    Create a temporary directory, initialize a doc and a wrapper, run the doc.

    Raises SkipTest on inactive filters.
    """
    def __init__(self, filter_alias, doc_contents, ext=".txt"):
        self.filter_alias = filter_alias
        self.doc_contents = doc_contents
        self.ext = ext

    def __enter__(self):
        # Create a temporary working dir and move to it
        self.tempdir = tempfile.mkdtemp()
        self.location = os.path.abspath(os.curdir)
        os.chdir(self.tempdir)

        # Create a document. Skip testing documents with inactive filters.
        try:
            doc_key = "example%s|%s" % (self.ext, self.filter_alias)
            doc_spec = [doc_key, {"contents" : self.doc_contents}]
            wrapper = Wrapper(doc_spec)
            wrapper.run()
        except InactiveFilter:
            print "Skipping tests for inactive filter", self.filter_alias
            raise SkipTest

        return wrapper.docs[0]

def assert_output(filter_alias, doc_contents, expected_output, ext=".txt",args={}):
    if not ext.startswith("."):
        raise Exception("ext arg to assert_in_output must start with dot")

    if isinstance(expected_output, dict):
        expected_output = create_ordered_dict_from_dict(expected_output)
    if isinstance(doc_contents, dict):
        doc_contents = create_ordered_dict_from_dict(doc_contents)

    with runfilter(filter_alias, doc_contents, ext=ext) as doc:
        if expected_output:
            try:
                assert doc.output().data() == expected_output
            except AssertionError as e:
                if not isinstance(expected_output, OrderedDict):
                    print char_diff(doc.output().as_text(), expected_output)
                else:
                    print "Output: %s" % doc.output().data()
                    print "Expected: %s" % expected_output

                raise e
        else:
            raise Exception("Output is '%s'" % doc.output().data())

def assert_output_matches(filter_alias, doc_contents, expected_regex, ext=".txt"):
    if not ext.startswith("."):
        raise Exception("ext arg to assert_in_output must start with dot")

    with runfilter(filter_alias, doc_contents, ext=ext) as doc:
        if expected_regex:
            assert re.match(expected_regex, doc.output().as_text())
        else:
            raise Exception(doc.output().as_text())

def assert_in_output(filter_alias, doc_contents, expected_output, ext=".txt"):
    if not ext.startswith("."):
        raise Exception("ext arg to assert_in_output must start with dot")

    with runfilter(filter_alias, doc_contents, ext=ext) as doc:
        if expected_output:
            assert expected_output in doc.output().as_text()
        else:
            raise Exception(doc.output().as_text())

def assert_not_in_output(filter_alias, doc_contents, expected_output):
    with runfilter(filter_alias, doc_contents) as doc:
        assert not expected_output in doc.output().as_text()

class divert_stdout():
    def __enter__(self):
        self.old_stdout = sys.stdout
        self.my_stdout = StringIO()
        sys.stdout = self.my_stdout
        return self.my_stdout

    def __exit__(self, type, value, traceback):
        sys.stdout = self.old_stdout
        self.my_stdout.close()

class divert_stderr():
    def __enter__(self):
        self.old_stderr = sys.stderr
        self.my_stderr = StringIO()
        sys.stderr = self.my_stderr
        return self.my_stderr

    def __exit__(self, type, value, traceback):
        sys.stderr = self.old_stderr
        self.my_stderr.close()
