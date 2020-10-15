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

def print_edge_eqs(CFG):
    equation_dict = {}
    for edge in CFG.edges:
        if edge.condition == "True":
            edge.condition = ""
        else:
            edge.condition = " & (" +edge.condition +")"
        if edge.dest in equation_dict:
            equation_dict[edge.dest] = equation_dict[edge.dest] + " || L" + edge.source + edge.condition
        else:
            equation_dict[edge.dest] = "L" + edge.source + edge.condition

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
    our_CFG = get_CFG("test.txt") # parse the output from Ocaml and build a CFG object
    print_edge_eqs(our_CFG) # traverse the CFG and print the contents in eqaution form
    our_DFG = get_dataflow_graph("test.txt")
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
