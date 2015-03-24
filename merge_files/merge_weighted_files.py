#!/usr/bin/env python
import glob
import subprocess

reweight_path = "/nfs_scratch/kdlong/condor_reweight/"

lhe_file_list = glob.glob('*.lhe')
if len(lhe_file_list) != 0:
    gzip_command = ["gzip"]
    gzip_command.extend(lhe_file_list)
    subprocess.call(gzip_command)

gz_file_list = glob.glob('*.lhe.gz')
print len(gz_file_list)
if len(gz_file_list) != 0:
    merge_command = [reweight_path + "merge.pl"]
    merge_command.extend(gz_file_list)
    merge_command.append("../unweighted_events_rwgt.lhe.gz")
    merge_command.append("banner.txt")
    subprocess.call(merge_command)
else:
    print 'No LHE files found'
