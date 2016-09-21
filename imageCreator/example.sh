#!/bin/bash

python generate.py --output_dir /tmp/testOut --req_file ~/docker/V0/requirements.txt --tar_ball ~/docker/V0/Rule_Set_2_scoring_v1.2.tar.gz --script_name runLocal.sh --input_repo DHS30mer --docker_user fuquanwang --pipeline rs2test --docker_image dhs1604
