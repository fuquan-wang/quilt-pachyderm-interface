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
	parser.add_argument('--table_number',
		type=int,
		required=True,
		help='The number of the table in Quilt data base')
	parser.add_argument('--user_name',
		type=str,
		default='fuquan',
		help='The Quilt user name')
	parser.add_argument('--docker_user',
		type=str,
		default='fuquanwang',
		help='Docker hub user name')
	parser.add_argument('--docker_image',
		type=str,
		default=str(uuid.uuid4()),
		help='The desired docker image name, a UUID will be used as default')
	parser.add_argument('--parallelism',
		type=int,
		default=4,
		help='The number of workers, default is 4')
	return parser

if __name__ == '__main__':
	args = get_parser().parse_args()
	connection = quilt.Connection(args.user_name)
	t = connection.get_table(args.table_number)
	f = t.export()
	f.download()
	filename = str(f.filename)
	s = filename.replace(".","_")
	subprocess.call(['pachctl','create-repo',s])
	subprocess.call(['pachctl','start-commit',s,'master'])
	subprocess.call(['pachctl','put-file',s,'master','data','-f',filename])
	subprocess.call(['pachctl','finish-commit',s,'master'])
	p = subprocess.Popen('wc -l '+filename+' |awk \'{print $1\'}', stdout=subprocess.PIPE, shell=True)
	(nlines, err) = p.communicate()
	subprocess.call(['rm','-f',filename])

	split_pipeline = 'SPLIT_'+s
	nfiles_per_job = 4
	subprocess.call(['python','../splitter/splitter.py',
			'--output_dir', args.output_dir, 
			'--nlines', str(int(nlines)/args.parallelism/nfiles_per_job+1),
			'--input_repo', s,
			'--pipeline', split_pipeline])

	proc_pipeline = 'PROC_'+s
	subprocess.call(['python','../imageCreator/generate.py',
			'--output_dir', args.output_dir, 
			'--req_file', args.req_file,
			'--tar_ball', args.tar_ball,
			'--script_name', args.script_name, 
			'--input_repo', split_pipeline,
			'--docker_user', args.docker_user,
			'--pipeline', proc_pipeline,
			'--docker_image', args.docker_image,
			'--parallelism', str(args.parallelism)])

	jobid=''
	while jobid=='':
		p = subprocess.Popen('pachctl list-job -p '+proc_pipeline+' |grep running |awk \'{print $1}\'', stdout=subprocess.PIPE, shell=True)
		(jobid, err) = p.communicate()
		time.sleep(5)
	jobid = jobid[:-1]

	print 'waiting for job', jobid, 'to finish'
	subprocess.call(['pachctl','inspect-job',jobid,'--block'])
	print 'job', jobid, 'has finished'

	merge_pipeline = 'MERGE_'+s
	subprocess.call(['python','../merger/merger.py',
			'--output_dir', args.output_dir, 
			'--input_repo', proc_pipeline,
			'--pipeline', merge_pipeline])

	p = subprocess.Popen('pachctl list-commit '+merge_pipeline+' |tail -1 |awk \'{print $2}\'', stdout=subprocess.PIPE, shell=True)
	(outputid, err) = p.communicate()
	outputid = outputid[ outputid.index('/')+1 : -1 ]
	print 'pachctl','get-file',merge_pipeline,outputid,'data','>','merge_'+s
	p = subprocess.Popen('pachctl get-file '+merge_pipeline+' '+outputid+' data > merge_'+s, stdout=subprocess.PIPE, shell=True)
	p.communicate()
	f = connection.upload('merge_'+s)
	print f.url
	subprocess.call(['rm','-f','merge_'+s])
