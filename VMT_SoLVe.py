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
        temp_edge = edge(source, dest, condition)
        self.edges.append(temp_edge)


def get_CFG(file_name):
    our_CFG = CFG()
    file_id = open(file_name, "r")
    lines = file_id.readlines()
    for line in lines:
        if "(" in line:
            # this somewhat ugly regex line simply locates the data inside the brackets, strips off the new line, and splits it into a list
            edge_data  = re.sub(r'\((.*?)\)', lambda L: L.group(1).rsplit('|', 1)[-1], line).rstrip().split(",")

            source = edge_data[0].strip() # get the first item (source)
            dest = edge_data[1].strip() # get the second item (dest)
            condition = edge_data[2].strip()
            our_CFG.add_edge(source, dest, condition)

    return our_CFG

def get_dataflow_graph(file_name):
    our_DFG = DFG()
    file_id = open(file_name, "r")
    lines = file_id.readlines()
    for line in lines:
        if "[" in line:
            # this somewhat ugly regex line simply locates the data inside the brackets, strips off the new line, and splits it into a list
            data_transfer = re.sub(r'\[(.*?)\]', lambda L: L.group(1).rsplit('|', 1)[-1], line).rstrip().split(",")

            variable = data_transfer[0].strip() # get the first item (source)
            data = data_transfer[1].strip() # get the second item (dest)
            line_number = data_transfer[2].strip()

            our_DFG.add_data_transfer(variable, data, line_number)

    return our_DFG

def print_edge_eqs(CFG): # in VMT format
    equation_set = [] # a set of sets with each subset being the set of lines for each line number.
    for edge in CFG.edges:
        equation_subset = []

        # if edge.dest in equation_dict:

        equation_subset.append("(declare-fun L" + edge.dest + " () Bool)") # def line numb as bool
        equation_subset.append("(declare-fun L" + edge.dest + "n () Bool)") # def next state as bool
        equation_subset.append("(define-fun .L" + edge.dest + "rel () Int (! L" + edge.dest + " :next L" + edge.dest +"n))") # def relation for lx and lxn
        equation_subset.append("(define-fun .L" + edge.dest + "init () Bool (! L" + edge.dest + " 0) :" + "L" + edge.dest +"init true))") # init all vars but the first to 0
        equation_subset.append("(define-fun .L" + edge.dest + "trans () Bool (! L" + edge.dest + "n (L" + edge.source + ")) :L" + edge.dest + "trans " + edge.condition + "))")

        equation_set.append(equation_subset)


    # this is a test setup using VMT for the first var and will be changed once VMT is implemented correctly.
    print("(declare-fun L1 () Bool)") # the first line
    print("(declare-fun L1n () Bool)") # the first line_next
    print("(define-fun .L1rel () Int (! L1 :next L1n))") # set the relationship
    print("(define-fun .L1init () Bool (! (= L1 1) :L1init true))")
    print("(define-fun .L1trans () Bool (! (= L1n (0)) :L1trans true))") # this line make be wrong no reference to L1 used. "(define-fun .trans () Bool (! (= xn (+ x 1)) :trans true))"

    for eq_subset in equation_set:
        for eq in eq_subset:
            print(eq)
        #print("L" + eq + "+" + " = " + equation_dict[eq])

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
    our_CFG = get_CFG("test.txt") # parse the output from Ocaml and build a CFG object
    print_edge_eqs(our_CFG) # traverse the CFG and print the contents in eqaution form
    # our_DFG = get_dataflow_graph("test.txt")
    # print_data_eqs(our_DFG)


if __name__ == '__main__':
    main()

"""
TODO:
1. Add handling for data
2. Clean up the output from Ocaml so we can parse cleanly
3. Test more complex source code
4. Handle functions
"""
