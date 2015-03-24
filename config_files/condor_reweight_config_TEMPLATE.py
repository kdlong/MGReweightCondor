#####################################################################################
# Author: Kenneth Long                                                              #
# Created October 9, 2014                                                           #
#                                                                                   #
# Configuation file for condor_reweight.py.                                         #
# DO NOT EDIT THIS FILE!                                                            #
# Instead, create a condor_reweight_configs folder and add a copy of this file      #
# for each configuration you intend to run. You will need to add this path to your  #
# PYTHONPATH: In the shell, type PYTHONPATH=$PYTHONPATH:<full path to config dir>   #
# You can add this to your .bashrc file for convenience.                            #
#####################################################################################
# Set to false if tarball already exists or if split files have already been created.
[Run Mode]
kCreateTarball = True
kSplitFiles = True

# These settings are unique to each job and should always be specifically set for 
# each run
####################################################################################
[Run Info]
process_dir = 'wpz_zg_qcd_all_LT012' #no trailing or leading / 
run_name = 'run_01' 
#number of split files to make. Recommended order ~1000 events per files
num_files = '100'   
####################################################################################
# These settings are set to the MadGraph defaults. Change them if you have 
# changed the name of your .lhe file or its location
####################################################################################
run_path = process_dir + "/Events/" + run_name + "/"
lhe_file_name = "unweighted_events" #leave out the .lhe extension

# These directories should exist at run time. All directories should have trailing /
#####################################################################################
# Where your process directory is located. This is used when creating the tarball,
# and is used by default to simplify setting paths below which can be derived from it
base_directory = "/nfs_scratch/kdlong/"
full_process_path = base_directory + process_dir

# Full path to the directory containing your .lhe file
full_run_path = base_directory + run_path
# full path to directory to place process tarball in after it is created.
process_tarball_path = base_directory

# Where the templates and files to be transfered at runtime will be stored. These
# should be kept to the defaults unless you want to change the template files
template_files_path = "/nfs_scratch/kdlong/condor_reweight/templates/"
transfer_files_path = "/nfs_scratch/kdlong/condor_reweight/transfer_files/"

# All the run files and condor_submit files will be placed in these directories.
# if you prefer, you can set these to separate location. By default, they are
# placed inside the run directory
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

# Dictionary created to fill templated files.
dict = {'MADGRAPH_TARBALL' : 'madgraph.tar.gz',
        'MADGRAPH_TARBALL_PATH' : transfer_files_path,
        'PROCESS_TARBALL' : process_dir + '.tar.gz', 
        'PROCESS_TARBALL_PATH' : process_tarball_path, 
        'RUN_DIR' : run_path,
        'PROCESS_DIR' : process_dir,
        'RUN_NAME' : run_name,
        'RUN_FILES_PATH' : run_files_path,
        'CONDOR_OUTPUT_PATH' : condor_output_path,
        'CONDOR_ERROR_PATH' : condor_error_path,
        'CONDOR_LOG_PATH' : condor_log_path,
        'WEIGHTED_FILES_PATH' : weighted_files_path,
        'SPLIT_FILES_PATH' : split_files_path,
        'TRANSFER_FILES_PATH' : transfer_files_path}

# Directories which should be created at run time.
new_directories = [run_files_path, condor_output_path, condor_error_path,
               condor_log_path, weighted_files_path, split_files_path, 
               submit_files_path]
if condor_files_path != full_run_path:
    new_directories.insert(0, condor_files_path)
