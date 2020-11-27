import cfg_util
from cfg_util import expression

class eqaulity_equation():
    def __init__(self, lhs):
        self.lhs = lhs # type = var
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

class var():
    def __init__(self, name, type):
        self.name = name
        self.type = type

def print_data_assignment(line, variable, data):
    print(line + "+ --> " + variable + "+ = " + data)

def print_data_preservation(variable, update_loc_list):
    no_update_str = ""
    for line in update_loc_list:
        no_update_str += "!" + line + "+ & "
    print(no_update_str[:-3] + " --> " + variable + "+ = " + variable)

def print_line_eq(eq):
    eq_str = eq.lhs.name + " = "
    for term in eq.terms:
        for literal in term:
            eq_str += literal + " & "
        eq_str = eq_str[:-3] + " || "

    print(eq_str[:-4])

def print_cfg_driven_encoding(node, succs):
    current_eq_str = ""
    next_eq_str = ""
    if succs:
        for succ_node in succs:
            current_eq_str += succ_node + " || "
            next_eq_str += succ_node + "+ || "
        current_eq_str = current_eq_str[:-4] + " --> !" + node
        next_eq_str = next_eq_str[:-4] + " --> !" + node + "+"
    else:
        current_eq_str = node + " --> " + node
        next_eq_str = node + "+ --> " + node + "+"
    print(current_eq_str)
    print(next_eq_str)

def declare_variables(variable):
    if variable.type == "int": #this is a hack which will be removed once CIL produces full variable info.
        print("(declare-fun " + variable.name + " () " + "(_ BitVec 32))") # current state declaration
        print("(declare-fun " + variable.name + "$next () " + "(_ BitVec 32))") # next state declaration
        print("(define-fun ." + variable.name + " () " + "(_ BitVec 32)" + " (! " + variable.name + " :next " + variable.name + "$next))") # next state link
    else:
        print("(declare-fun " + variable.name + " () " + variable.type + ")") # current state declaration
        print("(declare-fun " + variable.name + "$next () " + variable.type + ")") # next state declaration
        print("(define-fun ." + variable.name + " () " + variable.type + " (! " + variable.name + " :next " + variable.name + "$next))") # next state link


def intial_state(variable_dict):
    print("\n")
    print("(define-fun .init () Bool (! \n \t(and") # define the initial state function
    for variable in variable_dict.values():
        if variable.type == "int":
            print("\t\t(= " + variable.name + " (_ bv0 32))") # super hacky REMOVE ME
        elif variable.name == "L1": # I hate this, maybe mark the entry node in a clean way.
            print("\t\t" + variable.name + "")
        else:
            print("\t\t(not " + variable.name + ")")
    print("\t)\n\t:init true))")
    print("\n")


def get_vmt_operator(operator):
    op_map = {
    ">" : "bvgt",
    "<" : "bvult",
    "+" : "bvadd",
    "-" : "bvsub",
    }
    try:
        return op_map[operator]

    except:
        print("THIS OPERATOR: " + operator + " IS NOT CURRENTLY SUPPORTED")

def get_vmt_data_type(variable):
    if variable.isdigit():
        return "(_ bv" + variable + " 32)"
    else:
        return variable

def VMT_And(literals):
    and_str = "(and "
    for literal in literals:
        and_str += literal + " "
    return and_str[:-1] + ")"

def parse_data(data):
    if "+" in data:
        [lhs, rhs] = data.split("+")
        return expression(lhs, rhs, "+", True)


def write_line_transition(name, terms, next_state_string):
    next_state_string = next_state_string
    term = terms[0]
    condition = term[1]
    if condition.lhs == "":
        next_state_string += "\t\t(ite\n"
        next_state_string += "\t\t\t" + term[0] + "\n"
        next_state_string += "\t\t\t" + term[0] + "\n"
        if len(terms[1:]): # remove the processed term
            next_state_string = write_line_transition(name, terms[1:], next_state_string)
            return next_state_string
    else:
        next_line = term[0]
        next_state_string += "\n\t\t(ite\n"
        vmt_condition = VMT_And([next_line, "("+get_vmt_operator(condition.operator) + " " + condition.lhs + " " + get_vmt_data_type(condition.rhs) + ")"])
        next_state_string += "\t\t\t" + vmt_condition + "\n"
        next_state_string += "\t\t\t" + next_line + "\n"
        if len(terms[1:]): # remove the processed term
            next_state_string = write_line_transition(name, terms[1:], next_state_string)
            return next_state_string
    next_state_string += "\t\t\t" + name[:-5]

    for i in range(-1, next_state_string.count("(ite")): # close all ite calls -1 is to add the final closing bracket
        next_state_string += ")"
    return next_state_string





def build_transition_relation(one_hot_cfg_driven_eq_dict, implication_equation_dict, vmt_line_equation_dict):

    print("\n")
    ######## line VMT transitions####################
    print("(define-fun .trans () Bool (!  \n \t(and") # define the initial state function
    for eq in vmt_line_equation_dict.values():
        next_state_string = "\t\t(= " + eq.lhs.name +  " "
        condition = eq.terms[0][1]
        next_line = eq.terms[0][0]
        if (condition.lhs == "") and (len(eq.terms) == 1):
                next_state_string += eq.terms[0][0]
                next_state_string += ")"
                print(next_state_string)
                continue
        next_state_string = write_line_transition(eq.lhs.name, eq.terms, next_state_string)
        print(next_state_string)

    ######## data VMT transitions####################
    for eq in implication_equation_dict.values():
        indent = "\t\t"
        next_state_string = indent
        next_state_string += "(= " + eq.variable + "$next\n"
        ite_count = 0
        for line, data in eq.line_and_data_set:
            ite_count += 1
            # if ite_count == 2:
                # import pdb; pdb.set_trace()
            next_state_string += indent + "(ite\n"
            indent += "   "
            if data.isdigit(): # fixme when I have type info
                next_state_string += indent + line +"\n"
                next_state_string += indent + "(_ bv"+ data + " 32)\n"
            else:
                exp = parse_data(data)
                next_state_string += indent + line +"\n"
                if exp.rhs.isdigit():
                    next_state_string += indent + "("+ get_vmt_operator(exp.operator) + " " + exp.lhs +  " (_ bv" + exp.rhs + " 32))\n"
                else:

                    next_state_string += indent + "("+ get_vmt_operator(exp.operator) + " " + exp.lhs + " " + exp.rhs + " )\n"


        closing_brackets = ")"
        for i in range(0, ite_count):
            closing_brackets += ")"
        next_state_string += "\t\t\t" + eq.variable + closing_brackets
        print(next_state_string)

############ CFG-driven One-Hot ####################
    for node in one_hot_cfg_driven_eq_dict:
        preds = one_hot_cfg_driven_eq_dict[node]
        next_state_string = "\t\t(= " + node + "\n"
        next_state_string += "\t\t\t(ite\n"
        if len(preds) > 1:
            next_state_string += "\t\t\t(or "
            for pred in preds:
                next_state_string += pred + " "
            next_state_string = next_state_string[:-1] + ")\n\t\t\tfalse\n"
            next_state_string += "\t\t\t" + node + "))"

        elif preds:
                pred = preds[0]
                next_state_string += "\t\t\t" + pred + " "
                next_state_string = next_state_string[:-1] + "\n\t\t\tfalse\n"
                next_state_string += "\t\t\t" + node + "))"

        else:
            next_state_string = "" # FIXME check final state, should loop I think.
        print(next_state_string)

    print("\t) \n\t:trans true))")
    print("\n")


def Hard_code_P(P_bool):
    if P_bool:
        print("\n(define-fun .property () Bool (!")
        print("\t(and")
        print("\t\t(not (= z (_ bv9 32)))")
        print(")")
        print(":invar-property 0))")
    else:
        print("\n(define-fun .property () Bool (!")
        print("\t(and")
        print("\t\t(not (= z (_ bv7 32)))")
        print("\t)")
        print("\t:invar-property 0))")


def get_readable_equations(CFG):
    line_equation_dict = {} # lhs_var_name, class eqaution
    vmt_line_equation_dict = {}
    variable_dict = {} # name, class variable
    implication_equation_dict = {}
    one_hot_cfg_driven_eq_dict = {}
    variable_update_loc_dict = {}
    data_variable_dict = {}
    print_readable = False

    for node in CFG.node_dict.values():
        one_hot_cfg_driven_eq_dict[node.node_numb] = [] # empty list to be populated by each pred
        next_state = node.node_numb + "$next"
        variable_dict[node.node_numb] = var(node.node_numb, "Bool")
        # if node.preds == []:
        #     line_equation_dict[next_state] = eqaulity_equation(var(next_state, "Bool")) # define an eq and set the lhs to Ln+
        #     line_equation_dict[next_state].terms.append(["false"]) # next state = false, if no preds, this node never occurs again.

        for expression in node.expressions:
            if expression.lhs.name not in implication_equation_dict:
                data_variable_dict[expression.lhs.name] = var(expression.lhs.name, expression.lhs.type)
                implication_equation_dict[expression.lhs.name] = implication_equation(expression.lhs.name)

                variable_update_loc_dict[expression.lhs.name] = [node.node_numb] # track each update location
            else:
                variable_update_loc_dict[expression.lhs.name].append(node.node_numb) # track each update location
            if print_readable:
                print_data_assignment(node.node_numb, expression.lhs.name, expression.rhs)

            implication_equation_dict[expression.lhs.name].line_and_data_set.append([node.node_numb, expression.rhs])

        for succ in node.succs:
            succ_node = CFG.node_dict[succ]
            if succ_node == node: #if self loop
                continue
            one_hot_cfg_driven_eq_dict[node.node_numb].append(succ_node.node_numb) # empty list to be populated by each pred
        if print_readable:
            print_cfg_driven_encoding(node.node_numb, node.succs)

        for edge in node.edges:
            dest_node = CFG.node_dict[edge.dest] # get the destination of the edge
            # if dest_node.node_numb == node.node_numb:
            #     continue # skip self loops?
            dest_next_state = dest_node.node_numb + "+"
            vmt_dest_next_state = dest_node.node_numb + "$next"
            if dest_next_state not in line_equation_dict:
                line_equation_dict[dest_next_state] = eqaulity_equation(var(dest_next_state, "Bool")) # define an eq and set the lhs to Ln+
                vmt_line_equation_dict[dest_next_state] = eqaulity_equation(var(vmt_dest_next_state, "Bool"))
            vmt_line_equation_dict[dest_next_state].terms.append([node.node_numb, edge.condition])

            if edge.condition.lhs == "": # if the edge is unconditional append the next (destination) node
                line_equation_dict[dest_next_state].terms.append([node.node_numb])
            else:
                exp = edge.condition # this is an expression like: x > y

                if exp.negate == True:# CLEAN ME UP SOON!
                    line_equation_dict[dest_next_state].terms.append([node.node_numb, "!("+exp.lhs + exp.operator + exp.rhs+ ")"])
                else:
                    line_equation_dict[dest_next_state].terms.append([node.node_numb, "("+exp.lhs + exp.operator + exp.rhs+ ")"])

        # if print_readable:
        #     print(node.node_numb)
        #     print_line_eq(line_equation_dict[dest_next_state])


#################### READABLE EQS #####################
    # for eq in line_equation_dict.values():
    #     print_line_eq(eq)

    # for eq in implication_equation_dict.values():
    #     print_data_eq(eq)
    #
    # for node in one_hot_cfg_driven_eq_dict:
    #     pred_nodes = one_hot_cfg_driven_eq_dict[node]
    #     print_cfg_driven_encoding(node, pred_nodes)
    # print(line_equation_dict)

    if print_readable:
        print("\n# Line Next State")
        for eq in line_equation_dict.values():
            print_line_eq(eq)
        print("\n# Data Preservation")
        for variable in variable_update_loc_dict:
            print_data_preservation(variable, variable_update_loc_dict[variable])


################## VMT #############################
    for variable in variable_dict.values():
        declare_variables(variable)
    for variable in data_variable_dict.values():
        declare_variables(variable)
    intial_state(variable_dict)

    build_transition_relation(one_hot_cfg_driven_eq_dict, implication_equation_dict, vmt_line_equation_dict)
    #
    #
    Hard_code_P(True)



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
