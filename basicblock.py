
class CFG:
    def __init__(self):
        self.block_dict = []

    def add_block(self, basicblock):
        self.block_dict.append(basicblock)

    def get_block(self, block_name, block_cond):
        for block in self.block_dict:
            if block.name == block_name and block.cond == block_cond:
                return block
        return None

    def print_cfg(self):
        for block in self.block_dict:
            block.print()

    def print_cfg_md(self):
        for block in self.block_dict:
            block.print_markdown()

    def get_block(self, block_name):
        for block in self.block_dict:
            if block.name == block_name:
                return block
        return None

    def print_args(self):
        for block in self.block_dict:
            if block.is_function_define:
                print(block.func.name, block.func.args)

class BasicBlock:
    def __init__(self, name='', cond='', func='', parent_class='', operations=None, succ_block=None, prev_block=None, var=None, is_function_define=False):
        if var is None:
            var = []
        if prev_block is None:
            prev_block = []
        if succ_block is None:
            succ_block = []
        if operations is None:
            operations = []
        self.name = name
        self.cond = cond
        self.operations = operations
        self.succ_block = succ_block
        self.prev_block = prev_block
        self.var = var
        self.func = func
        self.parent_class = parent_class
        self.is_function_define = is_function_define
        self.returned = False

    def add_pre_basic_block(self, prevbb):
        self.prev_block.append(prevbb.name)

    def add_succ_basic_block(self, succbb, cond):
        print('succbb added', self.name, ' --> ', succbb.name)
        self.succ_block.append((succbb.name, cond))

    def add_operation(self, operation):
        self.operations.append(operation)

    def add_instr_begin(self, operation):
        self.operations.insert(0, operation)

    def empty(self):
        return len(self.operations) == 0

    def print(self):
        print('name = ',self.name)
        print('cond = ',self.cond)
        print('prev:')
        for prevbb in self.prev_block:
            print(prevbb)
        print('operations: ')
        for operation in self.operations:
            print(operation.pretty())
        print('succ:')
        for succbb in self.succ_block:
            print(succbb)

    def print_markdown(self):
        for succbb in self.succ_block:
            print(self.markdown_name(self.name), '-->', self.markdown_name(succbb[0]))

    def markdown_name(self, name):
        md_name = ''
        for i in range(len(name)):
            if 'a' <= name[i] <= 'z':
                md_name += name[i]
            elif 'A' <= name[i] <= 'Z':
                md_name += name[i]
            elif '0' <= name[i] <= '9':
                md_name += name[i]
            elif name[i] == '_':
                md_name += name[i]
        return md_name
