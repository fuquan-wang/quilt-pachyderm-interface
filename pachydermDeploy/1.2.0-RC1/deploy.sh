#!/bin/bash
CLUSTER_NAME=pach-cluster
GCP_ZONE=us-west1-b

gcloud config set compute/zone ${GCP_ZONE}
gcloud config set container/cluster ${CLUSTER_NAME}

# By default this spins up a 3-node cluster. You can change the default with `--num-nodes VAL`
gcloud container clusters create ${CLUSTER_NAME} --scopes storage-rw
gcloud container clusters get-credentials ${CLUSTER_NAME}

kubectl get all

# BUCKET_NAME needs to be globally unique across the entire GCP region
BUCKET_NAME=fuquan-pach

# Name this whatever you want, we chose pach-disk as a default
STORAGE_NAME=fuquan-pach-disk

# For a demo you should only need 10 GB. This stores PFS metadata. For reference, 1GB
# should work for 1000 commits on 1000 files.
STORAGE_SIZE=200

gsutil mb gs://${BUCKET_NAME}
gcloud compute disks create --size=${STORAGE_SIZE}GB ${STORAGE_NAME}

gcloud compute instances list
# should see a number of instances

gsutil ls
# should see a bucket

gcloud compute disks list
# should see a number of disks, including the one you specified

#pachctl deploy google ${BUCKET_NAME} ${STORAGE_NAME} ${STORAGE_SIZE}

#kubectl get all

kubectl create -f test.json
