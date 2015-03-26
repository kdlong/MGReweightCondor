#!/bin/bash

echo "Downloading MadGraph5_amC@NLO v2.2.3 from the web." 
echo "If you need use an external model (one that isn't in MadGraph ny default
    you should instead create a tar of your version of MadGraph which includes
    the model file"
echo "-----------------------------------------------------------------------"
wget https://launchpad.net/mg5amcnlo/2.0/2.2.0/+download/MG5_aMC_v2.2.3.tar.gz
mv MG5_aMC_v2.2.3.tar.gz `dirname $0`/transfer_files/madgraph.tar.gz
