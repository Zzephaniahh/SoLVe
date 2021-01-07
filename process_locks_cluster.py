import os # used to navigate the file file system
from os import listdir
from os.path import isfile, join
# from os import walk # not used currently
import pandas as pd # build dataframes
import datetime
import subprocess
current_time = datetime.datetime.now()

# cd ../avr/


# LOCKSPATH = "/home/zeph/SoLVe/locks"
LOCKSPATH = "/home/zephaniah/Documents/Zephaniahs_Research/SoLVe/cluster_test"

locks_df = {
# 'Name': [],
'Start_time': [],
'End_time': [],
# 'P_holds': []
# ... add more info here
}


f = []
# for (dirpath, dirnames, filenames) in walk("/home/zephaniah/Documents/Zephaniahs_Research/sv-benchmarks-svcomp17/c/locks"):4
# get all files excluding folders, and only accept files ending with ".c"
files_in_locks_dir = [f for f in listdir(LOCKSPATH) if (isfile(join(LOCKSPATH, f)) and (f.endswith(".c")))]

for file_name in files_in_locks_dir:
    # if 'true-unreach-call' in file_name:
    #     locks_df['P_holds'].append('True')
    # else:
    #     locks_df['P_holds'].append('False')
    # locks_df['Name'].append(file_name)
    locks_df['Start_time'].append(current_time)
    bashCommand = "time ./full_run.sh locks/" + file_name
    os.system(bashCommand)
    locks_df['End_time'].append(current_time)

    # process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    # output, error = process.communicate()


# os.chdir(LOCKSPATH) # change dir to benchmarks
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

df = pd.DataFrame(locks_df)

print(df)
