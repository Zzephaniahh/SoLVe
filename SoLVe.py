import re #regex for parsing
import sys
from graphviz import Digraph

class node():
    def __init__(self, node_numb, label_list, func):
        self.node_numb = node_numb
        self.label_list = label_list
        self.edges = []
        self.succs = []
        self.preds = []
        self.func = func

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
        self.actual_args = actual_args
        self.param_assign = param_assign
        self.nodes = []

# class DFG():
#     def __init__(self):
#         self.data_transfer_list = []
#
#     def add_data_transfer(self, variable, data, line_number):
#         temp_data_transfer = data_transfer(variable, data, line_number)
#         self.data_transfer_list.append(temp_data_transfer)

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
        self.CFG = CFG()

current_line_numb = 0 # global for line numbs
# func_decl_list = [] # globals for c program parameters
func_call_list = []
full_func_list = []
our_CFG = CFG()
# our_DFG = DFG()


def process_cil_output(file_name):
    file_id = open(file_name, "r")
    lines = file_id.readlines()
    final_line_numb = len(lines)

    global current_line_numb
    # global func_decl_list # globals for c program parameters
    global func_call_list
    global our_CFG
    # global our_DFG

    first_line = lines[0]
    if first_line.startswith("FUNCTION CALL BEGIN"):
        get_call_CFG(lines, "Main")



def get_call_CFG(lines, func_name): # recursive function
    current_full_func = full_func()
    current_full_func.name = func_name
    global func_call_list
    global full_func_list
    global current_line_numb
    global our_CFG
    # global our_DFG
    final_line_numb = len(lines)
    func_call = fun_call(None, None, None, [], [])
    while current_line_numb < final_line_numb:
        line = lines[current_line_numb]
        current_line_numb = current_line_numb + 1
        print(str(current_line_numb) + line )
        if "FUNCTION CALL BEGIN" in line: #TEST ME
            lines = get_call_CFG(lines, func_name)
            continue

        if "call ends:" in line:
            full_func_list.append(current_full_func)
            return lines

        if line.startswith('Name: '):
            func_call = fun_call(None, None, None, [], [])
            func_call.func_name = line[len("Name: "):].strip()
            current_full_func.name = func_call.func_name
            continue

        if line.startswith('Call Line: '):
            func_call.line = line[len("Call Line: "):].strip()
            continue

        if line.startswith('LHS: '):

            func_call.lhs = line[len("LHS: "):].strip()
            continue

        if line.startswith('Param_assign: '):
            param_str = line[len("Param_assign: "):].strip()
            # re.search(r'\((.*?)\)',param_str).group(1)
            param_list = re.findall(r'\((.*?)\)',param_str)
            for param_set in param_list:
                param_pair = param_set.split(" ")
                func_call.param_assign.append(param_pair)
            for para_assignment_pair in func_call.param_assign:
                actual = para_assignment_pair[0]
                formal = para_assignment_pair[1]
                current_full_func.formal_param_list.append(formal)
                # our_DFG.add_data_transfer(formal, actual, func_call.line)
            func_call_list.append(func_call)
            # for func_call in func_call_list:
            #     print(func_call.func_name)
            #     print(func_call.line)
            #     print(func_call.lhs)
            #     print(func_call.param_assign)
            continue

        if line.startswith("("):# and #line.endswith(")"):
            get_edge(line, current_full_func)

        if line.startswith("["):# and line.endswith("]"):
            get_data_edge(line, current_full_func)


    # for func_call in func_call_list:
    #     print(func_call.func_name)
    #     print(func_call.line)
    #     print(func_call.lhs)
    #     print(func_call.param_assign)
    return #func_call_list

def get_edge(line, current_full_func):
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
    return

def get_data_edge(line, current_full_func):

    # global our_DFG
    # this somewhat ugly regex line simply locates the data inside the brackets, strips off the new line, and splits it into a list
    data_transfer = re.sub(r'\[(.*?)\]', lambda L: L.group(1).rsplit('|', 1)[-1], line).rstrip().split(",")

    variable = data_transfer[0].strip() # get the first item (source)
    data = data_transfer[1].strip() # get the second item (dest)
    line_number = data_transfer[2].strip()

    # our_DFG.add_data_transfer(variable, data, line_number)
    our_CFG.add_node(line_number, [variable, "=", data], current_full_func.name)

    current_full_func.CFG.add_node(line_number, [variable, "=", data], current_full_func.name)

    # for node in our_CFG.nodes:
    #     if line_number == node.node_numb:
    #         lbl = str(variable) + " = " + str(data)
    #         our_CFG.add_node(line_number, lbl)
    return

def print_edge_eqs(CFG):
    equation_dict = {}
    for edge in CFG.edges:
        if edge.condition == "True":
            edge.condition = ""
        else:
            edge.condition = " & (" + edge.condition + ")"

        if edge.dest in equation_dict:
            equation_dict[edge.dest] = equation_dict[edge.dest] + " || L" + edge.source + edge.condition
        else:
            equation_dict[edge.dest] = "L" + edge.source + edge.condition

    print("L1+ = 0") # probably don't need this, but helps us read for now.
    for eq in equation_dict:
        print("L" + eq + "+" + " = " + equation_dict[eq])

# def print_data_eqs(): #DFG
#     equation_dict = {}
#     location_var_dict = {}
#     for data_transfer in DFG.data_transfer_list:
#         var = data_transfer.variable
#         location = data_transfer.line_number
#         value = data_transfer.data

        # L2 --> i+ = i + 2
        # L3 --> i+ = i + 5
        # !L2 & !L3 --> i+ = i
        # equation_dict[location] = "L" + location + " --> " + var + "+ = " +  value
    #
    #     if var in location_var_dict:
    #         location_var_dict[var].append(location)
    #     else:
    #         location_var_dict[var] = [location]
    #
    #     # if var in equation_dict:
    #     #     equation_dict[var] = equation_dict[var]+ " || "+ "L" + location + " & value = " +  value
    #     # else:
    #     #     equation_dict[var] = var + "+ = " + "L" + location + " & value = " +  value
    #
    # for eq in equation_dict:
    #     print(equation_dict[eq])
    # #print(location_var_dict)
    # for var in location_var_dict:
    #             # !L2 & !L3 --> i+ = i
    #     loc_str = ""
    #     for location in location_var_dict[var]:
    #         loc_str = loc_str + "!L" + location + " & "
    #
    #     loc_str = loc_str[:-3] + " --> " + var + "+ = " + var
    #     print(loc_str)

def generate_dot(our_CFG, name):
    graph = Digraph(comment=name)
    # global our_CFG
    # global our_DFG
    global func_call_list

    # for fun_call in func_call_list:
        # print(fun_call.func_name)
    # fun_call = func_call_list[1]
    # our_CFG.add_node("w" + str(fun_call.line), ["w" + str(fun_call.line)], "")
    # our_CFG.add_node("r" + str(fun_call.line), ["r" + str(fun_call.line)], "")
    #
    # our_CFG.add_edge("w" + str(fun_call.line), "w" + str(fun_call.line), "!L7")
    # our_CFG.add_edge("w" + str(fun_call.line), "r" + str(fun_call.line), "L7")

    # call_node = our_CFG.node_dict[fun_call.line]
    # for pred in call_node.preds:
    #     pred_node = CFG.node_dict[pred]
    #     for i, edge in enumerate(pred_node.edges):
    #         if edge.dest == fun_call.line:
    #             # pred_node.edges[i] = edge(pred_node.node_numb, "w" + str(fun_call.line), edge.condition)
    #             edge.dest = "w" + str(fun_call.line)
    #             edge.source = pred_node.node_numb
                # our_CFG.add_edge(
        # """
        # insert w and r nodes
        # add edges for w and r
        # """

    #
    #     our_CFG.add_node(node_numb, lbl)
    #     pred_list = our_CFG.pred(fun_call.line)
    #     for pred in pred_list:
    #         our_CFG.add_edge("w"+str(fun_call.line), dest, condition)
    #
    #     succ_list = our_CFG.succ(fun_call.line)


    for node_numb in our_CFG.node_dict:
        lbl_str = ""
        node = our_CFG.node_dict[node_numb]
        for edge in node.edges:
            if edge.condition == "True":
                edge.condition = ""
            graph.edge(edge.source, edge.dest, label = edge.condition)

        for lbl_set in node.label_list:
            for lbl in lbl_set:
                lbl_str += str(lbl)
            lbl_str += "\n"

        graph.node(node.node_numb, label=lbl_str)

        # lbl = "L" + edge.source

        # our_CFG.add_node(data_transfer.line_number, lbl)
        # graph.node(edge.source, label=lbl)

    # for data_transfer in our_DFG.data_transfer_list:
    #     if data_transfer.line_number in node_lbl_dict:
    #         node_lbl_dict[data_transfer.line_number] += data_transfer.variable + " = " + data_transfer.data +"\n"
    #     else:
    #         node_lbl_dict[data_transfer.line_number] = "L" + data_transfer.line_number  + "\n" + data_transfer.variable + " = " + data_transfer.data +"\n"
    #
    #     lbl = node_lbl_dict[data_transfer.line_number]
    #     our_CFG.add_node(self, data_transfer.line_number, lbl):
        # graph.node(data_transfer.line_number, label=lbl)

        # self.func_name = func_name
        # self.line = call_line
        # self.lhs = lhs # the value assigned after the function, may be None
        # self.actual_args = actual_args
        # self.param_assign = param_assign





    graph.render('round-table.gv', view=True)

def main():
    global our_CFG
    # global our_DFG

    process_cil_output(sys.argv[1])
    print_edge_eqs(our_CFG) # traverse the CFG and print the contents in eqaution form
    # print_data_eqs(our_DFG)
    this_cfg = full_func_list[2].CFG
    generate_dot(this_cfg, full_func_list[0].name)
    for function in full_func_list:
        print(function.name)

if __name__ == '__main__':
    main()

"""
TODO:
1. Add handling for data
2. Clean up the output from Ocaml so we can parse cleanly
3. Test more complex source code
4. Handle functions
"""















def get_function_decls(lines):
    global current_line_numb

    for line in lines:
        current_line_numb = current_line_numb + 1
        if line.startswith('Function dec: '): # get names
            func_decl = fun_decl(None, None, [])
            func_decl.func_name = line[len("Function dec: "):].strip()
        #CHECK ME WITH VOID/NO ARGS
        if line.startswith('Type: '): # get formal args and type
            args_type_str = line[len("Type: "):]
            func_decl.func_type = re.search(r"(.*?)\(", args_type_str).group(0)[:-1].strip()
            args_str = args_type_str[len(func_decl.func_type):].strip()

            args  = re.sub(r'\((.*?)\)', lambda L: L.group(1).rsplit('|', 1)[-1], args_str).rstrip().split(",")
            for index, arg in enumerate(args):
                arg = arg.strip() #clears spaces
                arg_and_type = arg.split(" ")
                func_decl.formal_param_list.append(arg_and_type)
            func_decl_list.append(func_decl)

            # if verbose == True:

            # print(func_decl.func_name)
            # print(func_decl.func_type)
            # print(func_decl.formal_param_list)
            current_line_numb = current_line_numb + 1
            return
