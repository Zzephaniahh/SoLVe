import os # used to navigate the file file system
from os import listdir
from os.path import isfile, join
# from os import walk # not used currently
import pandas as pd # build dataframes
import datetime
import subprocess
current_time = datetime.datetime.now()
from tabulate import tabulate


LOCKSPATH = "/home/zephaniah/Documents/Zephaniahs_Research/SoLVe/locks/global_out"
SOLVEPATH = '/home/zephaniah/Documents/Zephaniahs_Research/SoLVe'
f = []
# for (dirpath, dirnames, filenames) in walk("/home/zephaniah/Documents/Zephaniahs_Research/sv-benchmarks-svcomp17/c/locks"):4
# get all files excluding folders, and only accept files ending with ".c"
files_in_locks_dir = [f for f in listdir(LOCKSPATH) if (isfile(join(LOCKSPATH, f)) and (f.endswith(".txt")))]
os.chdir(LOCKSPATH) # change dir to benchmarks
# import pdb; pdb.set_trace()
locks_df = {
'Name': [], # file name
'Time_stamp': [], # when this analysis was run
'Flops_initialized': [],
'One_hot_type': [], # local or global
'Run_time': [], # if the property holds when AVR checks
'AVR_run_time': [],
'Number_of_refinements': [],
'Number_of_learned_clauses': [],
'MEM': [],
'P_holds': [], # if the file is supposed to hold
'AVR_result': [] # if the property holds when AVR checks
# ... add more info here
}

# files_in_locks_dir = ['test_locks_15_false-unreach-call_true-valid-memsafety_false-termination.c_out_global.txt']
for file_name in files_in_locks_dir:
    locks_df['Name'].append(file_name[:-len('_out_global.txt')])
    locks_df['Time_stamp'].append(current_time)
    if 'true-unreach-call' in file_name:
        locks_df['P_holds'].append('True')
    else:
        locks_df['P_holds'].append('False')

    if 'global' in file_name:
        locks_df['One_hot_type'].append('Global')

    lines = open(file_name, 'r').readlines()
    for index, line in enumerate(lines):
        if ' flops initialized)' in line:
            [lhs, slash, rhs] = line.split()[:len(line.split())-2]
            locks_df['Flops_initialized'].append(lhs[1:]+slash+rhs)

        if '           h' in line:
            locks_df['AVR_result'].append('True')
            [avr_result, avr_time, mem, refs] = line.split()
            locks_df['AVR_run_time'].append(avr_time + ' sec')
            locks_df['MEM'].append(mem + ' MB')
            [user, system, elapsed, cpu, other, other2] = lines[index+1].split()
            [minutes, seconds] = elapsed[:-len('elapsed')].split(':')
            run_time = float(minutes)*60+float(seconds)
            locks_df['Run_time'].append(run_time)
            final_step_data = lines[index-3].split(':')
            final_step_data = [data.strip() for data in final_step_data]
            Number_of_refinements = final_step_data[1]
            Number_of_learned_clauses = final_step_data[len(final_step_data)-1].split()[0]
            locks_df['Number_of_refinements'].append(Number_of_refinements)
            locks_df['Number_of_learned_clauses'].append(Number_of_learned_clauses)
            # import pdb; pdb.set_trace()

        if '           v' in line:
            locks_df['AVR_result'].append('False')
            [avr_result, avr_time, mem, refs] = line.split()
            locks_df['AVR_run_time'].append(avr_time + ' sec')
            locks_df['MEM'].append(mem + ' MB')
            [user, system, elapsed, cpu, other, other2] = lines[index+1].split()
            [minutes, seconds] = elapsed[:-len('elapsed')].split(':')
            run_time = float(minutes)*60+float(seconds)

            locks_df['Run_time'].append(run_time)
            final_step_data = lines[index-3].split(':')
            final_step_data = [data.strip() for data in final_step_data]
            Number_of_refinements = final_step_data[1]
            Number_of_learned_clauses = final_step_data[len(final_step_data)-1].split()[0]
            locks_df['Number_of_refinements'].append(Number_of_refinements)
            locks_df['Number_of_learned_clauses'].append(Number_of_learned_clauses)
            # if file_name == 'test_locks_6_true-unreach-call_true-valid-memsafety_false-termination.c_out_global.txt':
            # import pdb; pdb.set_trace()
    # process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    # output, error = process.communicate()


# items = ['Name', 'Time_stamp', 'Flops_initialized', 'One_hot_type', 'Run_time', 'AVR_run_time', 'MEM', 'P_holds', 'AVR_result']
#
#
# for item in items:
#     print(locks_df[item])


# locks_df = {
# 'Name': [],
# 'Lines': [],
# 'Time_stamp': [],
# 'P_holds': []
# # ... add more info here
# }

# for file_name in onlyfiles:
#     number_of_lines = len(open(file_name, 'r').readlines())
#     if 'true-unreach-call' in file_name:
#         locks_df['P_holds'].append('True')
#     else:
#         locks_df['P_holds'].append('False')
#
#     locks_df['Name'].append(file_name)
#     locks_df['Lines'].append(number_of_lines)
#     locks_df['Time_stamp'].append(current_time)
#
df = pd.DataFrame(locks_df)
os.chdir(SOLVEPATH) # change dir to benchmarks

with open('global_run_data.csv', 'w') as f_csv:
    gfg_csv_data = df.to_csv(index = False)
    # import pdb; pdb.set_trace()
    f_csv.write(gfg_csv_data)
# print('\nCSV String:\n', gfg_csv_data)
# print(df)
print(tabulate(df, headers='keys', tablefmt='psql'))
