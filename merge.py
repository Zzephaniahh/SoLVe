# assume each location has the following class:
class location ():
    def __init__(self):
        self.next_state_condition = ""
        self.implication_equation_list = []

class implication_equation():
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

L1 = location()
L1.next_state_condition = "L0"
# "L1+ -> x+ = 3;"
L1_implication_eq = implication_equation("L1+", " x+ = 3")
L1.implication_equation_list.append(L1_implication_eq)

L2 = location()
L2.next_state_condition = "L1"
# "L1+ -> x+ = 3;"
L2_implication_eq = implication_equation("L2+", " y+ = 3")
L2.implication_equation_list.append(L2_implication_eq)

#
def merge(L1, L2):




def process_CFG(CFG):
    L1 = CFG.node_dict["L1"]
    L2 = CFG.node_dict["L2"]
    print(L1.expressions)
    print(L2.expressions)
