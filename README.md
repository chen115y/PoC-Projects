# Distributed Memory based Data Engineering and Architecture Design 
## - with Apache Ignite and Spark
An instructional document for distributed & memory based data engineering (ETL) with Apache Ignite and Spark

## 1. What is Data Engineering and Data Architecture Design?

### 1.1 Conventional approach

### 1.2 Issues with big data

## 2. Why Distributed Memory based Data Engineering?

### 2.1 Differences between conventional approach and this one

### 2.2 Pros and Cons

## 3. Get Started

### 3.1 Spark Installation

### 3.2 Ignite Installation

### 3.3 Development Tools

#### 3.3.1 Jupyter Notebook with Spark
Link jupyter notebook with Spark (pyspark)
```python
    import findspark
    findspark.init()
    import pyspark
```

## Appendix 1 - Python 3.X Installation
### Use Apt on Ubuntu
```shell
    # Step 1: install python 3.X
    # sudo add-apt-repository ppa:jonathonf/python-3.6
    sudo apt update
    sudo apt install python3

    # Step 2: install pip and virtual environment
    sudo apt install python3-pip python-dev build-essential
    sudo pip install --upgrade pip
    sudo pip install --upgrade virtualenv

    # Step 3: install ipython & jupyter
    sudo apt install ipython3
    sudo pip3 install jupyter
    
    # Step 4: install Virtual Studio Code or PyCharm Community Edition
    
    # Download and install VS Code
    curl -O https://go.microsoft.com/fwlink/?LinkID=760868
    sudo apt update
    sudo dpkg -i <file>.deb
    sudo apt-get install -f
    
    # Download pycharm
    wget -P /tmp/ https://download.jetbrains.com/python/pycharm-community-2018.2.4.tar.gz
    
    # Install PyCharm with snap
    sudo snap install pycharm-community --classic
    # Or install PyCharm with tar and pycharm.sh
    tar xfz pycharm-*.tar.gz -C /usr/local/pycharm
    cd /usr/local/pycharm/pycharm-*/bin
    sh pycharm.sh
```
In the ~/.bashrc file, add 
```bash
    alias jupyter-notebook="~/.local/bin/jupyter-notebook --no-browser"
```
then type the command
```shell
    jupyter-notebook
```
to start jupyter notebook service. Use 127.0.0.1:8888 to access web UI.

## Appendix 2 - Spark Installation
### Use Apt on Ubuntu
```shell
    # Step 1: Install Java
    # check Java version
    java -version
    sudo apt update
    sudo apt install default-jre
    sudo apt install default-jdk

    # Step 2: Install Python
    See Appendix 1 - Python 3.X Installation

    # Step 3: Instal Spark
    sudo apt install git
    
    # download latest spark and untar it
    wget -P /tmp/ http://apache.osuosl.org/spark/spark-2.4.0/spark-2.4.0-bin-hadoop2.7.tgz
    sudo mkdir /usr/local/spark/
    sudo tar xvf /tmp/spark-2.4.0-bin-hadoop2.7.tgz -C /usr/local/spark
    
    # installing pyspark with pip
    sudo pip3 install pyspark
    
    # add snippet of SPARK_HOME to the bash file
    vim ~/.bashrc 
    
    # then type: 
        SPARK_HOME = /usr/local/spark/spark-2.4.0-bin-hadoop2.7/
        export PATH = $SPARK_HOME/bin:$PATH
    source ~/.bashrc
```
Then use 
```shell
    pyspark 
```
to access spark shell in python and use
```shell
    sh $SPARK_HOME/sbin/start-all.sh
```
to start the spark service. The web ui will be available at 127.0.1.1:8080 port


## Appendix 3 - Python Data Science and Engineering Tools Installation
### Use Pip (after Python 3.X installation above)
```shell
    sudo pip3 install numpy pandas scipy tensorflow
    sudo pip3 install -U scikit-learn
    sudo pip3 install matplotlib seaborn findspark
    # or install optimuspyspark for all
    sudo pip3 install optimuspyspark  
```
The eventual installed python packages include: pytz, python-dateutil, numpy, pandas, findspark, h5py, setuptools, kiwisolver, pyparsing,cycler, matplotlib, scipy, seaborn, keras-applications, keras-preprocessing, keras, pillow, pyarrow, multipledispatch, wrapt, deprecated, pyspark, atomicwrites, pluggy, py, more-itertools, pytest, nose, tabulate, ratelimit, ipython, vine, amqp, kombu, requests, pika, pymongo, backoff, itsdangerous, Werkzeug, flask, humanize, future, colorama, h2o-pysparkling-2.3, psutil, fastnumbers, protobuf, markdown, tensorboard, grpcio, termcolor, astor, gast, absl-py, tensorflow, tqdm, optimuspyspark

### Use Anaconda on Linux:
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
### Use Anaconda on Windows
Step 1: Download anaconda executable (.exe) from the website of https://www.anaconda.com/download/#windows

Step 2: Follow the installation wizard to install python and related libraries step-by-step
