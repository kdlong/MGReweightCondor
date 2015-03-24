#!/usr/bin/env python
import subprocess
import sys
import splitLHEFile
import string
import os
import argparse
# Author: Kenneth Long, Matt Herndon
# Created: Oct. 3, 2014

# This program runs the MadGraph/MadEvent reweight process on the condor cluster
# by dividing a large .lhe file stored in the Events/run_XX directory of a 
# MadGraph process into multiple files and separately running MadEvent reweight
# on each split LHE file unweighted_events_XXX.lhe. It is recommended that the 
# number of split files be such that each separate condor process takes more than 5
# hours but absolutely not more than 24 (the condor job will be evicted in this case)

# Command line arguments: configuration file
#
# Edit configuration file from condor_reweight_config.py
# Set paths and specifics of reweight here

def main():
    args = getComLineArgs()
    print arg.config_file
    if args.config_file[-3:] == '.py':
       config_file_name = args.config_file[:-3]
    __import__(config_file_name)
    config = sys.modules[config_file_name]

    if not os.path.exists(config.full_process_path):
        print 'Your configuration file does not list a valid process directory!'
        exit(1) 
    lhe_file = config.full_run_path + config.lhe_file_name + ".lhe"
    split_file_base = config.split_files_path + config.lhe_file_name + '_' 
    makeDirectories(config.new_directories)
    
    if os.path.isfile(lhe_file + '.gz'):
        subprocess.call(["gunzip", lhe_file + '.gz']) 

    if config.kCreateTarball:
        createProcessTarball(config.process_dir, config.process_tarball_path, 
                             config.base_directory, config.process_dir + "/Events/*")
    if config.kSplitFiles:    
        print 'Spliting lhe file into ' + str(config.num_files) + ' files'
        splitLHEFile.split(lhe_file, split_file_base, int(config.num_files))
    
    makeFileFromTemplate(config.template_files_path, config.run_files_path, 
                         "madevent_reweight", "", ".cmd", 
                         {'RUN_NAME' : config.run_name}) 
    
    for i in range(0, int(config.num_files)):
        job_num = formatNumWithZeros(i, 3)
        submit_file = split_file_base + job_num + ".lhe"
        submitCondorJob(config.template_files_path, config.submit_files_path, 
                        config.run_files_path, job_num, config.dict)

# This function returns command line argument #(argument_num). If there is no 
# argv[argument_num], it asks the user to enter argument_name and returns this value
def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str, help="Configuration file name" 
                        " (stored in config_files directory)")
    return parser.parse_args()
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
def createProcessTarball(process_dir, process_base_path, process_tarball_path, 
                         exclude_file): 
    print 'Creating tar file'
    tar_file = process_dir + ".tar.gz"
    subprocess.call(["tar", "-czf", tar_file, "-C", process_base_path, 
                     process_dir, "--exclude", exclude_file])
    subprocess.call(["mv", tar_file, process_tarball_path])
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
        if not os.path.exists(directory): 
            os.makedirs(directory)
if __name__ == "__main__":
    main()
