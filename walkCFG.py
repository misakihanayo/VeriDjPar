from basicblock import CFG, BasicBlock
import lark.tree


class walkCFG:
    def __init__(self, cfg=None, classes = None, relations = None):
        if classes == None:
            classes = []
        if relations == None:
            relations = []
        self.cfg = cfg
        self.def_var = []
        self.instructions = []
        self.path = []
        self.classes = classes
        self.relations = relations

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

    def walk(self, block):
        self.path.append(block.name)
        print('current path is, ', self.path)
        block_def_var = []
        block_instruction = []
        for operation in block.operations:
            if operation.data == 'expr_stmt':
                var, isFunccall = self.expr_var(operation)
                if isFunccall != None:
                    block_instruction.append(self.function_call_operation(isFunccall))
                block_def_var.append(var)
            elif operation.data == 'compound_stmt':
                # In CFG, all noted operation should have no compound statement
                pass
            elif operation.data == 'funccall':
                block_instruction.append(self.function_call_operation(operation))


        self.def_var.append(block_def_var)
        self.instructions.append(block_instruction)
        for next_block in block.succ_block:
            self.walk(self.cfg.get_block(next_block))
        self.def_var.pop()
        self.instructions.pop()

    # define several function to seperate the statement

    def function_call_operation(self, operation):
        varlist = self.analyze_funccall(operation)
        print('New varlist is ',varlist)
        var = varlist[0][0]
        if self.in_class(var):
            expression = ''
            for func in varlist:
                if func[1] == 'get_event_queryset':
                    expression = 'all(%s)' % (var)
                elif func[1] == 'filter':
                    vars = ''
                    for arg in func[3]:
                        vars += '.'+arg[0] + '=' + arg[1]
                    expression = 'filter(%s, %s)' % ('vars', expression)
                elif func[1] == 'exclude':
                    vars = ''
                    for arg in func[3]:
                        vars += '.'+arg[0] + '!=' + arg[1]
                    expression = 'filter(%s, %s)' % ('vars', expression)
                elif func[1] == 'annotate':
                    pass
                elif func[1] == 'alias':
                    pass
                elif func[1] == 'orderby':
                    vars = ''
                    for arg in func[3]:
                        vars += '.(%s)' % (self.get_field(var, arg))
                # TODO: distinguish ORM function call from expr

    def expr_var(self, stmt):
        print ('stmt is, ', stmt.pretty())
        isFunccall = None
        assignvalue = stmt.children[1]
        if assignvalue.data == 'funccall':
            print('funccall is ', assignvalue)
            isFunccall = assignvalue
        return stmt.children[0], isFunccall

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





