# Data Analytics Project
In this project, I will demontrate how to implement a data analytics work by using jupyter notebook with Python libraries, such as pandas, numpy, sciki-learn, scipy, matplotlib, seaborn, etc.
The [notebook](./jupyter_notes/Data_Analytics_Project.ipynb) is stored in the folder of jupyter_notes. The data sets can be found in the folder of datasets. The table of contents is given below.
<h1>Table of Contents<span class="tocSkip"></span></h1>
<div class="toc"><ul class="toc-item"><li><span><span class="toc-item-num">1&nbsp;&nbsp;</span>Introduction: Data Analytics Project</a></span><ul class="toc-item"><li><span><span class="toc-item-num">1.1&nbsp;&nbsp;</span>Dataset</a></span></li><li><span><span class="toc-item-num">1.2&nbsp;&nbsp;</span>Python Library</a></span></li></ul></li><li><span><span class="toc-item-num">2&nbsp;&nbsp;</span>Exploratory Data Loading</a></span><ul class="toc-item"><li><span><span class="toc-item-num">2.1&nbsp;&nbsp;</span>Data Loading</a></span><ul class="toc-item"><li><span><span class="toc-item-num">2.1.1&nbsp;&nbsp;</span>Read in data from csv files</a></span></li></ul></li><li><span><span class="toc-item-num">2.2&nbsp;&nbsp;</span>Data Set Information</a></span><ul class="toc-item"><li><span><span class="toc-item-num">2.2.1&nbsp;&nbsp;</span>Describe for numeric columns</a></span></li><li><span><span class="toc-item-num">2.2.2&nbsp;&nbsp;</span>Histogram of columns</a></span></li><li><span><span class="toc-item-num">2.2.3&nbsp;&nbsp;</span>Value counts for destination column</a></span></li></ul></li></ul></li><li><span><span class="toc-item-num">3&nbsp;&nbsp;</span>Data Engineering</a></span><ul class="toc-item"><li><span><span class="toc-item-num">3.1&nbsp;&nbsp;</span>Generate Sample Data Set</a></span><ul class="toc-item"><li><span><span class="toc-item-num">3.1.1&nbsp;&nbsp;</span>Take samples</a></span></li><li><span><span class="toc-item-num">3.1.2&nbsp;&nbsp;</span>Combine three data sets</a></span></li></ul></li><li><span><span class="toc-item-num">3.2&nbsp;&nbsp;</span>Create Columns based on Existing Ones</a></span><ul class="toc-item"><li><span><span class="toc-item-num">3.2.1&nbsp;&nbsp;</span>Calculate distance for every driving history record</a></span></li><li><span><span class="toc-item-num">3.2.2&nbsp;&nbsp;</span>Determine the directions of driving vehicle</a></span></li><li><span><span class="toc-item-num">3.2.3&nbsp;&nbsp;</span>Calculate how many stops during one driving history</a></span></li><li><span><span class="toc-item-num">3.2.4&nbsp;&nbsp;</span>Calculate how fuel was added and purchased</a></span></li></ul></li><li><span><span class="toc-item-num">3.3&nbsp;&nbsp;</span>Extract Data Set for Machine Learning Use</a></span><ul class="toc-item"><li><span><span class="toc-item-num">3.3.1&nbsp;&nbsp;</span>Query data set</a></span></li><li><span><span class="toc-item-num">3.3.2&nbsp;&nbsp;</span>Data Set Profiling</a></span></li></ul></li><li><span><span class="toc-item-num">3.4&nbsp;&nbsp;</span>Data Exploration for Trending</a></span><ul class="toc-item"><li><span><span class="toc-item-num">3.4.1&nbsp;&nbsp;</span>Column distributions</a></span></li><li><span><span class="toc-item-num">3.4.2&nbsp;&nbsp;</span>Column distributions by different countries</a></span></li><li><span><span class="toc-item-num">3.4.3&nbsp;&nbsp;</span>Numerical correlations</a></span></li></ul></li><li><span><span class="toc-item-num">3.5&nbsp;&nbsp;</span>Generate Training and Testing Data Sets</a></span><ul class="toc-item"><li><span><span class="toc-item-num">3.5.1&nbsp;&nbsp;</span>Select most correlated 3 columns</a></span></li><li><span><span class="toc-item-num">3.5.2&nbsp;&nbsp;</span>Plots of Selected Columns Correlation Coefficient</a></span></li></ul></li></ul></li><li><span><span class="toc-item-num">4&nbsp;&nbsp;</span>Predictive Analytics with Machine Learning Approaches</a></span><ul class="toc-item"><li><span><span class="toc-item-num">4.1&nbsp;&nbsp;</span>Setup Metrics</a></span></li><li><span><span class="toc-item-num">4.2&nbsp;&nbsp;</span>Setup Baseline</a></span></li><li><span><span class="toc-item-num">4.3&nbsp;&nbsp;</span>Machine Learning Approaches</a></span></li><li><span><span class="toc-item-num">4.4&nbsp;&nbsp;</span>Visual Comparison of ML Approaches</a></span></li><li><span><span class="toc-item-num">4.5&nbsp;&nbsp;</span>Interpretable Formula with Ordinary Linear Regression</a></span></li></ul></li><li><span><span class="toc-item-num">5&nbsp;&nbsp;</span>Conclusions</a></span></li><li><span><span class="toc-item-num">6&nbsp;&nbsp;</span>Future Work</a></span></li></ul></div>

# Environmental Setup

## Prerequisite Installation & Configuration On Linux

## Hardware Environment
* 8 GB Memory
* 2.60GHz 2 Cores CPU
* 250 GB Hard Disck

### Install Linux Ubuntu

* [Ubuntu Linux 18.04 LTS](https://www.ubuntu.com/download/desktop)
* [Windows Subsystem for Linux - Ubuntu](https://docs.microsoft.com/en-us/windows/wsl/install-win10)

### Install Python 3.X
```shell
    # sudo add-apt-repository ppa:jonathonf/python-3.6
    sudo apt update
    sudo apt install python3

    sudo apt install python3-pip python-dev build-essential
    sudo pip3 install --upgrade pip
    sudo pip3 install --upgrade virtualenv
```
### Install Spark
```shell
    # check Java version
    java -version
    sudo apt update
    sudo apt install default-jre
    sudo apt install default-jdk

    # download latest spark and untar it
    wget -P /tmp/ http://apache.osuosl.org/spark/spark-2.4.0/spark-2.4.0-bin-hadoop2.7.tgz
    sudo mkdir /usr/local/spark/
    sudo tar xvf /tmp/spark-2.4.0-bin-hadoop2.7.tgz -C /usr/local/spark
    
    # installing pyspark with pip
    sudo pip3 install pyspark
```
### Install Git for Source Version Control
```shell
sudo apt install git-all
# or install light version
sudo apt install git
```
### Install a Hadoop Single Node Cluster
Please following the instructions at [apache.org](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SingleCluster.html) to setup a single node hadoop cluster.

### Install VS Code and Pycharm
```shell
    # Virtual Studio Code
    curl -O https://go.microsoft.com/fwlink/?LinkID=760868
    sudo apt update
    sudo dpkg -i <file>.deb
    sudo apt-get install -f
    
    # Pycharm Community Edition
    wget -P /tmp/ https://download.jetbrains.com/python/pycharm-community-2018.2.4.tar.gz
    sudo snap install pycharm-community --classic
    # Or install PyCharm with tar and pycharm.sh
    tar xfz pycharm-*.tar.gz -C /usr/local/pycharm
    cd /usr/local/pycharm/pycharm-*/bin
    sh pycharm.sh
```

### Install MySQL
```shell
    sudo apt update
    sudo apt install mysql-server
    # For fresh installations, runt eh included security script to change some of less secure default options
    sudo mysql_secure_installation
    sudo pip3 pymysql
    sudo pip3 install mysql-connector-python
```
To start, stop, restart and enable MySQL at reboot, use
```shell
    sudo systemctl stop mysql
    sudo systemctl start mysql
    sudo systemctl restart mysql
    sudo systemctl enable mysql
    sudo systemctl status mysql
```
or use
```shell
    sudo service mysql start
    sudo service mysql stop
    sudo service mysql restart
    sudo service mysql status
```
To connect MySQL locally, use
```shell
    sudo mysql -u root -p
```
### Install SQL Server 2017 on Ubuntu 16.04 LTS as Optional
Note: the Windows Subsystem for Linux for Windows 10 is not supported as an installation target.
```shell
    sudo apt update
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
    sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/16.04/mssql-server-2017.list)"
    # Register the Microsoft Ubuntu repository.
    curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list
    sudo apt install -y mssql-server
    sudo /opt/mssql/bin/mssql-conf setup
    sudo apt update
    sudo apt install mssql-tools unixodbc-dev
    # A cross-platform command-line interface for running Transact-SQL commands.
    sudo apt install mssql-cli # or pip3 install mssql-cli
```
To start, stop, restart and enable SQL Server at reboot, use
```shell
    sudo systemctl stop mssql-server
    sudo systemctl start mssql-server
    sudo systemctl restart mssql-server
    sudo systemctl enable mssql-server
    sudo systemctl status mssql-server
```
or use
```shell
    sudo service mssql-server start
    sudo service mssql-server stop
    sudo service mssql-server restart
    sudo service mssql-server status
```
To connect SQL Server locally, use
```shell
    sqlcmd -S localhost -U SA -p
```
To use mssql-cli, use
```shell
    mssql-cli -S localhost -U sa -d <database>
```
### Install ipython & jupyter
```shell
    sudo pip3 install jupyter
```
iPython Data Science and Engineering Tools Installation
```shell
    sudo pip3 install numpy pandas scipy tensorflow pymc3
    sudo pip3 install -U scikit-learn
    sudo pip3 install matplotlib seaborn clarify findspark 
    # install optimuspyspark for all
    sudo pip3 install optimuspyspark
    sudo pip3 install sqlalchemy
    sudo pip3 install pandas-profiling
    sudo pip3 install spark-df-profiling
    # Optional: install ipython-sql to enable sql adaptible
    sudo pip3 install ipython-sql
    # Optional: install jupyter extensions
    sudo pip3 install jupyter_contrib_nbextensions # for python 3
    sudo pip install jupyter_contrib_nbextensions # for python 2 if your ipython jupyter support both 2 & 3
    sudo pip3 install autopep8 # for enable autopep8 extension
    sudo jupyter contrib nbextension install --user
    sudo chmod 777 ~/.jupyter/nbconfig/notebook.json # grant juypter extension to write data in this json file to load extensions later
```
The eventual installed python packages include: pytz, python-dateutil, numpy, pandas, findspark, h5py, setuptools, kiwisolver, pyparsing,cycler, matplotlib, scipy, seaborn, keras-applications, keras-preprocessing, keras, pillow, pyarrow, multipledispatch, wrapt, deprecated, pyspark, atomicwrites, pluggy, py, more-itertools, pytest, nose, tabulate, ratelimit, ipython, vine, amqp, kombu, requests, pika, pymongo, backoff, itsdangerous, Werkzeug, flask, humanize, future, colorama, h2o-pysparkling-2.3, psutil, fastnumbers, protobuf, markdown, tensorboard, grpcio, termcolor, astor, gast, absl-py, tensorflow, tqdm, optimuspyspark, clarify, sqlalchemy, ipython-sql

### Validating ipython jupyter notebook
For validating if jupyter notebook is working well with SQL, Python and Shell commands, you can run the [Notebook_Validation.ipynb](./jupyter_notes/Notebook_Validation.ipynb) notebook.


# Appendix - Install Anaconda on Linux for light data science and engineering tools
```shell
    # Step 1: Download Anaconda bash script
    curl -O https://repo.anaconda.com/archive/Anaconda3-5.2.0-Linux-x86_64.sh

    # Step 2: Verify the data integrity of the installer
    sha256sum Anaconda3-5.2.0-Linux-x86_64.sh

    # Step 3: Run the Anaconda script and complete installation process as prompted
    bash Anaconda3-5.2.0-Linux-x86_64.sh

    # Step 4: Activate and test installation
    source ~/.bashrc
    conda list

    # Step 5: Setup Anaconda environments
    conda create --name my_env python=3
    source activate my_env
```

# Appendix - BASH Configuration
    In the ~/.bashrc file, add 
```bash
    export DISPLAY=localhost:0.0
    alias pycharm="/mnt/c/'Program Files'/JetBrains/'PyCharm Community Edition 2018.2.4'/bin/pycharm64.exe"
    alias jupyter-notebook="~/.local/bin/jupyter-notebook --no-browser"
    alias vscode="/mnt/c/Users/yaohua.chen/AppData/Local/Programs/'Microsoft VS Code'/Code.exe"
    SPARK_HOME=/usr/local/spark/spark-2.4.0-bin-hadoop2.7
    export SPARK_HOME=$SPARK_HOME
    export PATH=$SPARK_HOME/bin:$PATH
```
    and then use the command
```
    source ~/.bashrc
```
    to activate the config then type the command
```shell
    jupyter-notebook
```
    to start jupyter notebook service. Copy the prompted jupyter URL or use 127.0.0.1:8888 to access web UI.
    Then use 
```shell
    pyspark 
```
    to access spark shell in python and use
```shell
    sh $SPARK_HOME/sbin/start-all.sh
```
    to start the spark service. The web ui will be available at 127.0.1.1:8080 port.

# Appendix - Vim Configuration    
* Use the [vimrc](./vim/vimrc) in the folder [vim](vim/) to replace `~/.vim/vimrc`

# Appendix - Install web Scrape tools
```shell
    sudo pip3 install scrapy beautifulsoup4
```