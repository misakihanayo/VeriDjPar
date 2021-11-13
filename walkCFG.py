from basicblock import CFG, BasicBlock
import lark.tree


class walkCFG:
    def __init__(self, cfg=None, classes = None, relations = None, file = None, function = None, myclass = None):
        if classes == None:
            classes = []
        if relations == None:
            relations = []
        self.cfg = cfg
        self.def_var = []
        self.instructions = []
        self.file = file
        self.path = []
        self.classes = classes
        self.relations = relations
        self.function = function
        self.myclass = myclass

    def call_walk(self):
        self.cfg.print_args()
        for block in self.cfg.block_dict:
            if block.is_function_define:
                self.walk(block)

    def in_class(self, var):
        for ormclass in self.classes:
            if var == ormclass.name:
                return True
        return False

    def in_func_arg(self, var):
        for arg in self.function.args:
            if var == arg[0]:
                return True
        return False

    def walk(self, block):
        self.path.append(block.name)
        print('current path is, ', self.path)
        block_def_var = []
        block_instruction = []
        for operation in block.operations:
            print('handle operation:')
            print(operation.pretty())
            cur_instr = ''
            if operation.data == 'expr_stmt':
                var, isFunccall = self.expr_var(operation)
                if isFunccall != None:
                    block_instruction.append(var + '<-' + self.function_call_operation(isFunccall))

                block_def_var.append(var)
            elif operation.data == 'compound_stmt':
                # In CFG, all noted operation should have no compound statement
                pass
            elif operation.data == 'funccall':
                block_instruction.append(self.function_call_operation(operation))
        self.def_var.append(block_def_var)
        ## TODO: add guard instructions when walk through blocks
        if len(block.succ_block) > 0:
            for next_block in block.succ_block:
                block_instruction.append(self.add_guard(next_block[1]))
                self.instructions.append(block_instruction)
                self.walk(self.cfg.get_block(next_block[0]))
                self.instructions.pop()
                block_instruction.pop()
            self.def_var.pop()
        else:
            self.print_instruction(self.instructions)

    # define several function to seperate the statement

    def function_call_operation(self, operation):
        varlist = self.analyze_funccall(operation)
        print('New varlist is ',varlist)
        var = varlist[0][0]
        if self.in_class(var) or self.in_func_arg(var):
            expression = ''
            for func in varlist:
                if func[1] == 'get_event_queryset':
                    expression = 'all(%s)' % (var)
                elif func[1] == 'filter':
                    vars = ''
                    for arg in func[3]:
                        vars += '.'+arg[0] + '=' + arg[1]
                    expression = 'filter(%s, %s)' % (vars, expression)
                elif func[1] == 'exclude':
                    vars = ''
                    for arg in func[3]:
                        vars += '.'+arg[0] + '!=' + arg[1]
                    expression = 'filter(%s, %s)' % (vars, expression)
                elif func[1] == 'annotate':
                    pass
                elif func[1] == 'alias':
                    pass
                elif func[1] == 'orderby':
                    vars = ''
                    for arg in func[3]:
                        cur_var = '%s' % (self.get_field(var, arg))
                    expression = 'orderby(%s, %s, %s)' % ('todo','todo','todo')
                elif func[1] == 'save':
                    if func[0] == 'serializer':
                        expression = 'insert serializer'
                # TODO: distinguish ORM function call from expr
                elif self.
            return expression

    def expr_var(self, stmt):
        print ('stmt is, ', stmt.pretty())
        isFunccall = None
        assignvalue = stmt.children[1]
        if assignvalue.data == 'funccall':
            print('funccall is ', assignvalue)
            isFunccall = assignvalue
        return stmt.children[0].children[0], isFunccall

    def analyze_funccall(self, operation):
        funccalllist = []
        funccalllist, attr, var = self.analyze_attr(operation.children[0])
        args = []
        try:
            args = self.analyze_funcargs(operation.children[1])
        except:
            pass
        funccalllist.append((var, attr, args))
        return funccalllist

    def analyze_attr(self, attrs):
        var = ''
        cur_attr = ''
        funccalllist = []
        for attr in attrs.children:
            if type(attr) == lark.Token:
                cur_attr = attr.value
            elif attr.data == 'funccall':
                funccalllist = self.analyze_funccall(attr)
            elif attr.data == 'var':
                var_token = attr.children[0]
                var = var_token.value
        return funccalllist, cur_attr, var

    def get_arg_name(self, arg):
        if type(arg) == lark.Token:
            return arg.value
        else:
            return arg.children[0].value

    def analyze_funcargs(self, arglist):
        args = []
        for argvalue in arglist.children:
            if len(argvalue.children) > 1:
                target = self.get_arg_name(argvalue.children[0])
                assign = self.get_arg_name(argvalue.children[1])
                args.append((target, assign))
            else:
                target = self.get_arg_name(argvalue.children[0])
                assign = ''
                args.append((target, assign))
        return args

    def get_field(self, var, arg):
        for myclass in self.classes:
            if myclass.name == var:
                for myarg in myclass.args:
                    if myarg[0] == arg:
                        pass

    def add_guard(self, conds):
        print('cond is ', conds)
        if conds is None:
            return
        str = ''
        for cond in conds:
            if cond[1]:
                str += self.print_test(cond[0])
            else:
                str += 'not ' + self.print_test(cond[0])
            if cond != conds[-1]:
                str += ' and '
        return str

    def print_instruction(self, instructions):
        operation_name = ''
        for each_path in self.path:
            operation_name += each_path
        self.file.write('op'+operation_name+'('+self.get_func_args()+')')
        print('instructions are ', instructions)
        for block_inst in instructions:
            for inst in block_inst:
                print (inst)
                self.file.write(inst)

    def get_func_args(self):
        str = ''
        for arg in self.function.args:
            if arg[0] == 'self':
                pass
            else:
                str += arg[0]

            if arg == self.function.args[-1]:
                pass
            else:
                str += ','
        return str

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

