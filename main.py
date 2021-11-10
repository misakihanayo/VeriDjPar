#
# This example demonstrates usage of the included Python grammars
#

import sys
import os, os.path
from io import open
import glob, time
from walktree import walktree
from walkCFG import walkCFG

from lark import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta
from lark.indenter import Indenter

# __path__ = os.path.dirname(__file__)

class PythonIndenter(Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types = ['LPAR', 'LSQB', 'LBRACE']
    CLOSE_PAREN_types = ['RPAR', 'RSQB', 'RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8

kwargs = dict(rel_to=__file__, postlex=PythonIndenter(), start='file_input')

python_parser3 = Lark.open('python3.lark', parser='lalr', **kwargs)

def readfile(filepath):
    files = []
    pathDir = os.listdir(filepath)
    for allDir in pathDir:
        child = os.path.join('%s%s' % (filepath, allDir))
        if not '.' in child:
            for childdirs in os.listdir(child):
                pathDir.append(allDir + '/' + childdirs)
        print(child)
        files.append(child)
    return files


def _read(fn, *args):
    kwargs = {'encoding': 'iso-8859-1'}
    with open(fn, *args, **kwargs) as f:
        return f.read()

def _get_lib_path():
    if os.name == 'nt':
        if 'PyPy' in sys.version:
            return os.path.join(sys.prefix, 'lib-python', sys.winver)
        else:
            return os.path.join(sys.prefix, 'Lib')
    else:
        return [x for x in sys.path if x.endswith('%s.%s' % sys.version_info[:2])][0]

def test_python_lib():

    path = "/Users/mskhana/PycharmProjects/VeriDjPar/input/"
    file_list = readfile(path)
    start = time.time()
    # files = glob.glob(path)
    root_lists = []
    for f in file_list:
        print(f)
        if not '.py' in f:
            continue
        if 'migration' in f:
            continue
        try:
            # print list(python_parser.lex(_read(os.path.join(path, f)) + '\n'))
            try:
                xrange
            except NameError:
                root_lists.append(python_parser3.parse(_read(os.path.join(path, f)) + '\n'))
            else:
                python_parser2.parse(_read(os.path.join(path, f)) + '\n')
        except:
            print ('At %s' % f)
            raise
    end = time.time()
    return root_lists



if __name__ == '__main__':
    root = test_python_lib()
    walktree_ = walktree()
    for file_input in root:
        class_list, relation_list, global_funcs = walktree_.file_input(file_input)
        for classes in class_list:
            for func in classes.func:
                print(func.name)
                func.CFG.print_cfg_md()
                walkCFG_ = walkCFG(cfg=func.CFG, relations=relation_list, classes= class_list)
                #walkCFG_.call_walk()
            print('\n')


    #walkCFG_ = walkCFG(cfg = CFG, relations=relation_list, classes=class_list)
    #walkCFG_.call_walk()

    # test_earley_equals_lalr()
    # python_parser3.parse(_read(sys.argv[1]) + '\n')