import sys, os
import argparse
import csv

def get_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('--output_file',
		type=str,
		required=True,
		help='The output file name')
	parser.add_argument('--input_file',
		type=str,
		required=True,
		help='The input file name')
	parser.add_argument('--number_of_tops',
		type=int,
		default=10,
		help='Number of top elements to be output')
	return parser

if __name__ == '__main__':
	args = get_parser().parse_args()
	ifile  = open(args.input_file, "rb")
	reader = csv.reader(ifile)

	k = args.number_of_tops

	mylist = []
	for row in reader:
		inserted = False
		for idx in range(len(mylist)):
			if mylist[idx][0]<float(row[1]):
				mylist.insert( idx, (float(row[1]),row[0]) )
				inserted = True
		if len(mylist)<k and inserted==False:
			mylist.append( (float(row[1]),row[0]) )
		elif inserted==True:
			mylist = mylist[:-1]

	ofile = open(args.output_file, 'wb')
	for item in mylist:
		ofile.write(item[1]+'\n')
	ofile.close()
