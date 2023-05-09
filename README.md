# Nonlinear and Stochastic Optimization

CBE/ACMS 40499 and 60499 at the University of Notre Dame

Prof. Alexander Dowling (dowlinglab.nd.edu)

https://ndcbe.github.io/optimization


## Configuring local environment to contribute
* Install anaconda: https://www.anaconda.com/
* Create new conda environment: `conda create -n jbook python=3.9`
* Activate new environemnt: `conda activate jbook`
* Install Jupyter Book: `conda install -c conda-forge jupyter-book`
* Install Jupyter Lab: `conda install -c conda-forge jupyterlab`
* Install Pandas: `conda install -c anaconda pandas`
* Install Numpy: `conda install -c anaconda numpy`
* Install matplotlib: `conda install -c anaconda matplotlib`
* Install GHP Import (for publishing with GitHub pages): `conda install -c conda-forge ghp-import`

## Building notebook
To build, run `jb build ../data-and-computing/` when inside the `data-and-computing` folder.
