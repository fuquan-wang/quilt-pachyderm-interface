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
	parser.add_argument('--column_number',
		type=int,
		required=True,
		help='The column number to be top\'ed, index starting from 0')
	parser.add_argument('--score_column',
		type=int,
		default=-1,
		help='The score column of each row, index starting from 0 and in float format')
	parser.add_argument('--integer_score',
		type=int,
		default=0,
		help='The score is an integer, 0 or 1')
	parser.add_argument('--to_lower',
		type=int,
		default=0,
		help='Change the column string to lower case, 0 or 1')
	parser.add_argument('--skip_header',
		type=int,
		default=1,
		help='Skip the header row, 0 or 1')
	return parser

if __name__ == '__main__':
	args = get_parser().parse_args()
	ifile  = open(args.input_file, "rb")
	reader = csv.reader(ifile)

	mydict = {}
	rownumber = 0
	for row in reader:
		if args.skip_header==1 and rownumber==0 :
			rownumber=1
			continue

		col = row[args.column_number]
		score = 1.
		if args.score_column>=0:
			if args.integer_score==1:
				score = int(row[args.score_column])
			else:
				score = float(row[args.score_column])
		if args.to_lower==1:
			col = col.lower()

		if col in mydict:
			mydict[col] = score + mydict[col]
		else:
			mydict[col] = score

	ifile.close()

	ofile = open(args.output_file, 'wb')
	writer = csv.writer(ofile, delimiter=',')
	for key in mydict:
		writer.writerow([key,mydict[key]])
	ofile.close()

