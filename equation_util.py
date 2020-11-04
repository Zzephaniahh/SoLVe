
class data_equation():
    def __init__(self, line, variable, data):
        self.line = line
        self.variable = variable
        self.data = data
    #         L2 --> i+ = i + 2
    #         L3 --> i+ = i + 5
    #         !L2 & !L3 --> i+ = i

def get_readable_equations(CFG):
    line_equation_dict = {}

    data_equation_dict = {}


    for node in CFG.node_dict.values():

        for edge in node.edges:
            # print(edge.condition)
            if edge.condition == "True":
                edge.condition = ""
            else:
                edge.condition = " & (" + edge.condition + ")"
            if edge.dest in line_equation_dict:
                line_equation_dict[edge.dest] = line_equation_dict[edge.dest] + " || L" + edge.source + edge.condition
            else:
                line_equation_dict[edge.dest] = "L" + edge.source + edge.condition

        # line = node.node_numb
        # print(node.label_list)
        for label_set in node.label_list:
            if len(label_set) == 3: # This filters for assignment labels
                data = label_set[2]
                # equal_symb = label_set[1]
                variable = label_set[0]
                if variable in data_equation_dict:
                    data_equation_dict[variable].append(data_equation(node.node_numb, variable, data))
                else:
                    data_equation_dict[variable] = [data_equation(node.node_numb, variable, data)]

    for i, (variable, data_eq_set) in enumerate(data_equation_dict.items()):

        line_list = []
        for data_eq in data_eq_set:
            # print(data_eq.line)
            print("L" + data_eq.line + " --> " + variable + "+ = " + data_eq.data)
            line_list.append(data_eq.line)

        str = ""
        for line in line_list:
            str = str + "!L" + line + " & "
        str = str[:-3] + " --> " + variable + "+ = " + variable
        print(str)
                #         L2 --> i+ = i + 2
                #         L3 --> i+ = i + 5
                #         !L2 & !L3 --> i+ = i
            # for lbl in label_set:
            #     if lbl = "":
            #         continue
            #     if lbl =


    print("L1+ = 0") # probably don't need this, but helps us read for now.
    for eq in line_equation_dict:
        print("L" + eq + "+" + " = " + line_equation_dict[eq])




# def print_data_eqs(): #DFG
#     equation_dict = {}
#     location_var_dict = {}
#     for node in DFG.data_transfer_list:
#         var = data_transfer.variable
#         location = data_transfer.line_number
#         value = data_transfer.data
#
#         L2 --> i+ = i + 2
#         L3 --> i+ = i + 5
#         !L2 & !L3 --> i+ = i
#         equation_dict[location] = "L" + location + " --> " + var + "+ = " +  value
#
#         if var in location_var_dict:
#             location_var_dict[var].append(location)
#         else:
#             location_var_dict[var] = [location]
#
#         # if var in equation_dict:
#         #     equation_dict[var] = equation_dict[var]+ " || "+ "L" + location + " & value = " +  value
#         # else:
#         #     equation_dict[var] = var + "+ = " + "L" + location + " & value = " +  value
#
#     for eq in equation_dict:
#         print(equation_dict[eq])
#     #print(location_var_dict)
#     for var in location_var_dict:
#                 # !L2 & !L3 --> i+ = i
#         loc_str = ""
#         for location in location_var_dict[var]:
#             loc_str = loc_str + "!L" + location + " & "
#
#         loc_str = loc_str[:-3] + " --> " + var + "+ = " + var
#         print(loc_str)
