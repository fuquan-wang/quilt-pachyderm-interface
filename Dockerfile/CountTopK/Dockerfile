FROM fuquanwang/pach-job-shim:latest

# UPDATE reop
RUN apt-get update

# ADD pip package list
ADD quilt-count.py  quilt-topK.py  reduce-count.sh  reduce-topK.sh  single-proc-count.sh /

# SET workdir
WORKDIR /
