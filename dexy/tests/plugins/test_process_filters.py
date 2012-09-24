from dexy.doc import Doc
from dexy.plugins.process_filters import SubprocessFilter
from dexy.tests.utils import wrap
import dexy.exceptions

def test_walk_working_dir():
    with wrap() as wrapper:
        doc = Doc("example.sh|sh",
                contents = "echo 'hello' > newfile.txt",
                sh = {
                    "walk-working-dir" : True,
                    },
                wrapper=wrapper)

        wrapper.docs = [doc]
        wrapper.run()

        for doc in wrapper.registered:
            if doc.key_with_class() == "Doc:example.sh-sh.txt-files":
                assert doc.output().as_sectioned()['newfile.txt'] == "hello\n"

def test_add_new_files():
    with wrap() as wrapper:
        doc = Doc("example.sh|sh",
                contents = "echo 'hello' > newfile.txt",
                sh = {
                    "add-new-files" : True,
                    "additional-doc-filters" : { '.txt' : 'markdown' }
                    },
                wrapper=wrapper)

        wrapper.docs = [doc]
        wrapper.run()

        assert wrapper.registered_docs()[1].key == 'newfile.txt'
        assert wrapper.registered_docs()[1].output().data() == "hello\n"

        assert wrapper.registered_docs()[2].key == 'newfile.txt|markdown'
        assert wrapper.registered_docs()[2].output().data() == "<p>hello</p>"

def test_not_present_executable():
    assert 'notreal' in NotPresentExecutable.executables()
    assert not NotPresentExecutable.executable()

class NotPresentExecutable(SubprocessFilter):
    EXECUTABLE = 'notreal'

def test_command_line_args():
    with wrap() as wrapper:
        doc = Doc("example.py|py",
                py={"args" : "-B"},
                wrapper=wrapper,
                contents="print 'hello'"
                )
        wrapper.docs = [doc]
        wrapper.run()

        assert doc.output().data() == "hello\n"

        command_used = doc.artifacts[-1].filter_instance.command_string()
        assert command_used == "python -B example.py  example.txt"

def test_scriptargs():
    with wrap() as wrapper:
        doc = Doc("example.py|py",
                py={"scriptargs" : "--foo"},
                wrapper=wrapper,
                contents="import sys\nprint sys.argv[1]"
                )
        wrapper.docs = [doc]
        wrapper.run()

        assert doc.output().data() == "--foo\n"

        command_used = doc.artifacts[-1].filter_instance.command_string()
        assert command_used == "python  example.py --foo example.txt"

def test_custom_env_in_args():
    with wrap() as wrapper:
        doc = Doc("example.py|py",
                py={"env" : {"FOO" : "bar" }},
                wrapper=wrapper,
                contents="import os\nprint os.environ['FOO']"
                )
        wrapper.docs = [doc]
        wrapper.run()

        assert doc.output().data() == "bar\n"

def test_nonzero_exit():
    with wrap() as wrapper:
        doc = Doc("example.py|py",
                wrapper=wrapper,
                contents="import sys\nsys.exit(1)"
                )
        wrapper.docs = [doc]
        try:
            wrapper.run()
            assert False, "should raise NonzeroExit"
        except dexy.exceptions.NonzeroExit:
            assert True

def test_ignore_nonzero_exit():
    with wrap() as wrapper:
        wrapper.ignore_nonzero_exit = True
        doc = Doc("example.py|py",
                wrapper=wrapper,
                contents="import sys\nsys.exit(1)"
                )
        wrapper.docs = [doc]
        wrapper.run()
        assert True # no NonzeroExit was raised...