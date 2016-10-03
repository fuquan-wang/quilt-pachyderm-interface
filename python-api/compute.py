import sys, os
import subprocess
import quilt
import uuid
import time
import tarfile

class Compute(object):
	def __init__(self, tar_ball, script_name, table_number, output_dir='/tmp/'+str(uuid.uuid4()), 
	docker_user='fuquanwang', docker_image=str(uuid.uuid4()), parallelism=4, mrmethod='simple_map', req_file=''):
		if not os.path.exists( output_dir ):
			os.makedirs( output_dir )
		self._output_dir = output_dir
		self._tar_ball = tar_ball
		self._script_name = os.path.basename(script_name)
		self._table_number = table_number
		self._docker_user = docker_user
		self._docker_image = docker_image
		self._parallelism = parallelism
		self._nlines = '100000000'
		self._input_repo = ''
		if( req_file=='' ):
			dir_path = os.getenv('QUILT_COMPUTE_DIR',os.path.dirname(os.path.realpath(__file__))+'/..')
			req_file = dir_pach+'/txt-templ/requirements.txt'
		self._req_file = req_file
		self._mrmethod = mrmethod 

		p = subprocess.Popen('pachctl version |grep pachctl |awk \'{print $2}\' |cut -f 1 -d\\-', stdout=subprocess.PIPE, shell=True)
		(self._pachy_version, err) = p.communicate()

	def commit_to_pachy(self, connection):
		t = connection.get_table( self._table_number )
		f = t.export()
		f.download()

		filename = str(f.filename)
		self._input_repo = filename.replace(".","_")
		subprocess.call(['pachctl','create-repo',self._input_repo])
		subprocess.call(['pachctl','start-commit',self._input_repo,'master'])
		subprocess.call(['pachctl','put-file',self._input_repo,'master','data','-f',filename])
		subprocess.call(['pachctl','finish-commit',self._input_repo,'master'])

		p = subprocess.Popen('wc -l '+filename+' |awk \'{print $1\'}', stdout=subprocess.PIPE, shell=True)
		(self._nlines, err) = p.communicate()
		subprocess.call(['rm','-f',filename])

	def gen_pipeline_split(self):
		dir_path = os.getenv('QUILT_COMPUTE_DIR',os.path.dirname(os.path.realpath(__file__))+'/..')
		nfiles_per_job = 4
		self._split_pipeline = 'SPLIT_'+self._input_repo
		subprocess.call(['bash', dir_path+'/bash-templ/bugfixer-1.2.0.sh',
				'--input_repo', self._input_repo,
				'--output_repo', self._split_pipeline,
				'--output_file', self._output_dir+'/split.json',
				'--nlines', str(int(self._nlines)/self._parallelism/nfiles_per_job+1),
				'--splitter'])
		subprocess.call(['pachctl', 'create-pipeline', '-f', self._output_dir+'/split.json'])
		subprocess.call(['bash', dir_path+'/bash-templ/monitor.sh',
				'--pipeline_name', self._split_pipeline,
				'--wait_span', '60',
				'--wait_interval', '2'])
	
	def gen_pipeline_merge(self, proc_pipeline):
		dir_path = os.getenv('QUILT_COMPUTE_DIR',os.path.dirname(os.path.realpath(__file__))+'/..')
		self._merge_pipeline = 'MERGE_'+self._input_repo
		subprocess.call(['bash', dir_path+'/bash-templ/bugfixer-1.2.0.sh',
				'--input_repo', proc_pipeline,
				'--output_repo', self._merge_pipeline,
				'--output_file', self._output_dir+'/merge.json',
				'--merger'])
		subprocess.call(['pachctl', 'create-pipeline', '-f', self._output_dir+'/merge.json'])
		subprocess.call(['bash', dir_path+'/bash-templ/monitor.sh',
				'--pipeline_name', self._merge_pipeline,
				'--wait_span', '60',
				'--wait_interval', '2'])
	
	def gen_docker_image(self):
		dir_path = os.getenv('QUILT_COMPUTE_DIR',os.path.dirname(os.path.realpath(__file__))+'/..')

		if not os.path.isfile( self._req_file ) :
			print 'The pip requirement file <' + self._req_file + '> does not exist! Exitting'
			sys.exit(0)
		if not os.path.isfile( self._tar_ball ) :
			print 'The tar ball file <' + self._tar_ball + '> does not exist! Exitting'
			sys.exit(0)
		if self._tar_ball[-4:]!='.tar' and self._tar_ball[-7:]!='.tar.gz' :
			print 'The tar ball file <' + self._tar_ball + '> is not .tar or .tar.gz! Exitting'
			sys.exit(0)
		tar = tarfile.open(self._tar_ball)
		dir_count = 0
		dir_name = ''
		for tarinfo in tar:
			if '/' in tarinfo.name :
				continue
			else : 
				dir_count += 1
				dir_name = tarinfo.name
				if dir_count>1 :
					print 'There are more than 1 top directory in tar ball file <' + self._tar_ball + '>. Exitting'
					sys.exit(0)
		if dir_count==0 :
			print 'There are less than 1 top directory in tar ball file <' + self._tar_ball + '>. Exitting'
			sys.exit(0)

		subprocess.call(['bash', dir_path+'/bash-templ/docker.sh',
				'--tar_ball', self._tar_ball,
				'--script', self._script_name,
				'--workdir', dir_name,
				'--output_file', self._output_dir+'/Dockerfile'])
		subprocess.call(['cp',self._req_file,self._output_dir+'/requirements.txt'])
		subprocess.call(['cp',self._tar_ball,self._output_dir])
		subprocess.call(['cp',dir_path+'/bash-templ/pachyRun.sh',self._output_dir])
		subprocess.call(['docker','build','-t',self._docker_image,self._output_dir])
		subprocess.call(['docker','tag',self._docker_image,self._docker_user+'/'+self._docker_image])
		subprocess.call(['docker','push',self._docker_user+'/'+self._docker_image])

	def gen_pipeline_map(self,input_repo):
		dir_path = os.getenv('QUILT_COMPUTE_DIR',os.path.dirname(os.path.realpath(__file__))+'/..')
		self._proc_pipeline = 'PROC_'+self._input_repo
		subprocess.call(['bash', dir_path+'/bash-templ/map.sh',
				'--input_repo', input_repo,
				'--output_file', self._output_dir+'/proc.json',
				'--parallelism', str(self._parallelism),
				'--docker_user', self._docker_user,
				'--docker_image', self._docker_image,
				'--pipeline_name', self._proc_pipeline])
		subprocess.call(['pachctl', 'create-pipeline', '-f', self._output_dir+'/proc.json'])
		subprocess.call(['bash', dir_path+'/bash-templ/monitor.sh',
				'--pipeline_name', self._proc_pipeline,
				'--wait_span', '1000'])
	
	def upload_to_quilt(self, final_pipeline):
		p = subprocess.Popen('pachctl list-commit '+final_pipeline+' |tail -1 |awk \'{print $2}\'', stdout=subprocess.PIPE, shell=True)
		(outputid, err) = p.communicate()
		outputid = outputid[ outputid.index('/')+1 : -1 ]
		p = subprocess.Popen('pachctl get-file '+final_pipeline+' '+outputid+' data > merge_'+self._input_repo, stdout=subprocess.PIPE, shell=True)
		p.communicate()
		f = connection.upload('merge_'+self._input_repo)
		subprocess.call(['rm','-f','merge_'+self._input_repo])
		return f

	def run_calc(self,connection):
		self.commit_to_pachy(connection)
		self.gen_docker_image()
		if( self._pachy_version<'1.2.1' ):
			self.gen_pipeline_split()
			if( self._mrmethod=='simple_map' ):
				self.gen_pipeline_map(self._split_pipeline)
				self.gen_pipeline_merge(self._proc_pipeline)
				self.upload_to_quilt(self._merge_pipeline)
		else:
			if( self._mrmethod=='simple_map' ):
				self.gen_pipeline_map(self._input_pipeline)
				self.upload_to_quilt(self._proc_pipeline)

####################################################################
# The below is for local testing, please remove them when incooperating into Quilt
###################################################################
import argparse
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
	compute = Compute( output_dir=args.output_dir,
			tar_ball=args.tar_ball,
			script_name=args.script_name,
			table_number=args.table_number,
			docker_user=args.docker_user,
			docker_image=args.docker_image,
			parallelism=args.parallelism,
			mrmethod='simple_map',
			req_file=args.req_file)
	compute.run_calc(connection)
