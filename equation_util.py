import cfg_util
from cfg_util import *

class equality_equation():
    def __init__(self, lhs):
        self.lhs = lhs # type: var
        self.terms = [] # list of lists, inner lists are ANDed, outter list are ORed
        # L4+ = [L2 & !(x < y)] || L3  --- Becomes:
        # self.lhs = L4+
        # self.terms = [[L2, !(x < y)], L3]
#
# class term():
#     def __init__(self, name, type, temporal_loc):
#



    # def add_term

    # L1+ = 0
    # L2+ = L1
    # L3+ = L2 & (x < y)
    # L4+ = [L2 & !(x < y)] || L3
    # L5+ = L4

    #         L2 --> i+ = i + 2
    #         L3 --> i+ = i + 5
    #         !L2 & !L3 --> i+ = i
#
class implication_equation():
    def __init__(self, variable):
        self.variable = variable
        self.line_and_data_set = []

    # L1 --> y+ = 0
    # !L1 --> y+ = y
    # L1 --> x+ = 0
    # !L1 --> x+ = x
    # L1 --> z+ = 0
    # L3 --> z+ = 1
    # L4 --> z+ = 7
    # !L1 & !L3 & !L4 --> z+ = z

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
    if variable.type == "int": #this is a hack which will be removed once CIL produces full variable info.
        print("(declare-fun " + variable.name + " () " + "(_ BitVec " + variable.size + "))") # current state declaration
        print("(declare-fun " + variable.name + "$next () " + "(_ BitVec " + variable.size + "))") # next state declaration
        print("(define-fun ." + variable.name + " () " + "(_ BitVec " + variable.size + ")" + " (! " + variable.name + " :next " + variable.name + "$next))") # next state link
    else:
        print("(declare-fun " + variable.name + " () " + variable.type + ")") # current state declaration
        print("(declare-fun " + variable.name + "$next () " + variable.type + ")") # next state declaration
        print("(define-fun ." + variable.name + " () " + variable.type + " (! " + variable.name + " :next " + variable.name + "$next))") # next state link


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



def write_line_transition(name, terms, next_state_string):
    next_state_string = next_state_string
    term = terms[0]
    condition = term[1]
    if condition.lhs == "":
        next_state_string += "\t\t(ite\n"
        next_state_string += "\t\t\t" + term[0] + "\n"
        next_state_string += "\t\t\t" + term[0]  + "\n"
        if len(terms[1:]): # remove the processed term
            next_state_string = write_line_transition(name, terms[1:], next_state_string)
            return next_state_string
    else:
        next_line = term[0]
        next_state_string += "\t\t(ite\n"


        condition_str = "("+get_vmt_operator(condition.operator) + " " + condition.lhs.name + " " + get_vmt_data_type(condition.rhs.name) + ")"
        if condition.operator == '!=':
            condition_str = "(not " + condition_str + ")"
        if condition.negate:
            condition_str = "(not " + condition_str + ")"

        vmt_condition = VMT_And([next_line, condition_str])
        next_state_string += "\t\t\t" + vmt_condition + "\n"
        next_state_string += "\t\t\t" + next_line + "\n"
        if len(terms[1:]): # remove the processed term
            next_state_string = write_line_transition(name, terms[1:], next_state_string)
            return next_state_string
    next_state_string += "\t\t\t" + name[:-5]

    for i in range(-1, next_state_string.count("(ite")): # close all ite calls -1 is to add the final closing bracket
        next_state_string += ")"
    return next_state_string

def print_one_hot_vmt(node, preds):
    # next_state_string = "\t\t(= " + node + "\n"
    next_state_string = "\n\t\t(ite\n"
    if len(preds) > 1:
        next_state_string += "\t\t\t(or "
        for pred in preds:
            next_state_string += pred + " "
        next_state_string = next_state_string[:-1] + ")\n\t\t\tfalse\n"
        # next_state_string += "\t\t\t" + node + "))"

    elif preds:
            pred = preds[0]
            next_state_string += "\t\t\t" + pred + " "
            next_state_string = next_state_string[:-1] + "\n\t\t\tfalse\n"
            # next_state_string += "\t\t\t" + node + "))"

    else:
        next_state_string = "" # FIXME check final state, should loop I think.

    return next_state_string

def build_transition_relation(one_hot_cfg_driven_eq_dict, implication_equation_dict, vmt_line_equation_dict):

    print("\n")
    ######## line VMT transitions####################
    # for node in one_hot_cfg_driven_eq_dict:
    #     preds = one_hot_cfg_driven_eq_dict[node]
    #     next_state_string = print_one_hot_vmt(node, preds)
    #     print(next_state_string)
    #     next_preds = [pred + "$next" for pred in preds]
    #     next_node = node + "$next"
    #     next_state_string = print_one_hot_vmt(next_node, next_preds)
    #     print(next_state_string)

    print("(define-fun .trans () Bool (!  \n \t(and") # define the initial state function
    for eq in vmt_line_equation_dict.values():
        indent = '\t\t\t'
        # import pdb; pdb.set_trace()
        next_node = eq.lhs.name
        next_state_string = "\t(= " + next_node +  " "
        node = next_node[:-len('$next')]
        preds = one_hot_cfg_driven_eq_dict[node]
        # next_state_string = print_one_hot_vmt(node, preds)
        # print(next_state_string)
        next_preds = [pred + "$next" for pred in preds]
        next_node = node + "$next"
        next_state_string += print_one_hot_vmt(next_node, next_preds)
        # print(next_state_string)

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
        next_state_string = write_line_transition(eq.lhs.name, eq.terms, next_state_string)
        # open_bracket_numb = next_state_string.count('(')
        # closing_bracket_numb = next_state_string.count(')')
        # for i in range(closing_bracket_numb, open_bracket_numb):
        print(next_state_string)

    ######## data VMT transitions####################
    for eq in implication_equation_dict.values():
        indent = "\t\t"
        next_state_string = indent
        next_state_string += "(= " + eq.variable + "$next\n"
        ite_count = 0
        for line, data_assignment in eq.line_and_data_set:
            ite_count += 1
            next_state_string += indent + "(ite\n"
            indent += "   "
            exp = data_assignment.exp
            # if exp.rhs.name.isdigit(): # some digit ex: x = 9;
            #     import pdb; pdb.set_trace()
            #     next_state_string += indent + line + "\n"
            #     next_state_string += indent + "(_ bv" + exp.rhs.name + " " + exp.rhs.size + ")\n"

            # else:
                # type(data) == type(variable("","","","")): # some variable ex: x = y;
                # next_state_string += indent + "("+ get_vmt_operator(exp.operator) + " " + exp.lhs.name +  " (_ bv" + exp.rhs.name.strip() + + " " + exp.rhs.size + "))\n"

            next_state_string += indent + line +"\n"

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


            #     if exp.rhs.strip().isdigit():
            #         next_state_string += indent + "("+ get_vmt_operator(exp.operator) + " " + exp.lhs +  " (_ bv" + exp.rhs.strip() + " 32))\n"
            #     else:
            #         next_state_string += indent + "("+ get_vmt_operator(exp.operator) + " " + exp.lhs + " " + exp.rhs + " )\n"
            # elif type(data) == type(expression("","","","")):
            #     pass

        closing_brackets = ")"
        for i in range(0, ite_count):
            closing_brackets += ")"
        next_state_string += "\t\t\t" + eq.variable + closing_brackets
        print(next_state_string)

########### CFG-driven One-Hot ####################
    # for node in one_hot_cfg_driven_eq_dict:
    #     preds = one_hot_cfg_driven_eq_dict[node]
    #     next_state_string = print_one_hot_vmt(node, preds)
    #     print(next_state_string)
    #     next_preds = [pred + "$next" for pred in preds]
    #     next_node = node + "$next"
    #     next_state_string = print_one_hot_vmt(next_node, next_preds)
    #     print(next_state_string)

    print("\t) \n\t:trans true))")
    print("\n")


def build_property (property_locations):
    output_str = "\n(define-fun .property () Bool (!\n"
    output_str += "\t(and\n"
    output_str += "\t(not\n" #FIXME MAYBE NOT CORRECT?
    for location in property_locations:
        output_str += "\t " + location + "\n"
    output_str += "\t)) \n:invar-property 0))"
    print(output_str)

def get_equations(CFG):
    line_equation_dict = {} # lhs_var_name, class equation
    vmt_line_equation_dict = {}
    line_variable_dict = {} # name, class variable
    implication_equation_dict = {}
    one_hot_cfg_driven_eq_dict = {}
    variable_update_loc_dict = {}
    data_variable_dict = {}
    print_readable = False
    print_vmt = True
    if print_readable:
        readable_one_hot_list = []
        readable_data_assignments = []

        print_readable_init(CFG.file_entry_node)


    for node in CFG.node_dict.values():
        one_hot_cfg_driven_eq_dict[node.node_numb] = [] # empty list to be populated by each pred
        next_state = node.node_numb + "$next"
        line_variable_dict[node.node_numb] = bool_line_var(node.node_numb, "Bool")
        if node.preds == []:
            vmt_line_equation_dict[next_state] = equality_equation(bool_line_var(next_state, "Bool")) # define an eq and set the lhs to Ln+
            vmt_line_equation_dict[next_state].terms.append(["false"]) # next state = false, if no preds, this node never occurs again.
        for expression in node.expressions:
            if expression.lhs.name not in implication_equation_dict:
                data_variable_dict[expression.lhs.name] = expression.lhs # exp.lhs is of class variable defined in the CFG python file
                implication_equation_dict[expression.lhs.name] = implication_equation(expression.lhs.name)

                variable_update_loc_dict[expression.lhs.name] = [node.node_numb] # track each update location
            else:
                variable_update_loc_dict[expression.lhs.name].append(node.node_numb) # track each update location
            if print_readable:
                readable_data_assignments.append([node.node_numb, expression.lhs.name, expression.rhs])
            implication_equation_dict[expression.lhs.name].line_and_data_set.append([node.node_numb, expression])

        for succ in node.succs:
            succ_node = CFG.node_dict[succ]
            if succ_node == node: #if self loop
                continue
            one_hot_cfg_driven_eq_dict[node.node_numb].append(succ_node.node_numb) # empty list to be populated by each pred
        if print_readable:
            # if CFG.file_entry_node == node.node_numb:
            #     # print("\n# CFG driven Encoding:")
            # # cfg_driven_encodings.append([node.node_numb, expression.lhs.name, expression.rhs])

            readable_one_hot_list.append([node.node_numb, node.succs])
            # print_cfg_driven_encoding(node.node_numb, node.succs)

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

            if edge.condition.lhs == "": # if the edge is unconditional append the next (destination) node
                line_equation_dict[dest_next_state].terms.append([node.node_numb])
            else:
                exp = edge.condition # this is an expression like: x > y

                if exp.negate == True:# CLEAN ME UP SOON!
                    line_equation_dict[dest_next_state].terms.append([node.node_numb, "!("+exp.lhs.name + exp.operator + exp.rhs.name + ")"])
                else:
                    line_equation_dict[dest_next_state].terms.append([node.node_numb, "("+exp.lhs.name + exp.operator + exp.rhs.name + ")"])


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

        build_transition_relation(one_hot_cfg_driven_eq_dict, implication_equation_dict, vmt_line_equation_dict)


        build_property(CFG.property_locations)


        #         edge.condition = " & (" + edge.condition + ")"
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

# def
