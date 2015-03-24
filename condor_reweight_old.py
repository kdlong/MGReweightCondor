#!/usr/bin/env python
import subprocess
import sys
import splitLHEFile
import string

# Author: Kenneth Long, Matt Herndon
# Created: Oct. 3, 2014

# This program runs the MadGraph/MadEvent reweight process on the condor cluster
# by dividing a large .lhe file stored in the Events/run_XX directory of a 
# MadGraph process into multiple files and separately running MadEvent reweight
# on each split LHE file unweighted_events_XXX.lhe. It is recommended that the 
# number of split files be such that each separate condor process takes more than 5
# hours but absolutely not more than 24 (the condor job will be evicted in this case)

# Command line arguments: process directory, user name in nfs_scrath, run number, 
# number of split files to make

#Ex: ./condor_reweight wpz_zg_all kdlong 1 100
def main():
    # Set these to true unless the split files and tarball have already been made
    kCreateTarball = False
    kSplitFiles = True
    
    process_dir = getCommandLineArg(1, 'process directory')
    if process_dir.endswith('/'):
        process_dir = process_dir[:-1]
    username = getCommandLineArg(2, 'user name')
    run_num = formatNumWithZeros(getCommandLineArg(3, 'run number'), 2)
    num_files = int(getCommandLineArg(4, 'Number of split files'))
     
    #These directories should exist at run time
    run_name = "run_" + run_num
    base_directory = "/nfs_scratch/" + username + "/"
    full_process_path = base_directory + process_dir + "/"
    
    #Where template files and transfer files are stored
    reweight_path = "/nfs_scratch/kdlong/condor_reweight/"
    template_path = reweight_path + "templates/"
    run_path = process_dir + "/Events/run_" + run_num + "/"
    full_run_path = base_directory + run_path
    lhe_file_name = "unweighted_events" #leave out the .lhe extension
    transfer_files_path = reweight_path + "transfer_files/"
    process_tarball_path = base_directory
   
    # By default, all files related to the condor reweight will be placed in the run
    # directory of the process in nfs_scratch
    condor_files_path = full_run_path
    # These directories are created at run_time. By default, they are created
    # in the directory of the reweighted run.
    run_files_path = condor_files_path + "run_files/"
    submit_files_path = condor_files_path + "submit_files/"
    condor_output_path = condor_files_path + "condor_output/"
    condor_error_path = condor_files_path + "condor_error/"
    condor_log_path = condor_files_path + "condor_logs/"
    weighted_files_path = condor_files_path + "weighted_lhe_files/"
    split_files_path = condor_files_path + "split_files/"
    
    # Used to fill templated files.
    dict = {'MADGRAPH_TARBALL' : 'madgraph.tar.gz',
            'MADGRAPH_TARBALL_PATH' : transfer_files_path,
            'PROCESS_TARBALL' : process_dir + '.tar.gz', 
            'PROCESS_TARBALL_PATH' : process_tarball_path, 
            'RUN_DIR' : run_path,
            'PROCESS_DIR' : process_dir,
            'REWEIGHT_PATH' : reweight_path,
            'RUN_NAME' : run_name,
            'RUN_FILES_PATH' : run_files_path,
            'CONDOR_OUTPUT_PATH' : condor_output_path,
            'CONDOR_ERROR_PATH' : condor_error_path,
            'CONDOR_LOG_PATH' : condor_log_path,
            'WEIGHTED_FILES_PATH' : weighted_files_path,
            'SPLIT_FILES_PATH' : split_files_path,
            'TRANSFER_FILES_PATH' : transfer_files_path}
    
    new_directories = [run_files_path, condor_output_path, condor_error_path,
                       condor_log_path, weighted_files_path, split_files_path, 
                       submit_files_path]
    if condor_files_path != full_run_path:
        new_directories.insert(0, condor_files_path)
    makeDirectories(new_directories)
    
    if kCreateTarball:
        createProcessTarball(process_dir, base_directory, 
                             run_path + lhe_file_name + '.lhe') 
    if kSplitFiles:    
        print 'Spliting lhe file into ' + str(num_files) + ' files'
        splitLHEFile.split(full_run_path + lhe_file_name + '.lhe', 
                           split_files_path + lhe_file_name + '_', num_files)
    
    makeFileFromTemplate(template_path, transfer_files_path, "madevent_reweight",
                         "", ".cmd", {'RUN_NAME' : run_name}) 
    
    lhe_file = split_files_path + lhe_file_name + ".lhe"
    split_file_base = split_files_path + lhe_file_name + "_"
    for i in range(num_files):
        job_num = formatNumWithZeros(i, 3)
        submit_file = split_file_base + job_num + ".lhe"
        submitCondorJob(template_path, submit_files_path, run_files_path, job_num, 
                        dict)

# This function returns command line argument #(argument_num). If there is no 
# argv[argument_num], it asks the user to enter argument_name and returns this value
def getCommandLineArg(argument_num, argument_name):
    if len(sys.argv) < argument_num + 1:
        print 'Please enter the ' + argument_name
        argument = raw_input()
    else:
        argument = sys.argv[argument_num]
    return argument
# This function creates a new file out_file_name by replacing all keys in
# keys in template_file_name of the form ${KEY_NAME} with the value indicated by
# the dictionary dict. e.g. if dict contains 'KEY' : 'hello', all occurances of
# ${KEY} in the file template file will be overwritten by hello in the new file
# out_file_name 
def fillTemplatedFile(template_file_name, out_file_name, dict):
    with open(template_file_name, "r") as templateFile:
        source = string.Template(templateFile.read())
        result = source.substitute(dict)
    with open(out_file_name, "w") as outFile:
        outFile.write(result)
# This function creates a tarball of the process directory, exluding the file
# exclude_file (the unsplit  unweighted_events.lhe in this program). This tarball
# is stored in base_directory
def createProcessTarball(process_dir, base_directory, exclude_file): 
    print 'Creating tar file'
    tar_file = process_dir + ".tar.gz"
    subprocess.call(["tar", "-czf", tar_file, "-C", base_directory, 
                     process_dir, "--exclude", exclude_file])
    subprocess.call(["mv", tar_file, base_directory])
# This function creates the run_madgraph_reweight_XXX.sh executable, stored in 
# run_files_path, and the submit_condor_xxx files, stored in submit_files_path, 
# from template files for the given job number XXX and calls the subprocess
# "condor_submit submit_condor_XXX to submit reweight #job_num to condor
def submitCondorJob(template_path, submit_files_path, run_files_path, job_num, 
                    dict):
    dict.update({'JOB_NUM' : job_num})
    submit_file = makeFileFromTemplate(template_path, submit_files_path, 
                                       "submit_condor", "_" + job_num, "", dict)
    run_file = makeFileFromTemplate(template_path, run_files_path, 
                            "run_madgraph_reweight", "_" + job_num, ".sh", dict) 
    subprocess.call(["chmod", "+x", run_file])
    subprocess.call(["condor_submit", submit_file])
# This function is a simple interface to create a file <file_name>_identifier
# in the location file_path given that a template file of the form
# <file_name>_template exists in the path template path. fillTemplatedFile
# is called to create the file.
def makeFileFromTemplate(template_path, file_path, file_name, indentifier, 
                         extension, dict) :
    template = template_path + file_name + "_template"
    file = file_path + file_name + indentifier + extension
    fillTemplatedFile(template, file, dict)
    return file
# formats a number to have length formatted_length regardless of it's order of
# magnitude by appending leading zeros. e.g., formatNumWithZeros(17, 5) returns
# 00017 
def formatNumWithZeros(num, formatted_length):
    formatted_num = str(num)
    while len(formatted_num) < formatted_length:
        formatted_num = "0" + formatted_num
    return formatted_num
# Creates a directory for each directory path in directory_list. These should be
# absolute, not relative, paths
def makeDirectories(directory_list):
    for directory in directory_list:
        subprocess.call(["mkdir", directory])

if __name__ == "__main__":
    main()
