class node():
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression # data assignments
        self.edges = [] # all edges coming in or exiting the node
        self.preds = [] # preds/succs are added via edges
        self.succs = []

class edge():
     def __init__(self, source, dest, condition):
        self.source = source 
        self.dest = dest
        self.condition = condition

class CFG:
    def __init__(self):
        self.node_dict = {}
        self.property = "L5" 


def build_CFG(edge_list, node_expression_list):
    example_CFG = CFG()

    for node_name, expression in node_expression_list:
        current_node = node(node_name, expression)
        example_CFG.node_dict[node_name] = current_node

    for source, dest, condition in edge_list:
        source_node = example_CFG.node_dict[source]
        dest_node = example_CFG.node_dict[dest]
        # add edges
        source_node.edges.append([source, dest, condition])
        dest_node.edges.append([source, dest, condition])
        # add succs/preds
        source_node.succs.append(dest)
        dest_node.preds.append(source)

    return example_CFG

def sliced_PDR(example_CFG):
    PDR_termination_condition = 4 # faking this out
    P = example_CFG.property
    P_node = example_CFG.node_dict[P]
    current_node = P_node
    while(PDR_termination_condition):
        for source, dest, condition in current_node.edges:
            if current_node.name == dest:
                t_slice = '(' + source + ' & ' + condition + ')'
                print(t_slice)
        current_node = example_CFG.node_dict[source]


        PDR_termination_condition = PDR_termination_condition - 1



def main():
   
    # list of lists containing edges formatted as: [source, dest, condition]
    edge_list = [
    ['L0', 'L1', 'True'],
    ['L1', 'L2', '(i<7)'],
    ['L1', 'L5', '!(i<7)'],
    ['L2', 'L3', 'True'],
    ['L3', 'L4', '!(i<5)'],
    ['L3', 'L1', '(i<5)']
    ]

    # list of lists containing expressions formatted as: [node, expression]
    node_expression_list = [
    ['L0', 'i = 0'],
    ['L1', ''],
    ['L2', 'i = i + 2'],
    ['L3', ''],
    ['L4', ''],
    ['L5', '']
    ]
    example_CFG = build_CFG(edge_list, node_expression_list)
    sliced_PDR(example_CFG)





if __name__ == '__main__':
    main()

        
