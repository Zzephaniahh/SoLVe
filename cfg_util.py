import re #regex for parsing
from graphviz import Digraph
import copy # maybe fix this, used when graphing only.

### VARIABLES ###
# A variable has a name, type, bitwidth, size, and function which it is scoped to

class data_assignment():
    def __init__(self, line_numb, lhs, exp):
        self.line_numb = line_numb
        self.lhs = lhs
        self.exp = exp

class variable():
    def __init__(self, name, type, bitwidth, function, int_type=''):
        self.type = type
        self.name = name
        self.function_scope = function
        self.size = bitwidth
        self.int_type = int_type

class input_variable(): # A primary input shown by: __VERIFIER_nondet_XXX() where 'XXX' is the type
    def __init__(self, name, type, bitwidth, function, location):
        self.type = type
        self.name = name
        self.function_scope = function
        self.size = bitwidth
        self.location = location

# class expr(): # Old deprecate ASAP
#     def __init__(self, exp_str, rhs, operator, lhs, negate):
#         self.exp_str = exp_str # for an exp: (i > 7) --> 'int 32 i > 7'
#         self.rhs = rhs # type: variable with size and type information
#         self.rhs = lhs # type: variable with size and type information
#         self.operator = operator # < > <= = etc.
#         self.negate = negate # this bool is True if the equation is negated (if ! in string)

### EXPRESSIONS ###
# An expression str has three elements and usually looks like:
# {int 32 i > 7, int 32 i, int 32 7}
# for the exp: i > 7
# where i and 7 are 32 bit integers
# the type and size is stored in the var.type/var.size fields
class expression():
    def __init__(self, lhs, rhs, operator, negate):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator # < > <= = etc.
        self.negate = negate # this bool is True if the equation is negated (if ! in string)


### NODES ###
# Each node is a single statement from CIL and represents a node in the CFG
# It may contain some expressions, and it has an edge set represeting all edges
# leaving the node. The Pred and Succ lists are node_numbs of each pred/succ
class node():
    def __init__(self, node_numb, func):
        self.node_numb = node_numb
        self.expressions = []
        self.edges = []
        self.succs = []
        self.preds = []
        self.func = func
        self.call_signature = ""

### EDGES ###
# Each edge has a source and destination of type 'node',
# and a condition of type 'expression'
class edge():
    def __init__(self, source, dest, condition):
        self.source = source
        self.dest = dest
        self.condition = condition

### DATA_TRANSFER ###
# This is an assignment ex: S1L1: i = k + 7; becomes:
# (variable = i), (data = k + 7), (line_number = S1L1)
# where i is of type 'variable'
# and data is type 'expression'
class data_transfer():
    def __init__(self, variable, data, line_number):
        self.variable = variable
        self.data = data
        self.line_number = line_number


class fun_call():
    def __init__(self, func_name, call_line, lhs, actual_args, param_assign):
        self.func_name = func_name
        self.line = call_line
        self.lhs = lhs # the value assigned after the function, may be None
        self.actual = actual_args
        self.formal_param_list = []
        self.param_assign = param_assign


class CFG():
    def __init__(self):
        self.num_of_nodes = 0
        self.node_dict = {}
        self.property_locations = [] # defines the locations which lead to a violation
        self.file_entry_node = "" # identifies the location of 'main'
        self.input_variables = {}

    def add_edge(self, source, dest, condition):
        if source not in self.node_dict:
            self.add_node(source, "")
        if dest not in self.node_dict:
            self.add_node(dest, "")

        self.node_dict[source].edges.append(edge(source, dest, condition))
        self.node_dict[source].succs.append(dest)
        self.node_dict[dest].preds.append(source)
        # self.node_dict[dest].edges.append(edge(source, dest, condition))


    def add_existing_node(self, existing_node):
        self.node_dict[existing_node.node_numb] = existing_node

    def add_node(self, node_numb, func, exp=None):
        if node_numb not in self.node_dict:
            self.num_of_nodes += 1
            self.node_dict[node_numb] = node(node_numb, func)

        if exp != None:
            self.node_dict[node_numb].expressions.append(exp)

    def get_node(self, this_node):
        self.node_dict[this_node]


    def update_succ_and_pred(self, node):
        node.succs = []
        node.preds = []
        for edge in node.edges:
            node.succs.append(edge.dest)
            node.preds.append(edge.source)
        return node

class full_func():
    def __init__(self):
        self.name = ""
        self.type = ""
        self.formal_param_list = []
        self.func_call_list = []
        self.CFG = CFG()
        self.return_list = []
        self.signature = "" #default sig
        self.entry_node = ""
        self.local_variable_dict = {}

# Just a way to uniquely identify each function with a hashable string
def get_sig(name, formal_param_list):
    signature = name + " "
    for formal in formal_param_list:
        signature += formal + " "
    return signature

current_line_numb = 0 # global for line numbs
func_call_list = []
full_func_list = []
our_CFG = CFG()
full_func_dict = {}


def process_cil_output(file_name):
    file_id = open(file_name, "r")
    lines = file_id.readlines()
    get_call_CFG(lines, "Main") # C file entry point


def get_call_CFG(lines, func_name, formal_list = []): # recursive function
    current_full_func = full_func()
    current_full_func.name = func_name
    current_full_func.formal_param_list = formal_list
    global func_call_list
    global full_func_dict
    global current_line_numb
    global our_CFG
    entry_node = True
    final_line_numb = len(lines)
    func_call = fun_call(None, None, None, [], [])
    while current_line_numb < final_line_numb:
        line = lines[current_line_numb]
        current_line_numb = current_line_numb + 1
        if "FUNCTION CALL BEGIN: " in line:
            call_data = [x.group() for x in re.finditer( r'\[(.*?)\]', line)]
            for data in call_data:
                if "Name: " in data: # extract the function name
                    func_call.func_name = data[len("[Name: "): -1].strip() #remove the "[Name: x]" and extract x
                    continue

                if "Call Line: " in data:
                    func_call.line = data[len("[Call Line: "):-1].strip()
                    continue

                if "Return Type: " in data:
                    # find the type between "Return Type:" and "(int a , int b )" in "[Return Type: int (int a , int b )]"
                    func_call.type = data[ data.find(":")+2 : data.find("(") ]

                if "LHS: " in data:
                    func_call.lhs = data[len("[LHS: "):-1].strip()
                    # get_data_edge("[" + func_call.lhs + ", {int 32 " + func_call.func_name + "}, " + func_call.line + "]", current_full_func)
                    get_data_edge("[" + func_call.lhs + ", {" + func_call.type + " " +  func_call.func_name + "}, " + func_call.line + "]", current_full_func)

                if "[(" in data:
                    initial_edge = data[1:-1]
                    get_edge(initial_edge, current_full_func, False, True)


            continue

        if "Call ends:" in line:
            full_func_dict[get_sig(current_full_func.name, current_full_func.formal_param_list)] = current_full_func
            return

        if line.startswith('Input: '):


            get_input_var(line, current_full_func)
            #
            # property = line.split('[', 1)[1].split(']')[0] # find the !XX in the brackets for Property: [!XX]
            # file_CFG.property_locations.append("L" + property[1:]) # format as LXX and remove the !
            continue

        if line.startswith('Property: '): # collect each line with an error state (usually only one line exists)
            property = line.split('[', 1)[1].split(']')[0] # find the !XX in the brackets for Property: [!XX]
            file_CFG.property_locations.append(property[1:]) # format as LXX and remove the !

        if line.startswith('Return: '):
            # import pdb; pdb.set_trace()
            if "(" and ")" in line:
                line = line[ :line.find("(")-1 ] + line[line.find(")")+1: ] # super hacky, but removes formal params
            
            get_data_edge(line[len('Return: '):], current_full_func, True)
            continue

        if line.startswith('Param_assign: '):
            func_call.param_assign = []
            # for each expression extract the string.
            # For example
            # {int 32 i = int 32 x, int 32 i, int 32 x} {int 32 j = int 32 k, int 32 j, int 32 k}
            # Becomes:
            # [{int 32 i = int 32 x, int 32 i, int 32 x}, {int 32 j = int 32 k, int 32 j, int 32 k} ]
            param_str = line[len("Param_assign: "):].strip()
            param_list = re.findall(r"\[.*?]", param_str)

            # if param_pair is :[int 32 i, {int 32 x}]
            # we get:
            # actual = int 32 i
            # formal = {int 32 x}
            for param_pair in param_list:

                [actual_str, formal_str] = param_pair[1:-1].split(',') # [1:-1] removes brakets
                actual = build_variable(actual_str.strip(), func_call.func_name) # add a variable
                formal_exp = build_expression(formal_str, func_call.func_name) # build an expression object for each assignment
                param_data_assign = data_assignment(func_call.line, actual, formal_exp)
                func_call.param_assign.append(param_data_assign)

            func_call.formal_param_list.append(param_str) # this is now broken

            current_full_func.func_call_list.append(func_call)
            func_call_list.append(func_call)
            call_signature = get_sig(func_call.func_name, func_call.formal_param_list)
            add_func_call(current_full_func, call_signature, func_call.lhs, func_call.line, func_call.param_assign)

            if call_signature in full_func_dict:
                while ("Call ends: " + func_call.func_name) not in line:

                    # skip all lines defining a function we've already seen.
                    line = lines[current_line_numb]
                    current_line_numb = current_line_numb + 1
            else:
                get_call_CFG(lines, func_call.func_name, func_call.formal_param_list)
            continue

        if line.startswith("("):# and #line.endswith(")"):
            if entry_node:
                get_edge(line, current_full_func, entry_node)
                entry_node = False
            else: # comment me for double arrows on entry nodes
                get_edge(line, current_full_func)

        if line.startswith("["):# and line.endswith("]"):
            get_data_edge(line, current_full_func)

    return




def add_func_call(current_full_func, func_signature, lhs, call_line, param_assign_list):
    global our_CFG

    for param_pair_exp in param_assign_list: # assign out the formals to the actuals #FIXME
            # def add_node(self, node_numb, func, exp=None):

        current_full_func.CFG.add_node(call_line, current_full_func.name, param_pair_exp)
        our_CFG.add_node(call_line, current_full_func.name, param_pair_exp)

        # current_full_func.CFG.add_node(call_line, [param_pair[1], "=", param_pair[0]], current_full_func.name)
        # our_CFG.add_node(call_line, [param_pair[1], "=", param_pair[0]], current_full_func.name)

    # add the function = lhs assignment # done elsewhere maybe move here
    # current_full_func.CFG.add_node(call_line, [current_full_func.name, "=", lhs], current_full_func.name)

    current_node = current_full_func.CFG.node_dict[call_line]

    current_node.call_signature = func_signature

    our_current_node = our_CFG.node_dict[call_line]

    our_current_node.call_signature = func_signature



def get_edge(line, current_full_func, entry=False, file_entry=False):

    # this somewhat ugly regex line simply locates the data inside the brackets, strips off the new line, and splits it into a list
    edge_data  = re.sub(r'\((.*?)\)', lambda L: L.group(1).rsplit('|', 1)[-1], line).rstrip().split(",")
    if edge_data[-1].strip() == "True": # if the edge(s) are unconditional
        for i, data in enumerate(edge_data):
            if edge_data[i+1].strip() == "True":
                break # this is the end of the list
            source =  edge_data[i].strip()
            dest = edge_data[i+1].strip()
            condition = expression("","","",False)
            if source == dest:
                return
            current_full_func.CFG.add_edge(source, dest, condition)
    else:
        source =  edge_data[0].strip() # get the first item (source)
        dest =   edge_data[1].strip() # get the second item (dest)
        condition =  edge_data[2].strip().split(",")

        condition_expr_str = re.search(r"\{.*?}", line).group(0)
        if '!{' in line: # preserve the negation
            condition_expr_str = '!' + condition_expr_str

        exp = build_expression(condition_expr_str, current_full_func.name)

        condition = exp
        current_full_func.CFG.add_edge(source, dest, condition)

    if entry:
        current_full_func.entry_node = source

    if file_entry:
        current_full_func.CFG.file_entry_node = source

    return

def get_input_var(input_str, current_full_func): # input_str looks like 'Input: [L13S3] [LHS: int 32 v_in]
    # import pdb; pdb.set_trace()
    [line, var_str] = re.findall(r"\[(.*?)\]", input_str) # split into three strings
    var_str = var_str[len('LHS: '):] # for LHS: int 32 v_in  rm LHS:  and return 'int 32 v_in'
    if len(var_str.split()) == 4:
        [additonal_type, type, size, name] = var_str.split() # changes [int 32] to: type = 'int' and size = '32'
    else:
        [type, size, name] = var_str.split() # changes [int 32] to: type = 'int' and size = '32'
    input_var = input_variable(name, type, size, current_full_func.name, line)

    if name in current_full_func.CFG.input_variables:
        current_full_func.CFG.input_variables[line].append(input_var)
    else:
        current_full_func.CFG.input_variables[line] = [input_var]


def build_variable(var_str, func_name): # var string looks something like: int 32 i

    if len(var_str.split()) == 4: # short int, unsigned int, etc.
        [int_type, type, size, name] = var_str.split() # var_string ex: short int 32 i
        name = name.replace('U', '') # for unsigned remove the U placed by CIL
        var = variable(name, type, size, func_name, int_type)
    else:
        [type, size, name] = var_str.split() # var_string ex: int 32 i
        var = variable(name, type, size, func_name)
    return var

def build_expression(exp_str, func_name, lhs=None):
    if exp_str.endswith(', }'): # this is because I cannot currently print exps cleanly from Cil
        exp_str = exp_str[:-3] + '}' # changes {int 32 i > 7, int 32 i, int 32 7, } to: {int 32 i > 7, int 32 i, int 32 7}

    negate =  False
    if '!{' in exp_str:
        negate = True 
        exp_str = exp_str.replace('!{', '{') # rm the "!"

    exp_str = exp_str[1:-1] # remove the '{ }'
    exp_set = exp_str.split(',') # split into one or three elements
    # Because C has no boolean type, we need to augment to check if the value is non-zero
    if ' ! ' in exp_set[0]: # something like 'int 32 ! cond, int 32 cond'
        # Needs to become: {int 32 cond != 0, int 32 cond, int 32 0}
        exp_str = exp_set[0].replace(' !', '') # int 32 cond
        bool_check = ' != 0, ' + exp_str + ', int 32 0' # check the value against 0
        exp_str =  exp_str + bool_check
        exp_set = exp_str.split(',') # redefine to match the new bool string
    
    if len(exp_set) == 3:
        lhs = build_variable(exp_set[1].strip(), func_name) # int 32 i
        rhs = build_variable(exp_set[2].strip(), func_name) # int 32 7
    
        

        operator = exp_set[0].split()[-2].strip() # hardcoded to find '>' may not always be the 4th element, check this!
        exp = expression(lhs, rhs, operator, negate)
    else: # an assignment such as: [int 32 i, {int 32 0}, L8S1]
        
            
        rhs = build_variable(exp_str.strip(), func_name)

        operator = "=" # assignment operator
        exp = expression(lhs, rhs, operator, negate)


    return exp

#change me to add node
def get_data_edge(line, current_full_func, return_bool=False):# optional return or call variable
    if "{" and "}" in line: # this line has a conditional edge
        condition_expr_str = re.search(r"\{.*?}", line).group(0)
        line = line.replace(condition_expr_str + ',', '') # remove the expression
    # this somewhat ugly regex line simply locates the data inside the brackets, strips off the new line, and splits it into a list
    if 'None' in line: # a void function has no return value.
        void_set = re.sub(r'\[(.*?)\]', lambda L: L.group(1).rsplit('|', 1)[-1], line).rstrip().split(",")
        line_number = void_set[-1].strip()
    else:
        [lhs_str, stmt_line_number] = re.sub(r'\[(.*?)\]', lambda L: L.group(1).rsplit('|', 1)[-1], line).rstrip().split(",")
        lhs = build_variable(lhs_str.strip(), current_full_func.name) # add a variable
        exp = build_expression(condition_expr_str.strip(), current_full_func.name)
        line_number = stmt_line_number.strip() # statement number
        if ((exp.operator == '!=') or (exp.operator == '==')) and (lhs.type == 'int'):
            lhs.type = 'int2bool'
        data_assign = data_assignment(line_number, lhs, exp)
        current_full_func.CFG.add_node(line_number, current_full_func.name, data_assign)

    if (return_bool):
        current_full_func.return_list.append(current_full_func.CFG.node_dict[line_number])
    return



file_CFG = CFG()

def insert_wait_node(call_node, entry_function, called_function):
    entry_node = called_function.CFG.node_dict[called_function.entry_node]
    entry_node.preds.append(call_node.node_numb)
    wait_node_name = "W" + call_node.node_numb
    return_node_name = "R" + call_node.node_numb
    return_exp = None
    for expr in call_node.expressions:
        if expr.exp.rhs.name == called_function.name:
            return_exp = expr

    file_CFG.add_node(wait_node_name, entry_function.name) # add each node
    if return_exp == None:
        file_CFG.add_node(return_node_name, entry_function.name) # add each node
    else:
        file_CFG.add_node(return_node_name, entry_function.name, return_exp) # add each node

    self_edge_cond = "("
    for return_node in called_function.return_list:
        self_edge_cond += return_node.node_numb + " & "
    self_edge_cond = self_edge_cond[:-3] +")"

    cond = expression(self_edge_cond,"","",False)

    file_CFG.add_edge(wait_node_name, return_node_name, cond) # add the edge from the call node
    self_edge_cond = expression(self_edge_cond,"","",True)
    for edge in call_node.edges:
        file_CFG.add_edge(return_node_name, edge.dest, edge.condition) # add the edge from the call node
        edge.dest = wait_node_name

    file_CFG.add_edge(wait_node_name, wait_node_name, self_edge_cond) # add the edge from the call node


def build_file_CFG(entry_function):
    global file_CFG

    if file_CFG.file_entry_node == '': # assign these only from main()
            file_CFG.file_entry_node = entry_function.CFG.file_entry_node
            file_CFG.input_variables = entry_function.CFG.input_variables
            

    # file_CFG.input_variables = entry_function.CFG.input_variables

    for node in entry_function.CFG.node_dict.values():

        file_CFG.add_existing_node(node) # add each node
        # file_CFG.node_dict[node.node_numb].label_list.append(node.node_numb)
        if node.call_signature != "": # if theres a function call
            called_function = full_func_dict[node.call_signature]
            entry_node = called_function.CFG.node_dict[called_function.entry_node]

            insert_wait_node(node, entry_function, called_function)
            cond = expression("","","",False)
            file_CFG.add_edge(node.node_numb, entry_node.node_numb, cond) # add the edge from the call node

            build_file_CFG(called_function)

            
            
    # for bad_node_name in file_CFG.property_locations:
    #     bad_node = file_CFG.node_dict[bad_node_name]
    #     for pred in bad_node.preds:
    #         pred_node = file_CFG.node_dict[pred]
    #         if len(pred_node.succs) == 1:
    #             file_CFG.property_locations.append(pred)
    return file_CFG


def get_file_CFG(file_name):
    global full_func_dict

    process_cil_output(file_name)
    entry_function = full_func_dict["Main "]
    build_file_CFG(entry_function)
    # for bad_node_name in file_CFG.property_locations:                FIXME to bubble up property node
    #             bad_node = file_CFG.node_dict[bad_node_name]
    #             for pred in bad_node.preds:
    #                 pred_node = file_CFG.node_dict[pred]
    #                 if len(pred_node.succs) == 1:
    #                     file_CFG.property_locations.append(pred)

    return file_CFG

def display_CFG(CFG_to_display_global, name):
    CFG_to_display = copy.deepcopy(CFG_to_display_global)
    graph = Digraph(comment=name)
    global func_call_list

    for node_numb in CFG_to_display.node_dict:
        lbl_str = node_numb + "\n"
        node = CFG_to_display.node_dict[node_numb]

        for edge in node.edges:
            # try:
            if edge.condition.lhs == "": # if any of the fields are missing its an 'always' edge
                label = ""
            elif isinstance(edge.condition.lhs, str): # if it's a wait node, maybe make this more robust
                label = edge.condition.lhs
            else:
                label = edge.condition.lhs.name + edge.condition.operator + edge.condition.rhs.name
            # except:
            #     import pdb; pdb.set_trace()
            if edge.condition.negate == True:
                label = "!(" + label + ")"
            graph.edge(edge.source, edge.dest, label = label)

        if node_numb in CFG_to_display.input_variables:
            for input_variable in CFG_to_display.input_variables[node_numb]:
                lbl_str += "Unconstrained input: " + input_variable.name + "\n"

        for data_assignment in node.expressions:
            try:
                exp = data_assignment.exp

            except:
                import pdb; pdb.set_trace()

            lhs = data_assignment.lhs
            try:
                if exp.lhs == None:
                    lbl_str += lhs.name + ' = ' + exp.rhs.name
                else:
                    lbl_str += lhs.name + ' = ' + exp.lhs.name + exp.operator + exp.rhs.name
            except:
                import pdb; pdb.set_trace()
            lbl_str += "\n"

            # the [::-1] simply reverses the list so Lx is printed on top.
            # for lbl in lbl_set:
            #     if type(lbl) == type(variable("name", "type", "funct")):
            #         lbl_str += str(lbl.type + " " + lbl.name)
            #     else:
            #         lbl_str += str(lbl)
            # lbl_str += "\n"
        if node.node_numb in file_CFG.property_locations:
            graph.node(node.node_numb, label=lbl_str, color="red", style='filled')

        if node.node_numb == CFG_to_display.file_entry_node:
            graph.node(node.node_numb, label=lbl_str, color="green", style='filled')

        graph.node(node.node_numb, label=lbl_str)

    file_name =  name+".gv"
    graph.render(file_name, view=True)
