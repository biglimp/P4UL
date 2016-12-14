# README #

### What is this repository for? ###

* This repository contains a wide range of python scripts for data pre- and post-processing.

### How do I get set up? ###

############################
Mandatory steps to make the python-scripts work:
1) Add to $HOME/.bashrc 

export PATH=$HOME/bin:$PATH
export PATH=$HOME/bin/pyPlot:$PATH
export PATH=$HOME/bin/pyFootprint:$PATH
export PATH=$HOME/bin/pyRaster:$PATH
export PATH=$HOME/bin/pyUtils:$PATH
export PATH=$HOME/bin/pyFoam:$PATH
export PATH=$HOME/bin/pyAnalyze:$PATH
export PATH=$HOME/bin/pyMisc:$PATH
export PATH=$HOME/bin/pyNetCDF:$PATH

export PYTHONPATH=$HOME/bin/pyLib/:$PYTHONPATH
export PYTHONPATH=$HOME/bin/netcdfLib/:$PYTHONPATH

2) Go to $HOME/bin and run the following command to make the programs executables:
chmod u+x py*/*.py

Now the scripts can be run everywhere in your system.

#########################
# INSTRUCTIONS for installing virtual environment which includes NETCDF4:

0) Make sure you have the required libraries on your computer:
>> sudo apt-get install libblas-dev liblapack-dev python-scipy libhdf5-dev netcdf-bin 
$$ sudo apt-get install libnetcdf-dev  libjpeg8-dev libfreetype6-dev libpng-dev


1) Install virtualenv-burrito. (Note: If you're behind a proxy, make sure your shell has the proper http_proxy and https_proxy variables set. E.g. export http_proxy=www_your_proxy_address.)
>> curl -sL https://raw.githubusercontent.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh | $SHELL

2) Open a new login shell by issuing a command:
>> bash -l

3) Create a new virtual environment called 'netcdf4':
>> mkvirtualenv netcdf4

4) Install netcdf4 (assuming that openmpi has already been installed) with the following:
>> C_INCLUDE_PATH=/usr/include/mpi pip install netcdf4

This might take awhile ... and you may see some error messages in the output thread concerning numpy, but those (very likely) will not matter.

5) Install matplotlib and scipy:
>> pip install matplotlib
>> pip install scipy

Again, these might take awhile ...

6) From $HOME/.bash_profile cut-and-paste the following contents into $HOME/.bashrc:

# startup virtualenv-burrito
if [ -f $HOME/.venvburrito/startup.sh ]; then
. $HOME/.venvburrito/startup.sh
fi
  

*) Now the virtual environment is complete and the python scripts which utilize netcdf4 libraries can be run after activating the virtual environment with the following command:
>> workon netcdf4

**) Deactivate the virtual environment with:
>> deactivate

If you so choose, you can add the following aliases into $HOME/.bashrc to make your life a bit easier:

alias n4on='workon netcdf4'
alias n4off='deactivate'

#########################

#  Ignore at this point! This is paraview specific and incomplete at the moment.
export PYTHONPATH=$PYTHONPATH:/usr/lib64/paraview/:/usr/lib64/paraview/site-packages/:/usr/lib64/paraview/site-packages/vtk 
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/lib64/paraview"

#########################
### Who do I talk to? ###

* Mikko Auvinen, University of Helsinki / Finnish Meteorological Institute.