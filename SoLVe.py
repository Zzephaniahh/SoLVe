import re #regex for parsing

class edge():
    def __init__(self, source, dest, condition):
        self.source = source
        self.dest = dest
        self.condition = condition


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
        if "to" in line:
            node_sub_str = re.search('.*on', line).group(0)[:-3] # somewhat hacky captures only the edge, need to fix on ocaml I think FIXME
            temp_source_dest_set = re.search('.*(\d+).*(\d+)', node_sub_str) # get the integer line numbers for source/dest
            source = temp_source_dest_set.group(1) # get the first item (source)
            dest = temp_source_dest_set.group(2) # get the second item (dest)
            m = re.search('on.*', line) # search the string for the condition
            condition = m.group(0)[3:] #hacky [3:] to remove the "on ", will clean up later FIXME
            our_CFG.add_edge(source, dest, condition)

    return our_CFG

def get_dataflow_graph(file_name):
    our_CFG = CFG()
    file_id = open(file_name, "r")
    lines = file_id.readlines()
    for line in lines:
        if "Data Transfers" in line:
            node_sub_str = re.search('.*on', line).group(0)[:-3] # somewhat hacky captures only the edge, need to fix on ocaml I think FIXME
            print()
            temp_source_dest_set = re.search('.*(\d+).*(\d+)', node_sub_str) # get the integer line numbers for source/dest
            source = temp_source_dest_set.group(1) # get the first item (source)
            dest = temp_source_dest_set.group(2) # get the second item (dest)
            m = re.search('on.*', line) # search the string for the condition
            condition = m.group(0)[3:] #hacky [3:] to remove the "on ", will clean up later FIXME
            our_CFG.add_edge(source, dest, condition)

    return our_CFG

def print_eqs(CFG):
    equation_dict = {}
    for edge in CFG.edges:
        if edge.dest in equation_dict:
            equation_dict[edge.dest] = equation_dict[edge.dest] + " || L" + edge.source + " & (" +edge.condition +")"
        else:
            equation_dict[edge.dest] = "L" + edge.source + " & (" +edge.condition +")"

    print("L1+ = 0") # probably don't need this, but helps us read for now.
    for eq in equation_dict:
        print("L" + eq + "+" + " = " + equation_dict[eq])

def main():
    our_CFG = get_CFG("test.txt") # parse the output from Ocaml and build a CFG object
    print_eqs(our_CFG) # traverse the CFG and print the contents in eqaution form


if __name__ == '__main__':
    main()

"""
TODO:
1. Add handling for data
2. Clean up the output from Ocaml so we can parse cleanly
3. Test more complex source code
4. Handle functions
"""
