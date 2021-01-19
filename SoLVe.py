import sys
import cfg_util as c_ut # builds CFG
import cfg_opt as o_ut # Optimizes the CFG
import equation_util as e_ut # builds equation set/VMT from the CFG

# import merge as merge
def main():
    # 'cfg_opt.txt'
    file_name = sys.argv[1]
    # LOCAL is a bool which if true prints local one-hottness or if false prints global one-hotness
    LOCAL = False
    if '--local' in sys.argv[:]:
        LOCAL = True
    CFG = c_ut.get_file_CFG(file_name)
    c_ut.display_CFG(CFG, "raw_CFG")
    # e_ut.get_equations(CFG)
    # CFG = o_ut.remove_redundant_nodes(CFG)
    # CFG = o_ut.remove_isolated_nodes(CFG)
    # c_ut.display_CFG(CFG, "opt_CFG")
    e_ut.get_equations(CFG, LOCAL)




if __name__ == '__main__':
    main()

"""
TODO:
1. Test more benchmarks
2. Integrate location information into euforia
"""
