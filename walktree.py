from lark import Lark, ast_utils, Transformer, v_args
import lark.tree
from lark.tree import Meta
from lark.indenter import Indenter
import traceback
from basicblock import CFG, BasicBlock


class ORMclass:
    def __init__(self):
        self.name = ''
        self.args = []
        self.constants = []
        self.func = []


class ORMfunc:
    def __init__(self):
        self.name = ''
        self.args = []
        self.CFG = None
        self.infunc = False


class EXPRclass:
    def __init__(self):
        varname = ''
        Type = ''


class ConstList:
    def __init__(self):
        self.name = ''
        self.member = []


class walktree:
    def __init__(self):
        self.current_class = None
        self.current_def = []
        self.current_func = None
        self.current_cond = []
        self.class_list = []
        self.field_list = []
        self.relation_list = []
        self.global_func = []
        self.branchtree = []
        self.operations = []
        self.methods = {}
        self.args = {}
        self.current_block = BasicBlock()
        self.CFG = CFG()

    def suit(self, root):
        field = []
        print('current suite has condition ', self.current_cond)
        if len(self.current_cond) != 0:
            self.branchtree.append(self.current_cond)
        for child in root.children:
            if type(child) == lark.Tree:
                print("found a Tree", child.data)
                if child.data == 'expr_stmt':
                    print(child.pretty())
                    var = child.children[0]
                    var_name = var.children[0]
                    # possibility 1: the expr_stmt is a field define
                    if child.children[1].data == 'funccall':
                        try:
                            print("found a function call")
                            func_call = child.children[1]
                            print("function call is ", self.print_test(func_call.children[0]))
                            attr = func_call.children[0]
                            field_type = attr.children[-1]
                            print('type is ', field_type)
                            # a function call can be a model defination
                            # iff current expression is in a class suite
                            if len(func_call.children) > 1:
                                args = func_call.children[1]
                                argvalues = args.children
                            else:
                                argvalues = []
                            if self.current_func is None:
                                print('ORM function call')
                                attribute = False
                                for argvalue in argvalues:
                                    print('current argvalue is', argvalue)
                                    try:
                                        if type(argvalue.children[0]) == lark.Tree:
                                            if argvalue.children[0].children[0].value == 'primary_key':
                                                attribute = True
                                    except:
                                        pass
                                if field_type == 'ForeignKey':
                                    print("has a Foreign Key")
                                    from_model = self.current_class.name
                                    from_model.strip('"')
                                    from_model.lstrip('"')
                                    relation_name = from_model + '_' + var_name.value
                                    relation_type = 'onemany'
                                    to_model = ''
                                    for argvalue in argvalues:
                                        # In Django, to = "name" has the same attribute with "name"
                                        if type(argvalue.children[0]) == lark.Token:
                                            to_model = argvalue.children[0].value
                                        elif argvalue.children[0].children[0].value == 'to':
                                            to_model = argvalue.children[1].children[0].value
                                            to_model.strip()
                                            to_model.strip('"')
                                            to_model.lstrip('"')
                                        elif argvalue.children[0].children[0].value == 'related_name':
                                            relation_name = argvalue.children[1].children[0].value
                                    self.relation_list.append((relation_name, relation_type, from_model, to_model))
                                elif field_type == 'OneToOne':
                                    print('Has a OneToOne model')
                                    from_model = self.current_class.name
                                    from_model.strip('"')
                                    from_model.lstrip('"')
                                    relation_name = from_model + '_' + var_name.value
                                    relation_type = 'oneone'
                                    to_model = ''
                                    for argvalue in argvalues:
                                        if type(argvalue.children[0]) == lark.Token:
                                            relation_name = argvalue.children[0].value
                                        elif argvalue.children[0].children[0].value == 'to':
                                            to_model = argvalue.children[1].children[0].value
                                            to_model.strip()
                                            to_model.strip('"')
                                            to_model.lstrip('"')
                                            break
                                    self.relation_list.append((relation_name, relation_type, from_model, to_model))
                                elif field_type == 'ManyToManyField':
                                    from_model = self.current_class.name
                                    from_model.strip('"')
                                    from_model.lstrip('"')
                                    relation_name = from_model + '_' + var_name.value
                                    relation_type = 'manymany'
                                    to_model = ''
                                    for argvalue in argvalues:
                                        if type(argvalue.children[0]) == lark.Token:
                                            relation_name = argvalue.children[0].value
                                        elif argvalue.children[0].children[0].value == 'to':
                                            to_model = argvalue.children[1].children[0].value
                                            to_model.strip()
                                            to_model.strip('"')
                                            to_model.lstrip('"')
                                            break
                                    self.relation_list.append((relation_name, relation_type, from_model, to_model))
                                elif 'Field' in field_type:
                                    field = (var_name.value, field_type.value, attribute)
                                    print("analyzed a field: ", field)
                                    self.current_class.args.append(field)
                            else:
                                # current function call is a normal function call
                                print('Normal function call')
                                cond_str = ''
                                func_args = []
                                for cond in self.current_cond:
                                    cond_str += cond + ', '
                                if not (cond_str in self.methods):
                                    self.methods[cond_str] = []
                                for arg in argvalues:
                                    arg_str = self.current_class.name + '_' + self.current_func.name \
                                              + '_' + self.print_test(arg)
                                    func_args.append(arg_str)
                                print('cond_str is ', cond_str)
                                print('func args are ', func_args)
                                self.current_block.add_operation(child)
                        except:
                            print('dumped')
                            traceback.print_exc()
                    elif child.children[1].data == 'getattr':
                        self.current_block.add_operation(child)
                    elif child.children[1].data == 'term':
                        self.current_block.add_operation(child)
                    elif child.children[1].data == 'list':
                        list = child.children[1]
                        if len(list.children) > 0:
                            testlist_comp = list.children[0]
                            const_list = ConstList()
                            const_list.name = var_name
                            for element in testlist_comp.children:
                                const_list.member.append(element)
                        if self.current_func is None:
                            self.current_class.constants.append(const_list)
                        else:
                            self.current_block.add_operation(child)
                elif child.data == 'compound_stmt':
                    if child.children[0].data == 'if_stmt':
                        curbranch = self.if_stmt(child.children[0])
                    if child.children[0].data == 'funcdef':
                        self.func_def(child.children[0])
                elif child.data == 'return_stmt':
                    self.current_block.add_operation(child)
                    # if a function returned with no side effect and no branches, we link
                    # this function to the original call?
                elif child.data == 'funccall':
                    self.current_block.add_operation(child)

    def if_stmt(self, root):
        print('if stmt is in func ', self.current_func)
        print(root.pretty())
        branchtable = []
        curbranch = []
        current_cond = ''
        if self.current_cond:
            current_cond = self.current_cond[-1]
        is_else = True
        prevbb = self.current_block
        exitbb = BasicBlock(name=self.current_func.name + current_cond + '_exitbb', cond=self.current_cond,
                            func=self.current_func, parent_class=self.current_class)
        condition = []
        self.CFG.add_block(exitbb)
        has_else = False
        for child in root.children:
            if child.data == 'suite':
                cond = ''
                for curbr in curbranch:
                    if curbr != curbranch[-1]:
                        cond += 'not ' + curbr
                    else:
                        if is_else:
                            cond += 'not ' + curbr
                            has_else = True
                        else:
                            cond += curbr
                is_else = True
                branchtable.append(cond)
                self.current_cond.append(cond)
                newbb = BasicBlock(name=self.current_func.name + cond, cond=self.current_cond,
                                   func=self.current_func, parent_class=self.current_class)
                self.CFG.add_block(newbb)
                prevbb.add_succ_basic_block(newbb, condition)
                newbb.add_pre_basic_block(prevbb)
                self.current_block = newbb
                self.suit(child)
                if not self.current_block.returned:
                    self.current_block.add_succ_basic_block(exitbb, None)
                    exitbb.add_pre_basic_block(self.current_block)
                self.current_cond.pop()
                condition[-1] = (condition[-1][0], False)
            else:
                test = child
                condition.append((test, True))
                test_expr = self.print_test(test)
                print('test_expr is ', test_expr)
                curbranch.append(test_expr)
                is_else = False
                exitbb.name = self.current_func.name + current_cond + curbranch[0] + '_exitbb'
        if not has_else:
            exitbb.add_pre_basic_block(prevbb)
            prevbb.add_succ_basic_block(exitbb, condition)
        self.current_block = exitbb
        return branchtable

    def get_func_name(self, root):
        if type(root) == lark.Token:
            return root.value
        else:
            ret_str = ''
            for child in root.children:
                print(child)
                ret_str += self.get_func_name(child)
            return ret_str

    def class_def(self, root):
        print("class def is ", root.data)
        for child in root.children:
            if type(child) == lark.Token:
                self.current_class = ORMclass()
                self.current_class.name = child.value
                print("cur class is ", self.current_class.name)
            elif child.data == 'arguments':
                pass
            else:
                print("entered suite")
                self.suit(child)
        self.class_list.append(self.current_class)

    def func_def(self, root):
        print("func_def is ", root.pretty())
        prev_func = self.current_func
        prev_cfg = self.CFG
        self.current_func = ORMfunc()
        self.CFG = CFG()
        for child in root.children:
            if type(child) == lark.Token:
                self.current_func.name = child.value
                self.current_func.infunc = True
            elif child.data == 'parameters':
                print('parameters', child.children)
                self.get_parameters(child)
            else:
                func_basicblock = BasicBlock(name=self.current_func.name, cond='',
                                             func=self.current_func, parent_class=self.current_class,
                                             is_function_define=True)
                self.CFG.add_block(func_basicblock)
                self.current_block = func_basicblock
                print('in func_def current_func is ', self.current_func.name)
                self.suit(child)
        self.current_func.CFG = self.CFG
        self.CFG = prev_cfg
        if self.current_class is not None:
            self.current_class.func.append(self.current_func)
        else:
            self.global_func.append(self.current_func)
        self.current_func = prev_func

    def analyze_paramvalue(self, root):
        print('in analyze_paramvalue', root)
        var = ''
        argtype = ''
        init = ''

        var, argtype = self.analyze_typedparam(root.children[0])
        init = self.print_test(root.children[1])
        return var, argtype, init

    def analyze_typedparam(self, root):
        if type(root) == lark.Token:
            var = root.value
            argtype = ''
            return var, argtype
        else:
            var = root.children[0].value
            argtype = ''
            if len(root.children) > 1:
                argtype = root.children[1].children[0].value
            return var, argtype

    def analyze_starparams(self, root):
        starparams = []
        for child in root.children:
            var = ''
            argtype = ''
            init = ''
            if type(child) == lark.Token:
                var = child.value
            elif child.data == 'paramvalue':
                var, argtype, init = self.analyze_paramvalue(child)
            elif child.data == 'typedparam':
                var, argtype = self.analyze_typedparam(child)
            else:
                var, argtype = self.analyze_kwparams(child)
            if child == root.children[0]:
                # this param is the star param
                argtype = '*' + argtype
            starparams.append((var, argtype, init))
        return starparams

    def analyze_kwparams(self, root):
        var, argtype = self.analyze_typedparam(root.children[0])
        return var, '**' + argtype

    def get_parameters(self, root):
        for child in root.children:
            if type(child) == lark.Token:
                var = child.value
                self.current_func.args.append((var, '', ''))
            elif child.data == 'paramvalue':
                var, argtype, init = self.analyze_paramvalue(child)
                self.current_func.args.append((var, argtype, init))
            elif child.data == 'typedparam':
                var, argtype = self.analyze_typedparam(child)
                self.current_func.args.append((var, argtype, ''))
            elif child.data == 'starparams':
                starparams = self.analyze_starparams(child)
                for param in starparams:
                    self.current_func.args.append(param)
            elif child.data == 'kwparams':
                var, argtype = self.analyze_kwparams(child)
                self.current_func.args.append((var, argtype, ''))

    def file_input(self, root):
        for child in root.children:
            print("file_input", child.data)
            if child.data == 'compound_stmt':
                for child_ in child.children:
                    if child_.data == 'classdef':
                        self.class_def(child_)
                    elif child_.data == 'funcdef':
                        self.func_def(child_)

#        print('classes:')
#        for each_class in self.class_list:
#             print(each_class.name)
#             print(each_class.args)
#         print('relations:')
#         for relation in self.relation_list:
#             print(relation)

        self.CFG.print_cfg()
        self.CFG.print_cfg_md()
        return self.class_list, self.relation_list, self.global_func

    # def adjust_to_soir(self):
    #     for each_class in self.class_list:
    #         if each_class.args[1] == 'CharField':
    #             each_class.args[1] = 'string'
    #         elif each_class.args[1] == 'BooleanField':
    #             each_class.args[1] = 'Boolean'
    #

    def print_test(self, root):
        if type(root) == lark.Token:
            return root.value
        else:
            if root.data == 'or_test':
                ret_str = ''
                for child in root.children:
                    ret_str = ret_str + self.print_test(child)
                    if child != root.children[-1]:
                        ret_str += ' or '
                return ret_str
            elif root.data == 'and_test':
                ret_str = ''
                for child in root.children:
                    ret_str = ret_str + self.print_test(child)
                    if child != root.children[-1]:
                        ret_str += ' and '
                return ret_str
            elif root.data == 'not':
                ret_str = 'not ' + self.print_test(root.children[0])
                return ret_str
            elif root.data == 'comparison':
                return self.print_test(root.children[0]) + self.print_test(root.children[1]) + self.print_test(
                    root.children[2])
            elif root.data == 'funccall':
                if len(root.children) > 1:
                    var = root.children[0]
                    arguments = root.children[1]
                    ret_str = ''
                    ret_str = ret_str + self.get_func_name(var.children[0]) + '('
                    for arg in arguments.children:
                        ret_str = ret_str + self.print_test(arg)
                        if arg != arguments.children[-1]:
                            ret_str = ret_str + ','
                    return ret_str + ')'
                else:
                    var = root.children[0]
                    ret_str = self.get_func_name(var.children[0]) + '()'
                    return ret_str

            elif root.data == 'const_false' or root.data == 'const_true':
                return root.data
            elif root.data == 'var':
                return self.print_test(root.children[0])
            elif root.data == 'number':
                return self.print_test(root.children[0])
            elif root.data == 'term':
                ret_str = ''
                for arg in root.children:
                    ret_str += self.print_test(arg)
                return ret_str
            elif root.data == 'tuple':
                ret_str = '('
                for arg in root.children[0].children:
                    ret_str += self.print_test(arg)
                    if root.children[-1] != arg:
                        ret_str += ','
                return ret_str + ')'
            elif root.data == 'getattr':
                ret_str = ''
                for attr in root.children:
                    ret_str += self.print_test(attr)
                    if attr != root.children[-1]:
                        ret_str += '.'
                return ret_str
            elif root.data == 'string':
                return self.print_test(root.children[0])
        return ''
