import cfg_util
from cfg_util import *

class equality_equation():
    def __init__(self, lhs):
        self.lhs = lhs # type: var
        self.terms = [] # list of lists, inner lists are ANDed, outter list are ORed
        # L4+ = [L2 & !(x < y)] || L3  --- Becomes:
        # self.lhs = L4+
        # self.terms = [[L2, !(x < y)], L3]

class implication_equation():
    def __init__(self, variable):
        self.variable = variable
        self.line_and_data_set = []


class bool_line_var():
    def __init__(self, name, type):
        self.name = name
        self.type = type

def print_readable_init(file_entry_node):
        print("# Initial state, assume all other locations are False. ")
        print(file_entry_node + " = True ")

def print_data_assignment(line, variable, data):
    print(line + "+ --> " + variable + "+ = " + data)

def print_data_preservation(variable, update_loc_list):
    no_update_str = ""
    for line in update_loc_list:
        no_update_str += "!" + line + "+ & "
    print(no_update_str[:-3] + " --> " + variable + "+ = " + variable)

def print_line_eq(eq):
    if eq.lhs.type == 'False':
        print(eq.lhs.name + "+ = False")
    else:
        eq_str = eq.lhs.name + " = "
        for term in eq.terms:
            for literal in term:
                eq_str += literal + " & "
            eq_str = eq_str[:-3] + " || "

        print(eq_str[:-4])

def print_cfg_driven_encoding(node, succs):
    if node in succs:
        succs.remove(node)
    current_eq_str = ""
    next_eq_str = ""
    if succs:
        for succ_node in succs:
            current_eq_str += succ_node + " || "
            next_eq_str += succ_node + "+ || "
        current_eq_str = current_eq_str[:-4] + " --> !" + node
        next_eq_str = next_eq_str[:-4] + " --> !" + node + "+"
        print(current_eq_str)
        print(next_eq_str)
    # else:
    #     current_eq_str = node + " --> " + node
    #     next_eq_str = node + "+ --> " + node + "+"

def declare_input_variables(input_variable):
    if input_variable.type == "int":
        print("(declare-fun " + input_variable.name + " () " + "(_ BitVec " + input_variable.size + "))") # current state declaration
    else:
        print("Variable: " + input_variable.name +  " of type: " + input_variable.type + ' is not currently supported')

def declare_variables(variable):
    if (variable.type == "int") or (variable.type == 'int2bool'): #this is a hack which will be removed once CIL produces full variable info.
        print("(declare-fun " + variable.name + " () " + "(_ BitVec " + variable.size + "))") # current state declaration
        print("(declare-fun " + variable.name + "$next () " + "(_ BitVec " + variable.size + "))") # next state declaration
        print("(define-fun ." + variable.name + " () " + "(_ BitVec " + variable.size + ")" + " (! " + variable.name + " :next " + variable.name + "$next))") # next state link
    else:
        print("(declare-fun " + variable.name + " () " + variable.type + ")") # current state declaration
        print("(declare-fun " + variable.name + "$next () " + variable.type + ")") # next state declaration
        print("(define-fun ." + variable.name + " () " + variable.type + " (! " + variable.name + " :next " + variable.name + "$next))") # next state link
    
    if re.search("\AL.*S\d", variable.name) != None:
        print("(define-fun .loc" + variable.name + " () " + variable.type + " (! " + variable.name + " :loc_var " + variable.name + "$next))") # location tag

 


def initial_state(line_variable_dict, initial_node):
    print("\n")
    print("(define-fun .init () Bool (! \n \t(and") # define the initial state function
    for variable in line_variable_dict.values():
        if variable.name == initial_node:
            print("\t\t" + variable.name + "")
        else:
            print("\t\t(not " + variable.name + ")")
    print("\t)\n\t:init true))")
    print("\n")


def get_vmt_operator(operator):
    op_map = {
    ">" : "bvugt",
    "<" : "bvult",
    "+" : "bvadd",
    "-" : "bvsub",
    "<=" : "bvule",
    ">=" : "bvuge",
    "!=" : "=",
    "==" : "=",
    "=" : "=",
    }
    try:
        return op_map[operator]

    except:
        print("THIS OPERATOR: " + operator + " IS NOT CURRENTLY SUPPORTED")

def get_vmt_data_type(variable):
    if variable.isdigit(): # FIXME how do I find data type for rhs variable+const?
        return "(_ bv" + variable + " 32)"
    else:
        return variable

def VMT_And(literals):
    and_str = "(and "
    for literal in literals:
        and_str += literal + " "
    return and_str[:-1] + ")"



def write_line_transition_total(name, terms, next_state_string):
    next_state_string = next_state_string
    next_state_string += "\n\t\t(or "
    for term in terms:
        condition = term[1]
        if condition.lhs == "":
            next_state_string += " " + term[0]  + " "
            continue

        if isinstance(condition.lhs, str):
            condition_str = condition.lhs[1:-1] # removes brackets FIXME for multiple return statements
            if condition.negate:
                condition_str =  " (not " + condition_str + ")"
            next_line = term[0]
            next_state_string += '(and ' + next_line + ' ' + condition_str + ")"

        else:
            condition_str = "("+get_vmt_operator(condition.operator) + " " + condition.lhs.name + " " + get_vmt_data_type(condition.rhs.name) + ")"
            if condition.operator == '!=':
                condition_str = "(not " + condition_str + ")"
            if condition.negate:
                condition_str = "(not " + condition_str + ")"
            next_line = term[0]
            vmt_condition = VMT_And([next_line, condition_str])
            next_state_string += " " + vmt_condition
    opening_brackets  = next_state_string.count("(")
    closing_brackets  = next_state_string.count(")")
    for i in range(0, opening_brackets-closing_brackets): # close all ite calls -1 is to add the final closing bracket
        next_state_string += ")"
    return next_state_string



def build_transition_relation_total( implication_equation_dict, vmt_line_equation_dict, CFG): #one_hot_cfg_driven_eq_dict,

    print("\n")
    print("(define-fun trel_equations () Bool (!  \n \t(and") # define the initial state function
    for eq in vmt_line_equation_dict.values():

        indent = '\t\t\t'
        next_node = eq.lhs.name
        next_state_string = "\t(= " + next_node +  " "
        node = next_node[:-len('$next')]


        if eq.terms[0][0] == "false":
            next_state_string += indent + eq.terms[0][0]
            open_bracket_numb = next_state_string.count('(')
            closing_bracket_numb = next_state_string.count(')')
            for i in range(closing_bracket_numb, open_bracket_numb):
                next_state_string += ")"
            print(next_state_string)
            continue

        condition = eq.terms[0][1]
        next_line = eq.terms[0][0]
        if (condition.lhs == "") and (len(eq.terms) == 1):
                next_state_string +=  indent + eq.terms[0][0]
                open_bracket_numb = next_state_string.count('(')
                closing_bracket_numb = next_state_string.count(')')
                for i in range(closing_bracket_numb, open_bracket_numb):
                    next_state_string += ")"
                print(next_state_string)
                continue
        next_state_string = write_line_transition_total(eq.lhs.name, eq.terms, next_state_string)

        print(next_state_string)

    ######## data VMT transitions####################
    for eq in implication_equation_dict.values():
        indent = "\t\t"
        next_state_string = indent
        next_state_string += "(= " + eq.variable.name + "$next\n"
       
        for line, data_assignment in eq.line_and_data_set:
            node = CFG.node_dict[line]
            for pred in node.preds:
                pred_node = CFG.node_dict[pred]
                for edge in pred_node.edges:
                    if edge.dest == node.node_numb:
                        condition = process_condition(edge.source, edge.condition)
                        next_state_string += indent + "(ite\n"
                        next_state_string += indent + condition
                        exp = data_assignment.exp
                        # Really hacky, but it's because a Bool in C is an int type, but a Bool in VMT
                        # is incompatable with int. So we convert to something like:
                        # G = (x==y) to: G = (x==y) ? 1 : G
                        if eq.variable.type == 'int2bool':
                            next_state_string += indent + "(ite\n"
                            int_2_bool_str =  "(" + get_vmt_operator(exp.operator) + ' ' + exp.rhs.name + ' ' + ' ' + exp.lhs.name + ")\n"
                            if exp.operator == '!=':
                                int_2_bool_str =  " (not " + int_2_bool_str + ")"
                            next_state_string += indent + int_2_bool_str 
                            next_state_string += indent + '(_ bv1 32)'
                            next_state_string += indent + eq.variable.name + ')'
                        else: 
                            if exp.lhs == None: # this is an expression with a single term from something like: x = y;
                                if exp.rhs.name.isdigit(): # some digit ex: x = 9;
                                    next_state_string += indent + "(_ bv" + exp.rhs.name + " " + exp.rhs.size + ")\n"
                                else: # this some variable like: x = y;
                                # lhs = data_assignment.lhs # this would be x and exp.rhs is y
                                    next_state_string += indent + exp.rhs.name + "\n"

                            else:

                                if exp.rhs.name.isdigit(): # some digit ex: x = x + 9;
                                    exp.rhs.name = "(_ bv" + exp.rhs.name + " " + exp.rhs.size + ")"

                                if exp.lhs.name.isdigit(): # some digit ex: x = 9 + x;
                                    exp.lhs.name = "(_ bv" + exp.lhs.name + " " + exp.lhs.size + ")"

                                next_state_string += indent + "("+ get_vmt_operator(exp.operator) + " " + exp.lhs.name + " " + exp.rhs.name + ")\n"


        closing_brackets = ''
        for i in range(0, next_state_string.count('(') - next_state_string.count(')')):
            closing_brackets += ")"
        next_state_string += "\t\t\t" + eq.variable.name + closing_brackets
        print(next_state_string)

    print("\t) \n\t:trans true))")
    print("\n")



def write_line_transition(name, terms, next_state_string):
    next_state_string = next_state_string
    next_state_string += "\n\t\t(or "
    for term in terms:
        condition = term[1]
        if condition.lhs == "":
            next_state_string += " " + term[0]  + " "
            continue

        if isinstance(condition.lhs, str):
            condition_str = condition.lhs[1:-1] # removes brackets FIXME for multiple return statements
            if condition.negate:
                condition_str =  " (not " + condition_str + ")"
            next_line = term[0]
            next_state_string += '(and ' + next_line + ' ' + condition_str + ")"

        else:
            condition_str = "("+get_vmt_operator(condition.operator) + " " + condition.lhs.name + " " + get_vmt_data_type(condition.rhs.name) + ")"
            if condition.operator == '!=':
                condition_str = "(not " + condition_str + ")"
            if condition.negate:
                condition_str = "(not " + condition_str + ")"
            next_line = term[0]
            vmt_condition = VMT_And([next_line, condition_str])
            next_state_string += " " + vmt_condition
    opening_brackets  = next_state_string.count("(")
    closing_brackets  = next_state_string.count(")")
    for i in range(0, opening_brackets-closing_brackets-2): # close all ite calls -2 is to add the final closing bracket
        next_state_string += ")" 
    # else:
    #     if isinstance(condition.lhs, str): # boolean/wait case
    #         condition_str = condition.lhs[1:-1] # removes brackets FIXME for multiple return statements
    #         if condition.negate:
    #             condition_str = "(not " + condition_str + ")"
    #
    #     else:
    #         # next_state_string += "\t\t(ite\n"
    #         condition_str = "("+get_vmt_operator(condition.operator) + " " + condition.lhs.name + " " + get_vmt_data_type(condition.rhs.name) + ")"
    #
    #         if condition.operator == '!=':
    #             condition_str = "(not " + condition_str + ")"
    #         if condition.negate:
    #             condition_str = "(not " + condition_str + ")"
    #     next_line = term[0]
    #     vmt_condition = VMT_And([next_line, condition_str])
    #     next_state_string += "\t\t\t" + vmt_condition + "\n"
    #     next_state_string += "\t\t\t" + next_line + "\n"
    #     if len(terms[1:]): # remove the processed term
    #         next_state_string = write_line_transition(name, terms[1:], next_state_string)
    #         return next_state_string
    # next_state_string += "\t\t\t" + name[:-5]

    # for i in range(-1, next_state_string.count("(ite")): # close all ite calls -1 is to add the final closing bracket
    #     next_state_string += ")"
    return next_state_string

# def print_one_hot_vmt(node, preds): # not in use FIXME remove
#     # next_state_string = "\t\t(= " + node + "\n"
#     next_state_string = "\n\t\t(ite\n"
#     if len(preds) > 1:
#         next_state_string += "\t\t\t(or "
#         for pred in preds:
#             next_state_string += pred + " "
#         next_state_string = next_state_string[:-1] + ")\n\t\t\tfalse\n"
#         # next_state_string += "\t\t\t" + node + "))"

    # elif preds:
    #         pred = preds[0]
    #         next_state_string += "\t\t\t" + pred + " "
    #         next_state_string = next_state_string[:-1] + "\n\t\t\tfalse\n"
    #         # next_state_string += "\t\t\t" + node + "))"
    #
    # else:
    #     next_state_string = "" # FIXME check final state, should loop I think.
    #
    # return next_state_string


def build_transition_relation( implication_equation_dict, vmt_line_equation_dict, CFG): #one_hot_cfg_driven_eq_dict,

    print("\n")
    # print("(define-fun trel_equations () Bool (!  \n \t(and") # define the initial state function
    for eq in vmt_line_equation_dict.values():
        next_state_string = "(define-fun .trel_slice_" + eq.lhs.name + " () Bool (!\n" # define the initial state function

        indent = '\t\t\t'
        next_node = eq.lhs.name
        next_state_string += "\t(= " + next_node +  " "
        node = next_node[:-len('$next')]


        if eq.terms[0][0] == "false":
            next_state_string += indent + eq.terms[0][0]
            open_bracket_numb = next_state_string.count('(')
            closing_bracket_numb = next_state_string.count(')')
            for i in range(closing_bracket_numb+2, open_bracket_numb):
                next_state_string += ")"
            next_state_string += "\n\t:trans_slice_" + eq.lhs.name + " true))"
            print(next_state_string + '\n') 
            continue

        condition = eq.terms[0][1]
        next_line = eq.terms[0][0]
        if (condition.lhs == "") and (len(eq.terms) == 1):
                next_state_string +=  indent + eq.terms[0][0]
                open_bracket_numb = next_state_string.count('(')
                closing_bracket_numb = next_state_string.count(')')
                for i in range(closing_bracket_numb+2, open_bracket_numb):
                    next_state_string += ")"
                next_state_string += "\n\t:trans_slice_" + eq.lhs.name + " true))"
                print(next_state_string + '\n')
                continue
        next_state_string = write_line_transition(eq.lhs.name, eq.terms, next_state_string) 
        next_state_string += "\n\t:trans_slice_" + eq.lhs.name + " true))"
        print(next_state_string + '\n')

    ######## data VMT transitions####################
    # Prints slices of data equations, an example looks like:
    # for some location: L13S1, where an assigment of (i=0) occurs:
    # (define-fun .data_slice_i_L13S1$next () Bool (!
	# (=> L13S1
	# 	(= i		(_ bv0 32)))
    # :data_slice_i_L13S1 true))

    for eq in implication_equation_dict.values():
        indent = "\t\t"
          
        for line, data_assignment in eq.line_and_data_set:
            print('(define-fun .data_slice_' + eq.variable.name + '_' + line + '$next () Bool (!')
            # next_state_string = "\t(=> " + line  + '$next'  # something like: (=> LiSj$next
            next_state_string = '\t\t(= ' + eq.variable.name + '$next'
            exp = data_assignment.exp

            if exp.lhs == None: # this is an expression with a single term from something like: x = y;
                if exp.rhs.name.isdigit(): # some digit ex: x = 9;
                    next_state_string += indent + "(_ bv" + exp.rhs.name + " " + exp.rhs.size + ")"
                else: # this some variable like: x = y;
                # lhs = data_assignment.lhs # this would be x and exp.rhs is y
                    next_state_string += indent + exp.rhs.name 

            else:

                if exp.rhs.name.isdigit(): # some digit ex: x = x + 9;
                    exp.rhs.name = "(_ bv" + exp.rhs.name + " " + exp.rhs.size + ")"

                if exp.lhs.name.isdigit(): # some digit ex: x = 9 + x;
                    exp.lhs.name = "(_ bv" + exp.lhs.name + " " + exp.lhs.size + ")"

                next_state_string += indent + "("+ get_vmt_operator(exp.operator) + " " + exp.lhs.name + " " + exp.rhs.name + ')'
            # next_state_string += ')'
            for i in range(0, next_state_string.count('(') - next_state_string.count(')')):
                next_state_string += ")"
            print(next_state_string)
            print(':data_slice_' + eq.variable.name + '_' + line  + '$next' + " true))")
            print("\n")

    

def process_condition(pred_name, condition):
    if condition.lhs == "":
        next_state_string = " " + pred_name  + " "
        return next_state_string

    if isinstance(condition.lhs, str):

        condition_str = condition.lhs[1:-1] # removes brackets FIXME for multiple return statements
        if condition.negate:
            condition_str =  " (not " + condition_str + ")"
        next_state_string = '(and ' + pred_name + ' ' + condition_str + ")"

    else:
        condition_str = "("+get_vmt_operator(condition.operator) + " " + condition.lhs.name + " " + get_vmt_data_type(condition.rhs.name) + ")"
        if condition.operator == '!=':
            condition_str = "(not " + condition_str + ")"
        if condition.negate:
            condition_str = "(not " + condition_str + ")"

        vmt_condition = VMT_And([pred_name, condition_str])
        next_state_string = " " + vmt_condition
    return next_state_string

def build_one_hot_encoding_global(node_name_list):
    print('; GLOBAL one-hot encoding assumptions')
    print('(define-fun one_hot_global () Bool\n(and')
    from itertools import combinations_with_replacement
    # node_name_list = set(['L0', 'L1', 'L2', 'L3', 'L4', 'L5'])
    # this gets each unique pair of nodes as a list, ie unique_node_pairs = [(L0, L1), (L0, L2) ... ] but pairs such as (L1, L0) will not appear.
    unique_node_pairs = list(combinations_with_replacement(node_name_list, 2))
    for [node1, node2] in unique_node_pairs:
        if node1 == node2:
            continue

        char_list = ['W', 'R']
        res2 = list(filter(lambda x:  x in node2, char_list))
        res1 = list(filter(lambda x:  x in node1, char_list))
        dummy_nodes = res1 + res2
        if len(dummy_nodes) > 0:
            continue
        print('(or (not ' +  node1 + ') (not ' + node2 + '))')
    print(')')
    print(')')

    print('; GLOBAL one-hot encoding assumptions')
    print('(define-fun one_hot_global$next () Bool\n(and')

    for [node1, node2] in unique_node_pairs:
        char_list = ['W', 'R']
        res2 = list(filter(lambda x:  x in node2, char_list))
        res1 = list(filter(lambda x:  x in node1, char_list))
        dummy_nodes = res1 + res2
        if len(dummy_nodes) > 0:
            continue
        if node1 == node2:
            continue
        print('(or (not ' +  node1 + '$next) (not ' + node2 + '$next))')
    print(')')
    print(')')


def print_one_hot_vmt_local(node, succs):
    one_hot_str = '(=> '
    if (len(succs)>1):
        one_hot_str += '(or '
        for succ in succs:
            one_hot_str += succ + ' '
        one_hot_str += ')'
    elif (len(succs) == 1):
        one_hot_str += succs[0] + ' '
    else:
        return
    one_hot_str += ' (not ' + node + '))'
    print(one_hot_str)

def build_one_hot_encoding_local(one_hot_cfg_driven_eq_dict):
    print('(define-fun one_hot_local () Bool')
    print('(and')

    for node in one_hot_cfg_driven_eq_dict:
        succs = one_hot_cfg_driven_eq_dict[node]
        print_one_hot_vmt_local(node, succs)
    print(')')
    print(')')

    print('(define-fun one_hot_local$next () Bool')
    print('(and')
    for node in one_hot_cfg_driven_eq_dict:
        succs = one_hot_cfg_driven_eq_dict[node]

        next_succs = [succ + "$next" for succ in succs]
        next_node = node + "$next"

        next_state_string = print_one_hot_vmt_local(next_node, next_succs)
    print(')')
    print(')')

# def build_pred_map(CFG):
#     for node in CFG.node_dict.values():
#         pred_str = '(define-fun .preds_' + node.node_numb   + ' () Bool (! '
#         pred_str += '(' + node.node_numb + "\n"
#         pred_str += "\n" +':preds_' + node.node_numb  + "\n"
#         if len(node.preds) == 0:
#             pred_str += "false" # no preds, never reachable unless init.
#         elif len(node.preds) == 1:
#             pred_str += node.preds[0] # add the pred
#         else: 
#             pred_str += '( ' + "\n"
#             for pred in node.preds:
#                 pred_str += pred + "\n" # check me for more than two preds for VMT?
#         for _ in range(0, pred_str.count('(') - pred_str.count(')')):
#             pred_str += ")" # close all brackets, save the last two added below
#         # pred_str += "\n" +':preds_' + node.node_numb  +  " true))" + "\n"
#         print(pred_str + "\n")

def build_VMT_CFG(implication_equation_dict, vmt_line_equation_dict, CFG): #one_hot_cfg_driven_eq_dict,
    import pdb
    indent = "\t"
    for node in CFG.node_dict.values():
        
        for edge in node.edges:
            edge_cond_list = []
        # for succ_name in node.succs:
            succ = CFG.node_dict[edge.dest] # get the node object for the destination
            data_assign_str = "" # may have multible variables in one data assignment

            for data_assign in succ.expressions:
                # data_assign_str = "" # may have multible variables in one data assignment

                # pdb.set_trace()
                exp = data_assign.exp
                assignment_variable = data_assign.lhs.name # variable getting assigned
                # data_assign_str = "\t(=> " + line  + '$next'  # something like: (=> LiSj$next
                data_assign_str += indent + '(= ' + assignment_variable + '$next'
                exp = data_assign.exp
                if exp.lhs == None: # this is an expression with a single term from something like: x = y;
                    if exp.rhs.name.isdigit(): # some digit ex: x = 9;
                        data_assign_str += indent + "(_ bv" + exp.rhs.name + " " + exp.rhs.size + ")"
                    else: # this some variable like: x = y;
                    # lhs = data_assignment.lhs # this would be x and exp.rhs is y
                        data_assign_str += indent + exp.rhs.name 

                else:

                    if exp.rhs.name.isdigit(): # some digit ex: x = x + 9;
                        exp.rhs.name = "(_ bv" + exp.rhs.name + " " + exp.rhs.size + ")"

                    if exp.lhs.name.isdigit(): # some digit ex: x = 9 + x;
                        exp.lhs.name = "(_ bv" + exp.lhs.name + " " + exp.lhs.size + ")"

                    data_assign_str += indent + "("+ get_vmt_operator(exp.operator) + " " + exp.lhs.name + " " + exp.rhs.name + ')'
                # next_state_string += ')'
                for i in range(0, data_assign_str.count('(') - data_assign_str.count(')')):
                    data_assign_str += ")"
                data_assign_str += '\n' 
                edge_cond_list.append(data_assign_str)
                
        
            edge_str = "\n"
            condition_str = ""
            # pdb.set_trace()
            condition = edge.condition
            if (condition.lhs != ""): #and (len(eq.terms) == 1):
                condition_str = "("+get_vmt_operator(condition.operator) + " " + condition.lhs.name + " " + get_vmt_data_type(condition.rhs.name) + ")"
                if condition.negate:
                    condition_str =  "(not " + condition_str + ")" 
                condition_str = indent + condition_str + '\n'
            if condition_str == data_assign_str == '':
                edge_cond_list.append('true\n')
            elif condition_str != "":
                edge_cond_list.append(condition_str)
            edge_str = '(define-fun .edge_' + edge.source + '$source_' + edge.dest + '$dest () Bool (!\n'   # one for each node
            
            # edge_str += data_assign_str + condition_str + '\n\n'
            if len(edge_cond_list) > 1 :
                edge_str += VMT_And(edge_cond_list)
            else:
                edge_str += edge_cond_list[0]

            # for i, cond_str in enumerate(edge_cond_list):

            #     edge_str += cond_str 
            # pdb.set_trace()
            for i in range(0, edge_str.count('(') - 2 - edge_str.count(')')):
                edge_str += ")"
            edge_str += ":edge_" + edge.source + '$source'  "_" + edge.dest + '$dest true))'
            print(edge_str + '\n\n')

        #     edge_str = write_line_transition(eq.lhs.name, eq.terms, edge_str) 
        #     edge_str += "\n\t:trans_slice_" + eq.lhs.name + " true))"
        #     print(edge_str + '\n')

        # node_str += edge_str
        # node_str  += ':node_' + node.node_numb + '$next' + " true))\n"

        # node_str += edge_str

        # open_bracket_numb = node_str.count('(')
        # closing_bracket_numb = node_str.count(')')
        

 
        

    # ######## data VMT transitions####################
    # # Prints slices of data equations, an example looks like:
    # # for some location: L13S1, where an assigment of (i=0) occurs:
    # # (define-fun .data_slice_i_L13S1$next () Bool (!
	# # (=> L13S1
	# # 	(= i		(_ bv0 32)))
    # # :data_slice_i_L13S1 true))

    # for eq in implication_equation_dict.values():
    #     indent = "\t\t"
          
    #     for line, data_assignment in eq.line_and_data_set:
    #         print('(define-fun .data_slice_' + eq.variable.name + '_' + line + '$next () Bool (!')
    #         # next_state_string = "\t(=> " + line  + '$next'  # something like: (=> LiSj$next
    #         next_state_string = '\t\t(= ' + eq.variable.name + '$next'
    #         exp = data_assignment.exp

    #         if exp.lhs == None: # this is an expression with a single term from something like: x = y;
    #             if exp.rhs.name.isdigit(): # some digit ex: x = 9;
    #                 next_state_string += indent + "(_ bv" + exp.rhs.name + " " + exp.rhs.size + ")"
    #             else: # this some variable like: x = y;
    #             # lhs = data_assignment.lhs # this would be x and exp.rhs is y
    #                 next_state_string += indent + exp.rhs.name 

    #         else:

    #             if exp.rhs.name.isdigit(): # some digit ex: x = x + 9;
    #                 exp.rhs.name = "(_ bv" + exp.rhs.name + " " + exp.rhs.size + ")"

    #             if exp.lhs.name.isdigit(): # some digit ex: x = 9 + x;
    #                 exp.lhs.name = "(_ bv" + exp.lhs.name + " " + exp.lhs.size + ")"

    #             next_state_string += indent + "("+ get_vmt_operator(exp.operator) + " " + exp.lhs.name + " " + exp.rhs.name + ')'
    #         # next_state_string += ')'
    #         for i in range(0, next_state_string.count('(') - next_state_string.count(')')):
    #             next_state_string += ")"
    #         print(next_state_string)
    #         print(':data_slice_' + eq.variable.name + '_' + line  + '$next' + " true))")
    #         print("\n")

   

def combine_one_hot_and_trans_formulas(LOCAL):
    if LOCAL:
        print('; With LOCAL one-hotness the combined formula is:')
    else:
        print('; With GLOBAL one-hotness the combined formula is:')

    print('(define-fun .trans () Bool (! ')
    print('(and ')
    print('trel_equations ')
    if LOCAL:
        print('one_hot_local')
        print('one_hot_local$next')
    else:
        print('one_hot_global')
        print('one_hot_global$next')
    print(') \n:trans true))')




def build_property(property_locations):
    output_str = "\n(define-fun .property () Bool (!\n"
    output_str += "\t(not\n"
    output_str += "\t(or\n" #FIXME MAYBE NOT CORRECT?
    for location in property_locations:
        output_str += "\t " + location + "\n"
    output_str += "\t)) \n:invar-property 0))"
    print(output_str)


def CFG_node_edge_count(node, node_count, conditional_branches):
    node_count += 1
    for edge in node.edges:
        if edge.condition.lhs != '':
            # import pdb; pdb.set_trace()
            conditional_branches += 1
    return [node_count, conditional_branches]



def get_equations(CFG, LOCAL):
    line_equation_dict = {} # lhs_var_name, class equation
    vmt_line_equation_dict = {}
    line_variable_dict = {} # name, class variable
    implication_equation_dict = {}
    one_hot_cfg_driven_eq_dict = {}
    variable_update_loc_dict = {}
    data_variable_dict = {}
    print_readable = False
    print_vmt = True
    node_count = 0
    conditional_branches = 0
    if print_readable:
        readable_one_hot_list = []
        readable_data_assignments = []

        print_readable_init(CFG.file_entry_node)


    for node in CFG.node_dict.values():
        [node_count, conditional_branches] = CFG_node_edge_count(node, node_count, conditional_branches)

        one_hot_cfg_driven_eq_dict[node.node_numb] = [] # empty list to be populated by each pred
        next_state = node.node_numb + "$next"
        line_variable_dict[node.node_numb] = bool_line_var(node.node_numb, "Bool")
        if node.preds == []:
            vmt_line_equation_dict[next_state] = equality_equation(bool_line_var(next_state, "Bool")) # define an eq and set the lhs to Ln+
            vmt_line_equation_dict[next_state].terms.append(["false"]) # next state = false, if no preds, this node never occurs again.
        for expression in node.expressions:
            if expression.lhs.name not in implication_equation_dict:
                data_variable_dict[expression.lhs.name] = expression.lhs # exp.lhs is of class variable defined in the CFG python file
                implication_equation_dict[expression.lhs.name] = implication_equation(expression.lhs)

                variable_update_loc_dict[expression.lhs.name] = [node.node_numb] # track each update location
            else:
                variable_update_loc_dict[expression.lhs.name].append(node.node_numb) # track each update location
            if print_readable:
                readable_data_assignments.append([node.node_numb, expression.lhs.name, expression.rhs])
            implication_equation_dict[expression.lhs.name].line_and_data_set.append([node.node_numb, expression])

        for succ in node.succs:
            try:
                succ_node = CFG.node_dict[succ]
            except:
                import pdb; pdb.set_trace()
            if succ_node == node: #if self loop
                continue
            one_hot_cfg_driven_eq_dict[node.node_numb].append(succ_node.node_numb) # empty list to be populated by each pred
        if print_readable:

            readable_one_hot_list.append([node.node_numb, node.succs])

        for edge in node.edges:

            dest_node = CFG.node_dict[edge.dest] # get the destination of the edge
            # if dest_node.node_numb == node.node_numb:
            #     continue # skip self loops?
            dest_next_state = dest_node.node_numb + "+"
            vmt_dest_next_state = dest_node.node_numb + "$next"
            if dest_next_state not in line_equation_dict:
                if node.preds == []:
                    line_equation_dict[node.node_numb] = equality_equation(bool_line_var(node.node_numb, "False")) # define an eq and set the lhs to Ln+

                line_equation_dict[dest_next_state] = equality_equation(bool_line_var(dest_next_state, "Bool")) # define an eq and set the lhs to Ln+
                vmt_line_equation_dict[dest_next_state] = equality_equation(bool_line_var(vmt_dest_next_state, "Bool"))
            vmt_line_equation_dict[dest_next_state].terms.append([node.node_numb, edge.condition])


            # used for READABLE eqs only
            # if edge.condition.lhs == "": # if the edge is unconditional append the next (destination) node
            #     line_equation_dict[dest_next_state].terms.append([node.node_numb])
            # elif isinstance(edge.condition.lhs, str):
            #
            # else:
            #     exp = edge.condition # this is an expression like: x > y
            #
            #     if exp.negate == True:# CLEAN ME UP SOON!
            #         try:
            #             line_equation_dict[dest_next_state].terms.append([node.node_numb, "!("+exp.lhs.name + exp.operator + exp.rhs.name + ")"])
            #         except:
            #             import pdb; pdb.set_trace()
            #     else:
            #         line_equation_dict[dest_ne#         edge.condition = " & (" + edge.condition + ")"
        #     if edge.dest in line_equation_dict:
        #         line_equation_dict[edge.dest] = line_equation_dict[edge.dest] + " || " + edge.source + edge.condition
        #     else:
        #         line_equation_dict[edge.dest] = edge.source + edge.condition
        #
        # # line = node.node_numb
        # for label_set in node.label_list:
        #     if (type(label_set) is list) and (len(label_set) == 3): # This filters for assignment labels
        #         data = label_set[2]
        #         if type(label_set[0]) == type(cfg_util.variable("name", "type", "funct")):
        #             variable = label_set[0].name
        #         else:
        #             variable = label_set[0]
        #         if variable in data_equation_dict:
        #             data_equation_dict[variable].append(data_equation(node.node_numb, variable, data))
        #         else:
        #             data_equation_dict[variable] = [data_equation(node.node_numb, variable, data)]
        #

                #         L2 --> i+ = i + 2
                #         L3 --> i+ = i + 5
                #         !L2 & !L3 --> i+ = i
            # for lbl in label_set:
            #     if lbl = "":
            #         continue
            #     if lbl =

    #
    # for eq in line_equation_dict:
    #     print(eq + "+" + " = " + line_equation_dict[eq])
    #
    # for i, (variable, data_eq_set) in enumerate(data_equation_dict.items()):
    #
    #     line_list = []
    #     for data_eq in data_eq_set:
    #         print(data_eq.line + " --> " + variable + "+ = " + data_eq.data)
    #         line_list.append(data_eq.line)
    #
    #     str = ""
    #     for line in line_list:
    #         str = str + "!" + line + " & "
    #     str = str[:-3] + " --> " + variable + "+ = " + variable
    #     print(str)

# defxt_state].terms.append([node.node_numb, "("+exp.lhs.name + exp.operator + exp.rhs.name + ")"])


#################### READABLE EQS #####################

    if print_readable:
        print("\n# Line Next State")
        for eq in line_equation_dict.values():
            print_line_eq(eq)

        print("\n# CFG-Driven One-Hot Encoding")
        for node_number, succs in readable_one_hot_list:
            print_cfg_driven_encoding(node_number, succs)

        print("\n# Data Assignments")
        for node_number, lhs, rhs in readable_data_assignments:
            print_data_assignment(node_number, lhs, rhs)

        print("\n# Data Preservation")
        for variable in variable_update_loc_dict:
            print_data_preservation(variable, variable_update_loc_dict[variable])



################## VMT #############################
    if print_vmt:
        for input_variable_set in CFG.input_variables.values():
            for input_variable in input_variable_set:
                declare_input_variables(input_variable)
        for variable in line_variable_dict.values():
            declare_variables(variable)
        for variable in data_variable_dict.values():
            declare_variables(variable)
        initial_state(line_variable_dict, CFG.file_entry_node)
        build_VMT_CFG(implication_equation_dict, vmt_line_equation_dict, CFG) #one_hot_cfg_driven_eq_dict,

        # build_transition_relation(implication_equation_dict, vmt_line_equation_dict, CFG) #one_hot_cfg_driven_eq_dict,
        build_transition_relation_total(implication_equation_dict, vmt_line_equation_dict, CFG)
        # build_pred_map(CFG)
        # if LOCAL:
        #     build_one_hot_encoding_local(one_hot_cfg_driven_eq_dict)
        # else:
        #     # using only the names of each node as a list
        #     build_one_hot_encoding_global(list(CFG.node_dict.keys()))

        # LOCAL is a bool which if true prints local one-hottness or if false prints global one-hotness
        # combine_one_hot_and_trans_formulas(LOCAL)
        build_property(CFG.property_locations)
        numb_of_data_variables = len(variable_update_loc_dict)
        numb_of_data_updates = 0
        for variable_update_loc_list in variable_update_loc_dict.values():
            numb_of_data_updates += len(variable_update_loc_list)
        node_count = 0
        conditional_branches = 0
        print_CFG_analytics_2_file(node_count, conditional_branches, numb_of_data_variables, numb_of_data_updates)



def print_CFG_analytics_2_file(node_count, conditional_branches, numb_of_data_variables, numb_of_data_updates):
    f = open("demofile2.txt", "a")
    f.write("NODES: " + str(node_count))
    f.write("CONDITIONAL BRANCHES: " + str(conditional_branches))
    f.write("NUMBER OF VARIABLES: " + str(numb_of_data_variables))
    f.write("NUMBER OF DATA UPDATES: " + str(numb_of_data_updates))
