FROM leechengchao/job-shim:latest

# UPDATE reop
RUN apt-get update

# ADD pip package list
ADD requirements.txt /

# Install pip libraries
RUN pip install -U pip setuptools && \
pip install -r /requirements.txt

# Unzip RS2 score
ADD Rule_Set_2_scoring_v1.2.tar.gz /

# ADD script
ADD pachyRun.sh /
RUN chmod 777 /pachyRun.sh

# SET workdir
WORKDIR /Rule_Set_2_scoring_v1.2
