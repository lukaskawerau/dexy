from dexy.tests.utils import assert_output
from dexy.tests.utils import assert_in_output
from dexy.tests.utils import wrap
from dexy.tests.utils import TEST_DATA_DIR
from dexy.doc import Doc
import os
import shutil

def test_r_batch():
    assert_output('rout', 'print(1+1)', "[1] 2\n")

def test_r_int_batch():
    assert_output('rintbatch', '1+1', "> 1+1\n[1] 2\n> \n")

def test_ragel_ruby_filter():
    assert_in_output('rlrb', RAGEL, "_keys = _hello_and_welcome_key_offsets[cs]", ext=".rl")

def test_ps2pdf_filter():
    with wrap() as wrapper:
        doc = Doc("hello.ps|ps2pdf",
                contents = PS,
                wrapper=wrapper)
        wrapper.docs = [doc]
        wrapper.run()
        assert doc.output().is_cached()
        assert doc.output().filesize() > 1000

def test_html2pdf_filter():
    with wrap() as wrapper:
        doc = Doc("hello.html|html2pdf",
                contents = "<p>hello</p>",
                wrapper=wrapper)
        wrapper.docs = [doc]
        wrapper.run()
        assert doc.output().is_cached()
        assert doc.output().filesize() > 1000

def test_dot_filter():
    with wrap() as wrapper:
        doc = Doc("graph.dot|dot",
                contents = "digraph { a -> b } ",
                wrapper=wrapper)
        wrapper.docs = [doc]
        wrapper.run()
        assert doc.output().is_cached()
        assert doc.output().filesize() > 1000

def test_pdf2img_filter():
    with wrap() as wrapper:
        orig = os.path.join(TEST_DATA_DIR, 'color-graph.pdf')
        shutil.copyfile(orig, 'example.pdf')
        doc = Doc("example.pdf|pdf2img",
                wrapper=wrapper)

        wrapper.docs = [doc]
        wrapper.run()
        assert doc.output().is_cached()
        assert doc.output().filesize() > 1000

def test_pdf2jpg_filter():
    with wrap() as wrapper:
        orig = os.path.join(TEST_DATA_DIR, 'color-graph.pdf')
        shutil.copyfile(orig, 'example.pdf')
        doc = Doc("example.pdf|pdf2jpg",
                wrapper=wrapper)

        wrapper.docs = [doc]
        wrapper.run()
        assert doc.output().is_cached()

def test_bw_filter():
    with wrap() as wrapper:
        orig = os.path.join(TEST_DATA_DIR, 'color-graph.pdf')
        shutil.copyfile(orig, 'example.pdf')
        doc = Doc("example.pdf|bw",
                wrapper=wrapper)

        wrapper.docs = [doc]
        wrapper.run()
        assert doc.output().is_cached()

def test_asciidoc_filter():
    assert_in_output("asciidoc", "hello", """<div class="paragraph"><p>hello</p></div>""")

def test_pandoc_filter():
    assert_output("pandoc", "hello", "<p>hello</p>\n", ext=".md")

def test_espeak_filter():
    with wrap() as wrapper:
        doc = Doc("subdir/hello.txt|espeak",
                contents="hello",
                wrapper=wrapper)

        wrapper.docs = [doc]
        wrapper.run()

        assert doc.output().is_cached()

PS = """%!PS
1.00000 0.99083 scale
/Courier findfont 12 scalefont setfont
0 0 translate
/row 769 def
85 {/col 18 def 6 {col row moveto (Hello World)show /col col 90 add def}
repeat /row row 9 sub def} repeat
showpage save restore"""

RD = """
 \\name{load}
     \\alias{load}
     \\title{Reload Saved Datasets}
     \description{
       Reload the datasets written to a file with the function
       \code{save}.
     }
"""

RAGEL = """%%{
  machine hello_and_welcome;
  main := ( 'h' @ { puts "hello world!" }
          | 'w' @ { puts "welcome" }
          )*;
}%%
  data = 'whwwwwhw'
  %% write data;
  %% write init;
  %% write exec;
"""
