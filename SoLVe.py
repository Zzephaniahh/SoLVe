import sys
import cfg_util as c_ut # builds CFG
import cfg_opt as o_ut # Optimizes the CFG
import equation_util as e_ut # builds equation set/VMT from the CFG

# import merge as merge
def main():
    # 'cfg_opt.txt'
    file_name = sys.argv[1]
    CFG = c_ut.get_file_CFG(file_name)
    c_ut.display_CFG(CFG, "raw_CFG")
    # e_ut.get_equations(CFG)
    # CFG = o_ut.remove_redundant_nodes(CFG)
    # CFG = o_ut.remove_isolated_nodes(CFG)
    c_ut.display_CFG(CFG, "opt_CFG")
    e_ut.get_equations(CFG)




if __name__ == '__main__':
    main()

"""
TODO:
1. Test more benchmarks
2. Develop optimizations on the CFG for verification
    2.1 Make a DFG --- unsure if global or local DFG is wise?
"""


def get_function_decls(lines):
    global current_line_numb

    for line in lines:
        current_line_numb = current_line_numb + 1
        if line.startswith('Function dec: '): # get names
            func_decl = fun_decl(None, None, [])
            func_decl.func_name = line[len("Function dec: "):].strip()
        #CHECK ME WITH VOID/NO ARGS
        if line.startswith('Type: '): # get formal args and type
            args_type_str = line[len("Type: "):]
            func_decl.func_type = re.search(r"(.*?)\(", args_type_str).group(0)[:-1].strip()
            args_str = args_type_str[len(func_decl.func_type):].strip()

            args  = re.sub(r'\((.*?)\)', lambda L: L.group(1).rsplit('|', 1)[-1], args_str).rstrip().split(",")
            for index, arg in enumerate(args):
                arg = arg.strip() #clears spaces
                arg_and_type = arg.split(" ")
                func_decl.formal_param_list.append(arg_and_type)
            func_decl_list.append(func_decl)

            # if verbose == True:

            # print(func_decl.func_name)
            # print(func_decl.func_type)
            # print(func_decl.formal_param_list)
            current_line_numb = current_line_numb + 1
            return
