Introduction and Purpose
------------------------
The reweight function of MadGraph first calculates new matrix elements for the new model parameters and then forms an event weight by the square of the ratios (more info via [the MadGraph Wiki](https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/Reweight)). It evaluates these for each event and writes these new events to the file. It's nowhere near as computationally intensive as the full calculation, so it is not set up to be parallel or able to run on condor. The problem is that for a large number of events and several different weights it can add up. For 100,000 events, 20 weights at 1 hour each is a stretch to run locally and for ~ 1 million events it's unreasonable. 

This script solves this issue by splitting the LHE file into pieces and running the process on each split file separately on condor. It's not computationally efficient but it's the simplest solution. MadGraph runs exactly like it would on the server, the advantage is that Condor allows you to run on many separate jobs simultaneously rather than on one sequentially.

### Usage:

Call the program as: `condor_reweight.py [config_file_name]`
  for example: `condor_reweight.py example.cfg`

You interact with the program via a config file. A heavily documented example is [config_files/example.cfg](https://github.com/kdlong/MGReweightCondor/blob/master/config_files/example.cfg). It implements the python [ConfigParser](https://docs.python.org/2/library/configparser.html) syntax, which is largely straightforward. Note that interpolation (including the value of another variable in a new variable definition) is supported by the syntax `value = new_text%(old_value)snew_text` ONLY FOR VALUES WITHIN THE SAME SECTION!

NOTE: The setup.sh script downloads the MadGraph version 2.2.3 tarball from the web and places in in the `transfer_files` folder. If you need a model not in MadGraph by default, you should instead create a tarball with your model in it. Make sure your directory is named MG5_aMC_v2_2_3 AND IS PLACED IN THE `transfer_files` DIRECTORY!  If you are at UW, you can copy tarball  of MG with the SM_LS0_LS1_UFO and SM_LT012_UFO models from `/nfs_kdlong/nfs_scratch/condor_reweight/transfer_files/madgraph.tar.gz`

### How It Works

1. Create a .tar.gz (compressed) file of the madgraph process. The tarball is then placed in a directory you specify (`/nfs_scratch/USERNAME` by default) and is transfered to condor for each run. Make sure your directory contains a reweight_card.dat before running the program!

2. Split the LHE file into `num_files` pieces. You should choose this so that jobs tke 3-6 hours to run. Because this technique is inefficient, and the same Matrix Elements have to be calculated for each file, JOBS RUNNING FOR LESS THAN 1 HOUR ARE VERY INEFFICIENT (See [this plot](http://www.hep.wisc.edu/~kdlong/plots/memGraphs/memGraph_nz.pdf))!!! For pp > WZ+jets, I use about 1000 events per file with ~30 reweight parameter. A large amount of time in the reweight process is devoted to calculated the matrix elements, after which the main time usage is calculating weights and writing them to the file. Therefore, to maximize your efficiency you should run with larger lhe files. However, condor jobs should absolutely not run over 24 hours! They will be likely be evicted if that is the case.

3. Create run-specific condor_submit and run files from the template files stored in [MGReweightCondor/template_files](https://github.com/kdlong/MGReweightCondor/tree/master/templates) using the specifications stored in the python dictionary inside the `condor_reweight.py`. By default, directories will be created inside the run directory, e.g. `/nfs_scratch/<username>/<process_name>/run_<run_num>/`. These directories will contain the split lhe files, the condor log, error, and output files, the reweighted lhe files (after completion of the condor jobs), and condor_submit and condor run scripts for each file.

4. Submit the job to condor for each separate split LHE file

### Notes and Tips

1. If you would like to recombine the weighted lhe files into a single file after all the condor processes complete, just run the script `merge_files/merge_weighted_files.py` in the directory where all the weighted lhe files are placed (by default in `weighted_lhe_files` in your run directory)

2. If a job you submit has a problem or is held, you should first check the `condor_error/condor_error_XXX` and `condor_output/condor_output_XXX` file corresponding to that job (placed in the `condor_run_files` diretory, by default in the `Events/run_0X` directory of your process). If the job is running and you want to see if it is running correctly, find the job ID from condor_q and use `condor_ssh_to_job <job_num>`. This will ssh you to the computer on which your job is running. You can look at its output by `less _condor_stdout` and its error messages by `less _condor_stderr`. You can also check for a hold reason on a job by running `condor_q -hold <jobID>`. If this returns that a file to transfer is missing, for example, you can locate that file and run `condor_release <jobID>` to continue running.

3. The line `requirement = memory >= 8000` in [submit_condor_template](https://github.com/kdlong/MGReweightCondor/blob/master/templates/submit_condor_template) stipulates that the jobs will only run on condor machines which have > 8GB of RAM. This is the reason that these jobs will be in an idle state for much longer than a usual condor submission. This means that jobs of about 10,000 events may not always run much faster using this technique, but it is important to run on condor rather than the login machines regardless, as those machines really aren't set up for one user to run a 8GB process for days.

