import argparse, sys, os
import subprocess
import quilt
import uuid
import time

def get_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('--output_dir',
		type=str,
		required=True,
		help='The file output directory')
	parser.add_argument('--input_repo',
		type=str,
		required=True,
		help='The name of the input repo')
	parser.add_argument('--pipeline',
		type=str,
		required=True,
		help='The name of the pipeline')
	return parser

if __name__ == '__main__':
	args = get_parser().parse_args()
	output_dir = args.output_dir
	if not os.path.exists( output_dir ):
		os.makedirs( output_dir )

	f = open(output_dir+'/merge.json', 'w')
	f.write('{\n\t"pipeline": {\n\t\t"name": "'+args.pipeline+'"\n\t},\n');
	f.write('\t"transform": {\n\t\t"cmd": [ "sh" ],\n\t\t"stdin": [\n\t\t\t"cat /pfs/'+args.input_repo+'/* > /pfs/out/data"\n\t\t],\n\t\t"image": "fuquanwang/pach-job-shim:latest"\n\t},\n')
	f.write('\t"parallelism_spec": {\n\t\t"strategy": "CONSTANT",\n\t\t"constant": 1\n\t},\n')
	f.write('\t"inputs": [\n\t\t{\n\t\t\t"repo": {\n\t\t\t\t"name": "'+args.input_repo+'"\n\t\t\t}\n\t\t}\n\t]\n}\n')
	f.close()

	subprocess.call(['pachctl', 'create-pipeline', '-f', output_dir+'/merge.json'])

	wait_time=120
	p = subprocess.Popen('pachctl list-job -p '+args.pipeline+' |grep running |awk \'{print $1}\'', stdout=subprocess.PIPE, shell=True)
	(jobid, err) = p.communicate()
	while jobid=='' and wait_time>0:
		p = subprocess.Popen('pachctl list-job -p '+args.pipeline+' |grep running |awk \'{print $1}\'', stdout=subprocess.PIPE, shell=True)
		wait_time -= 5
		time.sleep(5)
		(jobid, err) = p.communicate()

	if( jobid!='' ):
		print 'waiting for job', jobid, 'to finish'
		subprocess.call(['pachctl','inspect-job',jobid,'--block'])
		print 'job', jobid, 'has finished'
