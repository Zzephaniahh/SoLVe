from cfg_util import *

def remove_redundant_nodes(CFG):
    nodes_2_rm = []
    for node in CFG.node_dict.values():
        if  (len(node.preds) == 1) and (len(node.succs) == 1):
            if node.node_numb == 'L223S126':
                import pdb; pdb.set_trace()
            pred_node = node.preds[0]
            pred = CFG.node_dict[pred_node]
            succ_node = node.succs[0]
            succ = CFG.node_dict[succ_node]
            if node.node_numb in CFG.input_variables:
                continue
            if not (len(node.expressions) == 0 == len(succ.expressions)):
                continue
            if succ == node: # selfloop
                continue
            for pred_edge in pred.edges:
                if pred_edge.dest == node.node_numb:
                    pred.edges.append(edge(pred.node_numb, succ.node_numb, pred_edge.condition))
                    pred.edges.remove(pred_edge)
                    pred.succs.remove(node.node_numb)
                    pred.succs.append(succ.node_numb)
                    for data_assignment in node.expressions:
                        pred.expressions.append(data_assignment)
                    nodes_2_rm.append(node.node_numb)

        # succ = CFG.node_dict[node.succs[0]]

        # if (len(node.succs) == 1) and (len(succ.expressions) == len(node.expressions) == 0) and ((len(node.preds) == 1)): # if there is only a single unconditional path
            # if succ == node: # selfloop
            #     continue
    #
            # for data_assignment in node.expressions:
            #     succ.expressions.append(data_assignment)

            # for pred_name in node.preds:
            #     pred = CFG.node_dict[pred_name]
            #     for edge in pred.edges:
            #         if edge.dest == node.node_numb:
            #             edge.dest = succ.node_numb
            #
            #     for edge in node.edges:
            #         if edge.source == node.node_numb:
            #             edge.source = succ.node_numb
            # CFG.update_succ_and_pred(succ)
            # CFG.update_succ_and_pred(pred)
            # nodes_2_rm[succ.node_numb] = True
            # # import pdb; pdb.set_trace()
            # if succ.node_numb in CFG.property_locations:
            #     CFG.property_locations = [node.node_numb]

    #         node.succs = succ.succs
    #         node.edges = []
    #         for edge in succ.edges:
    #             if edge.source == edge.dest:
    #                 break
    #             # import pdb; pdb.set_trace()
    #             if edge.source == succ.node_numb:
    #                 edge.source = node.node_numb
    #
    #             if edge.dest == succ.node_numb:
    #                 edge.dest = edge.dest
    #             node.edges.append(edge)
    #         succ.succs = []
    #         # succ.edges = []
    #         nodes_2_rm[node.node_numb] = True
    #
    #
    #         # import pdb; pdb.set_trace()
    for node_numb in nodes_2_rm:
            del CFG.node_dict[node_numb]

    return CFG

def remove_isolated_nodes(CFG):
    nodes_2_rm = []
    for node in CFG.node_dict.values():
        # if node.node_numb == 'L4S0':
        #     import pdb; pdb.set_trace()
        if (len(node.preds) == 1) and (len(node.succs) == 1):
            pred = node.preds[0]
            succ = node.succs[0]

            if succ == pred == node.node_numb:
                nodes_2_rm.append(node.node_numb)


    for node_numb in nodes_2_rm:
            del CFG.node_dict[node_numb]
    return CFG
