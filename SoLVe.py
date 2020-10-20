import re #regex for parsing

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

class fun_decl():
    def __init__(self, func_name, func_type, formal_param_list):
        self.func_name = func_name
        self.func_type = func_type
        self.formal_param_list = formal_param_list

class fun_call():
    def __init__(self, func_name, call_line, lhs, actual_args, param_assign):
        self.func_name = func_name
        self.line = call_line
        self.lhs = lhs # the value assigned after the function, may be None
        self.actual_args = actual_args
        self.param_assign = param_assign

class DFG():
    def __init__(self):
        self.data_transfer_list = []

    def add_data_transfer(self, variable, data, line_number):
        temp_data_transfer = data_transfer(variable, data, line_number)
        self.data_transfer_list.append(temp_data_transfer)

class CFG():
    def __init__(self):
        self.vertices = []
        self.edges = []

    def add_edge(self, source, dest, condition):
        self.edges.append(edge(source, dest, condition))

current_line_numb = 0 # global for line numbs
func_decl_list = [] # globals for c program parameters
func_call_list = []
our_CFG = CFG()
our_DFG = DFG()

def process_cil_output(file_name):
    file_id = open(file_name, "r")
    lines = file_id.readlines()
    final_line_numb = len(lines)
    global current_line_numb
    global func_decl_list # globals for c program parameters
    global func_call_list
    global our_CFG
    global our_DFG

    while current_line_numb < final_line_numb: # globally set to 0 before this loop
        line = lines[current_line_numb]

        if line.startswith('Function dec: '):
            func_decl = get_function_decls(lines[current_line_numb:])
            func_decl_list.append(func_decl)

        if line.startswith("FUNCTION CALL BEGIN"):
            current_line_numb = current_line_numb + 1
            func_call = get_call_CFG(lines[current_line_numb:], True)
            func_call_list.append(func_call)

        if line.startswith("("):# and line.endswith(")"):
            get_edge(lines[current_line_numb])

        if line.startswith("["):# and line.endswith("]"):
            get_data_edge(lines[current_line_numb])
        current_line_numb = current_line_numb + 1


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
            current_line_numb = current_line_numb - 1
            return


def get_call_CFG(lines, verbose):

    global current_line_numb
    global our_DFG
    func_call_list = []
    for line_numb, line in enumerate(lines):
        current_line_numb = current_line_numb + 1
        # print(line)
        if "FUNCTION CALL BEGIN" in line: #TEST ME
            get_call_CFG(lines[line_numb:], True)
            continue

        if "FUNCTION CALL END" in line:
            return

        if line.startswith('Name: '):
            func_call = fun_call(None, None, None, [], [])
            func_call.func_name = line[len("Name: "):].strip()
            continue

        if line.startswith('Call Line: '):
            func_call.line = line[len("Call Line: "):].strip()
            continue

        if line.startswith('LHS: '):
            func_call.lhs = line[len("LHS: "):].strip()
            continue

        if line.startswith('Actual args: '):
            func_call.actual_args = line[len("Actual args: "):].strip().replace("(", '').replace(")", '').strip().split(" ") # use re.
            continue

        if line.startswith('Param_assign: '):
            param_str = line[len("Param_assign: "):].strip()
            # re.search(r'\((.*?)\)',param_str).group(1)
            param_list = re.findall(r'\((.*?)\)',param_str)
            for param_set in param_list:
                param_pair = param_set.split(" ")
                func_call.param_assign.append(param_pair)
            func_call_list.append(func_call)
            for para_assignment_pair in func_call.param_assign:
                formal = para_assignment_pair[0]
                actual = para_assignment_pair[1]
                print(formal + " actual = "+ actual)
                our_DFG.add_data_transfer(formal, actual, func_call.line)
            continue

        if line.startswith("("):# and #line.endswith(")"):
            get_edge(line)

        if line.startswith("["):# and line.endswith("]"):
            get_data_edge(line)


    # for func_call in func_call_list:
        # print(func_call.func_name)
        # print(func_call.line)
        # print(func_call.lhs)
        # print(func_call.actual_args)
        # print(func_call.param_assign)
    return #func_call_list

def get_edge(line):
    global our_CFG
    # this somewhat ugly regex line simply locates the data inside the brackets, strips off the new line, and splits it into a list
    edge_data  = re.sub(r'\((.*?)\)', lambda L: L.group(1).rsplit('|', 1)[-1], line).rstrip().split(",")
    source = edge_data[0].strip() # get the first item (source)
    dest =   edge_data[1].strip() # get the second item (dest)
    condition = edge_data[2].strip()
    our_CFG.add_edge(source, dest, condition)
    return

def get_data_edge(line):

    global our_DFG
    # this somewhat ugly regex line simply locates the data inside the brackets, strips off the new line, and splits it into a list
    data_transfer = re.sub(r'\[(.*?)\]', lambda L: L.group(1).rsplit('|', 1)[-1], line).rstrip().split(",")

    variable = data_transfer[0].strip() # get the first item (source)
    data = data_transfer[1].strip() # get the second item (dest)
    line_number = data_transfer[2].strip()

    our_DFG.add_data_transfer(variable, data, line_number)
    return

def print_edge_eqs(CFG):
    equation_dict = {}
    for edge in CFG.edges:
        if edge.dest in equation_dict:
            equation_dict[edge.dest] = equation_dict[edge.dest] + " || L" + edge.source + " & (" +edge.condition +")"
        else:
            equation_dict[edge.dest] = "L" + edge.source + " & (" +edge.condition +")"

    print("L1+ = 0") # probably don't need this, but helps us read for now.
    for eq in equation_dict:
        print("L" + eq + "+" + " = " + equation_dict[eq])

def print_data_eqs(DFG):
    equation_dict = {}
    location_var_dict = {}
    for data_transfer in DFG.data_transfer_list:
        var = data_transfer.variable
        location = data_transfer.line_number
        value = data_transfer.data

        # L2 --> i+ = i + 2
        # L3 --> i+ = i + 5
        # !L2 & !L3 --> i+ = i
        equation_dict[location] = "L" + location + " --> " + var + "+ = " +  value

        if var in location_var_dict:
            location_var_dict[var].append(location)
        else:
            location_var_dict[var] = [location]

        # if var in equation_dict:
        #     equation_dict[var] = equation_dict[var]+ " || "+ "L" + location + " & value = " +  value
        # else:
        #     equation_dict[var] = var + "+ = " + "L" + location + " & value = " +  value

    for eq in equation_dict:
        print(equation_dict[eq])
    #print(location_var_dict)
    for var in location_var_dict:
                # !L2 & !L3 --> i+ = i
        loc_str = ""
        for location in location_var_dict[var]:
            loc_str = loc_str + "!L" + location + " & "

        loc_str = loc_str[:-3] + " --> " + var + "+ = " + var
        print(loc_str)



def main():
    global our_CFG
    global our_DFG
    process_cil_output("gold.txt")
    print_edge_eqs(our_CFG) # traverse the CFG and print the contents in eqaution form
    print_data_eqs(our_DFG)

if __name__ == '__main__':
    main()

"""
TODO:
1. Add handling for data
2. Clean up the output from Ocaml so we can parse cleanly
3. Test more complex source code
4. Handle functions
"""
