#!/bin/bash
CLUSTER_NAME=pach-cluster
BUCKET_NAME=fuquan-pach
STORAGE_NAME=fuquan-pach-disk

gcloud container clusters delete $CLUSTER_NAME
#gcloud compute firewall-rules delete pachd
gsutil -m rm -r gs://$BUCKET_NAME
gcloud compute disks delete $STORAGE_NAME
