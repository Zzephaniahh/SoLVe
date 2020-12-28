import sys
import cfg_util as c_ut
import equation_util as e_ut
# import merge as merge
def main():
    # 'cfg_opt.txt'
    our_CFG = c_ut.get_file_CFG('assert_test.txt')
    c_ut.display_CFG(our_CFG, "test_file") # maybe fixme cause I change the CFG (elim true)
    e_ut.get_equations(our_CFG)
    # merge.process_CFG(our_CFG)
    # get_vmt(our_CFG)


if __name__ == '__main__':
    main()

"""
TODO:
1. Test more complex source code
2. Get SMT-lib/VMT -- partially complete, need to handle more cases
3. Get full type info from CIL
4. Fix Orphaned nodes in CIL

Handle functions -- DONE!
Compute equations from graph -- Done!
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
