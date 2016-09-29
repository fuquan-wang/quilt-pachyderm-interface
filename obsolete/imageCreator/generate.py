# The driver file of the various production
import argparse, sys, os
import uuid
import tarfile
from subprocess import call

def get_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('--output_dir',
		type=str,
		required=True,
		help='The file output directory')
	parser.add_argument('--req_file',
		type=str,
		required=True,
		help='The requirements.txt file for `pip install -r`')
	parser.add_argument('--tar_ball',
		type=str,
		required=True,
		help='The tar ball file containing the executable and the dependent files')
	parser.add_argument('--script_name',
		type=str,
		required=True,
		help='The name of the executable')
	parser.add_argument('--input_repo',
		type=str,
		required=True,
		help='The name of the input repo')
	parser.add_argument('--docker_user',
		type=str,
		default='fuquanwang',
		help='Docker hub user name')
	parser.add_argument('--pipeline',
		type=str,
		default=str(uuid.uuid4()),
		help='The desired names of the jobs, a UUID will be used as default')
	parser.add_argument('--docker_image',
		type=str,
		default=str(uuid.uuid4()),
		help='The desired docker image name, a UUID will be used as default')
	parser.add_argument('--use_uuid_filename',
		type=int,
		default=0,
		help='Use UUID as the output file name, otherwise use the same name as input file (default)')
	parser.add_argument('--parallelism',
		type=int,
		default=1,
		help='The number of workers, default is 1')
	return parser

def gen_Dockerfile( args ):
	output_dir = args.output_dir
	if not os.path.exists( output_dir ):
		os.makedirs( output_dir )
	req_file = args.req_file
	if not os.path.isfile( req_file ) :
		print 'The pip requirement file <' + req_file + '> does not exist! Exitting'
		sys.exit(0)
	tar_ball = args.tar_ball
	if not os.path.isfile( tar_ball ) :
		print 'The tar ball file <' + tar_ball + '> does not exist! Exitting'
		sys.exit(0)
	if tar_ball[-4:]!='.tar' and tar_ball[-7:]!='.tar.gz' :
		print 'The tar ball file <' + tar_ball + '> is not .tar or .tar.gz! Exitting'
		sys.exit(0)
	tar = tarfile.open(tar_ball)
	dir_count = 0
	dir_name = ''
	for tarinfo in tar:
		if '/' in tarinfo.name :
			continue
		else : 
			dir_count+=1
			dir_name = tarinfo.name
			if dir_count>1 :
				print 'There are more than 1 top directory in tar ball file <' + tar_ball + '>. Exitting'
				sys.exit(0)
	if dir_count==0 :
		print 'There are less than 1 top directory in tar ball file <' + tar_ball + '>. Exitting'
		sys.exit(0)

	f = open(output_dir+'/Dockerfile', 'w')
	f.write('FROM fuquanwang/pach-job-shim:latest\n\n')
	f.write('# UPDATE reop\nRUN apt-get update\n\n')
	call(['cp',req_file,output_dir+'/requirements.txt'])
	f.write('# ADD pip package list\nADD requirements.txt /\n\n')
	f.write('# Install pip libraries\nRUN pip install -U pip setuptools && \\\npip install -r /requirements.txt\n\n')
	call(['cp',tar_ball,output_dir])
	f.write('# Extract the package\nADD '+os.path.basename(tar_ball)+' /\n\n')
	f.write('# ADD script\nADD pachyRun.sh /\nRUN chmod 777 /pachyRun.sh\n\n')
	f.write('# SET workdir\nWORKDIR /'+dir_name+'\n')
	f.close()

def gen_pachyRun( args ):
	output_dir = args.output_dir
	if not os.path.exists( output_dir ):
		os.makedirs( output_dir )
	script_name = args.script_name
	use_uuid_filename = args.use_uuid_filename
	f = open(output_dir+'/pachyRun.sh', 'w')
	f.write('#!/bin/bash\n\n')
	f.write('if [ $# != 1 ];\nthen\n\techo "Usage: $0 <INPUTREPO>";\n\texit;\nfi\n\n')
	f.write('INPUTREPO=$1\n\n')
	f.write('for file in `ls /pfs/$INPUTREPO/*`; do\n\techo "processing file $file";\n\tcp $file tmpInput;\n\t[ -f tmpOutput ] && rm -f tmpOutput;\n\tsh '+script_name+' tmpInput tmpOutput;\n')
	if use_uuid_filename!=0:
		f.write('\tcp tmpOutput /pfs/out/`uuidgen`;\ndone\n')
	else:
		f.write('\tcp tmpOutput /pfs/out/`basename $file`;\ndone\n')
	f.close()

def gen_pipeline( args ):
	output_dir = args.output_dir
	if not os.path.exists( output_dir ):
		os.makedirs( output_dir )
	input_repo = args.input_repo
	pipeline = args.pipeline
	docker_user = args.docker_user
	docker_image = args.docker_image
	parallelism = args.parallelism
	f = open(output_dir+'/pipeline.json', 'w')
	f.write('{\n')
	f.write('\t"pipeline": {\n\t\t"name": "'+pipeline+'"\n\t},\n')
	f.write('\t"transform": {\n\t\t"cmd": [ "sh" ],\n\t\t"stdin": [\n\t\t\t"/pachyRun.sh '+input_repo+'"\n\t\t],\n\t\t"image": "'+docker_user+'/'+docker_image+':latest"\n\t},\n')
	f.write('\t"parallelism_spec": {\n\t\t"strategy": "CONSTANT",\n\t\t"constant": '+str(parallelism)+'\n\t},\n')
#	f.write('\t"inputs": [\n\t\t{\n\t\t\t"repo": {\n\t\t\t\t"name": "'+input_repo+'"\n\t\t\t},\n\t\t\t"method": {\n\t\t\t\t"partition": "file",\n\t\t\t\t"incremental": "DIFF"\n\t\t\t}\n\t\t}\n\t]\n')
	f.write('\t"inputs": [\n\t\t{\n\t\t\t"repo": {\n\t\t\t\t"name": "'+input_repo+'"\n\t\t\t}\n\t\t}\n\t]\n')
	f.write('}\n')
	f.close()

def run_build_docker( args ):
	output_dir = args.output_dir
	docker_user = args.docker_user
	docker_image = args.docker_image
	call(['docker','build','-t',docker_image,output_dir])
	call(['docker','tag',docker_image,docker_user+'/'+docker_image])
	call(['docker','push',docker_user+'/'+docker_image])

def run_create_pipeline( args ):
	output_dir = args.output_dir
	call(['pachctl','create-pipeline','-f',output_dir+'/pipeline.json'])

if __name__ == '__main__':
	args = get_parser().parse_args()
	gen_pachyRun( args )
	gen_Dockerfile( args )
	gen_pipeline( args )
	run_build_docker( args )
	run_create_pipeline( args )
