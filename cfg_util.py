import re #regex for parsing
from graphviz import Digraph

class node():
    def __init__(self, node_numb, label_list, func):
        self.node_numb = node_numb
        self.label_list = label_list
        self.edges = []
        self.succs = []
        self.preds = []
        self.func = func
        self.call_signature = ""

class edge():
    def __init__(self, source, dest, condition):
        self.source = source
        self.dest = dest
        self.condition = condition

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
        self.edges = []
        self.num_of_nodes = 0
        self.node_dict = {}

    def add_edge(self, source, dest, condition):
        if source not in self.node_dict:
            self.add_node(source, "", "")
        if dest not in self.node_dict:
            self.add_node(dest, "", "")

        self.node_dict[source].edges.append(edge(source, dest, condition))
        self.node_dict[source].succs.append(dest)
        self.node_dict[dest].preds.append(source)

    def add_existing_node(self, existing_node):
        self.node_dict[existing_node.node_numb] = existing_node

    def add_node(self, node_numb, lbl, func):
        if node_numb in self.node_dict:
            self.node_dict[node_numb].label_list.append(lbl)
        else:
            self.num_of_nodes += 1
            self.node_dict[node_numb] = node(node_numb, [lbl], func)

    def get_node(self, this_node):
        self.node_dict[this_node]

    def succ(self, node):
        succ_list = []
        for edge in self.edges:
            if node == edge.source:
                succ_list.append(self.get_node(edge.dest))
        return succ_list

    def pred(self, node):
        pred_list = []
        for edge in self.edges:
            if node == edge.dest:
                pred_list.append(self.get_node(edge.source))
        return pred_list


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
    final_line_numb = len(lines)
    global full_func_dict
    global current_line_numb
    global func_call_list
    global our_CFG

    first_line = lines[0]
    get_call_CFG(lines, "Main")


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
        if "FUNCTION CALL BEGIN: " in line: #TEST ME
            call_data = [x.group() for x in re.finditer( r'\[(.*?)\]', line)]
            for data in call_data:
                if "Name: " in data: # extract the function name
                    func_call.func_name = data[len("[Name: "): -1].strip() #remove the "[Name: x]" and extract x
                    continue

                if "Call Line: " in data:
                    func_call.line = data[len("[Call Line: "):-1].strip()
                    continue

                if "LHS: " in data:
                    func_call.lhs = data[len("[LHS: "):-1].strip()
                    get_data_edge("[" + func_call.func_name + ", " + func_call.lhs + ", " + func_call.line + "]", current_full_func)
            continue

        if "Call ends:" in line:
            full_func_dict[get_sig(current_full_func.name, current_full_func.formal_param_list)] = current_full_func
            return


        if line.startswith('Return: '):
            get_data_edge(line[len('Return: '):], current_full_func, True)
            continue

        if line.startswith('Param_assign: '):
            param_str = line[len("Param_assign: "):].strip()
            param_list = re.findall(r'\((.*?)\)',param_str)
            for param_set in param_list:
                param_pair = param_set.split(" ")
                func_call.param_assign.append(param_pair)
            for para_assignment_pair in func_call.param_assign:
                actual = para_assignment_pair[0]
                # func_call.actual = actual
                formal = para_assignment_pair[1]
                func_call.formal_param_list.append(formal)

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

    return #func_call_list




def add_func_call(current_full_func, func_signature, lhs, call_line, param_assign_list):
    global our_CFG

    for param_pair in param_assign_list: # assign out the formals to the actuals
        current_full_func.CFG.add_node(call_line, [param_pair[1], "=", param_pair[0]], current_full_func.name)
        our_CFG.add_node(call_line, [param_pair[1], "=", param_pair[0]], current_full_func.name)

    # add the function = lhs assignment # done elsewhere maybe move here
    # current_full_func.CFG.add_node(call_line, [current_full_func.name, "=", lhs], current_full_func.name)

    current_node = current_full_func.CFG.node_dict[call_line]

    current_node.call_signature = func_signature

    our_current_node = our_CFG.node_dict[call_line]

    our_current_node.call_signature = func_signature



def get_edge(line, current_full_func, entry=False):
    global our_CFG
    # this somewhat ugly regex line simply locates the data inside the brackets, strips off the new line, and splits it into a list
    edge_data  = re.sub(r'\((.*?)\)', lambda L: L.group(1).rsplit('|', 1)[-1], line).rstrip().split(",")
    source = edge_data[0].strip() # get the first item (source)
    dest =   edge_data[1].strip() # get the second item (dest)
    condition = edge_data[2].strip()
    our_CFG.add_edge(source, dest, condition)
    our_CFG.add_node(source, ["L" + source], current_full_func.name)
    current_full_func.CFG.add_edge(source, dest, condition)
    current_full_func.CFG.add_node(source, ["L" + source], current_full_func.name)
    if entry:
        current_full_func.entry_node = source
    return


#change me to add node
def get_data_edge(line, current_full_func, return_bool=False):# optional return or call variable

    # this somewhat ugly regex line simply locates the data inside the brackets, strips off the new line, and splits it into a list
    data_transfer = re.sub(r'\[(.*?)\]', lambda L: L.group(1).rsplit('|', 1)[-1], line).rstrip().split(",")

    variable = data_transfer[0].strip() # get the first item (source)
    data = data_transfer[1].strip() # get the second item (dest)
    line_number = data_transfer[2].strip()

    our_CFG.add_node(line_number, [variable, "=", data], current_full_func.name)

    current_full_func.CFG.add_node(line_number, [variable, "=", data], current_full_func.name)

    if (return_bool):
        current_full_func.return_list.append(our_CFG.node_dict[line_number])

    return



file_CFG = CFG()

def insert_wait_node(call_node, entry_function, called_function):
    global our_CFG
    entry_node = called_function.CFG.node_dict[called_function.entry_node]
    wait_node_name = "W" + call_node.node_numb
    return_node_name = "R" + call_node.node_numb

    file_CFG.add_node(wait_node_name, [wait_node_name], entry_function.name) # add each node
    file_CFG.add_node(return_node_name, [return_node_name], entry_function.name) # add each node

    self_edge_cond = "!(L"
    for return_node in called_function.return_list:
        self_edge_cond += return_node.node_numb + " & "
    self_edge_cond = self_edge_cond[:-3] +")"
    file_CFG.add_edge(wait_node_name, return_node_name, self_edge_cond[1:]) # add the edge from the call node

    for edge in call_node.edges:
        file_CFG.add_edge(return_node_name, edge.dest, edge.condition) # add the edge from the call node
        edge.dest = wait_node_name

    file_CFG.add_edge(wait_node_name, wait_node_name, self_edge_cond) # add the edge from the call node


def build_file_CFG(entry_function):
    global file_CFG

    for node in entry_function.CFG.node_dict.values():
        file_CFG.add_existing_node(node) # add each node

        if node.call_signature != "": # if theres a function call
            called_function = full_func_dict[node.call_signature]
            entry_node = called_function.CFG.node_dict[called_function.entry_node]

            insert_wait_node(node, entry_function, called_function)
            file_CFG.add_edge(node.node_numb, entry_node.node_numb, "True") # add the edge from the call node

            build_file_CFG(called_function)
    return file_CFG


def get_file_CFG(file_name):
    global full_func_dict

    process_cil_output(file_name)
    entry_function = full_func_dict["Main "]

    return build_file_CFG(entry_function)

def display_CFG(CFG_to_display, name):
    graph = Digraph(comment=name)
    global func_call_list

    for node_numb in CFG_to_display.node_dict:
        lbl_str = ""
        node = CFG_to_display.node_dict[node_numb]
        for edge in node.edges:
            if edge.condition == "True":
                edge.condition = ""
            graph.edge(edge.source, edge.dest, label = edge.condition)

        for lbl_set in node.label_list:
            for lbl in lbl_set:
                lbl_str += str(lbl)
            lbl_str += "\n"

        graph.node(node.node_numb, label=lbl_str)

    file_name =  name+".gv"
    graph.render(file_name, view=True)
