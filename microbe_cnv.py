#!/usr/bin/python

__version__ = '0.0.1'

# TO DO
# import microbe_species module

# Libraries
# ---------
import sys
import os
import numpy as np
import argparse
import pysam
import gzip
import time
import subprocess
import operator
import Bio.SeqIO

# Functions
# ---------
def parse_arguments():
	""" Parse command line arguments """
	
	parser = argparse.ArgumentParser(
		description='Estimate the copy-number of genes in reference genomes from metagenomic data',
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	
	parser.add_argument('--version', action='version', version='MicrobeCNV %s' % __version__)
	
	input = parser.add_argument_group('Input')
	input.add_argument('-1', type=str, dest='m1', help='FASTQ file containing 1st mate')
	input.add_argument('-2', type=str, dest='m2', help='FASTQ file containing 2nd mate')
	input.add_argument('-U', type=str, dest='r', help='FASTQ file containing unpaired reads')
	input.add_argument('-p', type=str, dest='profile', help='Estimated species abundance profile')
	input.add_argument('--db-dir', type=str, dest='db_dir', help='Directory of bt2 indexes for each species')
	
	input = parser.add_argument_group('Output')
	input.add_argument('-o', type=str, dest='out_bn', help='Base name for output files')
	
	input = parser.add_argument_group('Alignment')
	input.add_argument('--max-reads', type=int, dest='max_reads', help='Maximum number of reads to use from seqeunce file')
	
	input = parser.add_argument_group('Genome-clusters')
	input.add_argument('--min-abun', type=float, dest='min_abun', default=0.05,
		help='Abundance threshold for inclusion of genome cluster')
	
	return vars(parser.parse_args())

def check_arguments(args):
	""" Check validity of command line arguments """
	if not args['out_bn']:
		sys.exit('Specify output basename with -o')
	if (args['m1'] or args['m2']) and args['r']:
		sys.exit('Cannot use both -1/-2 and -U')
	if (args['m1'] and not args['m2']) or (args['m2'] and not args['m1']):
		sys.exit('Must specify both -1 and -2 for paired-end reads')
	if not (args['m1'] or args['r']):
		sys.exit('Specify reads using either -1 and -2 or -U')
	if not args['profile']:
		sys.exit('Specify species profile file with -p')
	if args['m1'] and not os.path.isfile(args['m1']):
		sys.exit('Input file specified with -1 does not exist')
	if args['m2'] and not os.path.isfile(args['m2']):
		sys.exit('Input file specified with -2 does not exist')
	if args['r'] and not os.path.isfile(args['r']):
		sys.exit('Input file specified with -U does not exist')
	if args['profile'] and not os.path.isfile(args['profile']):
		sys.exit('Input file specified with -p does not exist')
	if args['db_dir'] and not os.path.isdir(args['db_dir']):
		sys.exit('Input directory specified with --db-dir does not exist')

def parse_profile(args):
	""" Parse output from MicrobeSpecies """
	infile = open(args['profile'])
	next(infile)
	for line in infile:
		fields = [
			('cluster_id', str), ('mapped_reads', int), ('prop_mapped', float),
			('cell_count', float), ('prop_cells', float), ('avg_pid', float)]
		values = line.rstrip().split()
		yield dict( [ (f[0], f[1](v)) for f, v in zip(fields, values)] )

def select_genome_clusters(args):
	""" Select genome clusters to map to """
	cluster_ids = []
	for rec in parse_profile(args):
		if rec['prop_cells'] >= args['min_abun']:
			cluster_ids.append(rec['cluster_id'])
	return cluster_ids

def map_reads(cluster_id, index_bn):
	""" Use bowtie2 to map reads to reference genome cluster """
	# Build command
	command = 'bowtie2 --no-unal --very-sensitive -x %s ' % index_bn
	#   max reads to search
	if args['max_reads']: command += '-u %s ' % args['max_reads']
	#   input files
	if args['m1']: command += '-1 %s -2 %s ' % (args['m1'], args['m2'])
	else: command += '-U %(r)s ' % args['r']
	#   output
	command += '| samtools view -b - > %s' % '.'.join([args['out_bn'], cluster_id, 'bam'])
	# Run command
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = process.communicate()

def maps_reads_all_clusters(genome_clusters)
	""" Use Bowtie2 to map reads to all specified genome clusters """
	for cluster_id in genome_clusters:
		index_dir = os.path.join(args['db_dir'], cluster_id)
		index_bn = os.path.join(index_dir, cluster_id)
		if not os.path.isdir(index_dir):
			print("Warning: Bowtie2 index for %s was not found. Skipping." % cluster_id)
		else:
			map_reads(cluster_id, index_bn)

# Main
# ------

args = parse_arguments()
check_arguments(args)

genome_clusters = select_genome_clusters(args)
maps_reads_all_clusters(genome_clusters)

#
#def map_reads_cushaw(args, paths):
#	""" Use cushaw3 to map reads in fastq file to marker database """
#	command = "%(c3)s align -r %(db)s -f %(m1)s | %(st)s view -b - > %(out)s.bam 2> %(out)s.log"
#	arguments = {'c3':paths['cushaw3'],'db':paths['cushaw3db'],'m1':args['m1,'m2':args['m2,'st':paths['samtools'],'out':args['out}
#	process = subprocess.Popen(command % arguments, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#	out, err = process.communicate()
#
#def fastq_to_fasta(args, paths):
#	""" Use cushaw3 to map reads in fastq file to marker database """
#	infile = gzip.open(args['m1) if args['m1.split('.')[-1] == 'gz' else open(args['m1)
#	outfile = open('%s.fa' % args['out, 'w')
#	for rec in Bio.SeqIO.parse(infile, 'fastq'):
#		outfile.write('>'+rec.id+'\n'+str(rec.seq)+'\n')
#
#def map_reads_blast(args, paths):
#	""" Use blastn to map reads in fasta file to marker database """
#	command = "%(blastn)s -query %(query)s -db %(db)s -out %(out)s -outfmt 6"
#	arguments = {'blastn':paths['blastn'], 'query':'%s.fa' % args['out, 'db':paths['blastdb'], 'out':'%s.m8' % args['out}
#	process = subprocess.Popen(command % arguments, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#	out, err = process.communicate()
#
#def parse_blast(inpath):
#	""" Yield formatted record from BLAST m8 file """
#	formats = [str,str,float,int,float,float,float,float,float,float,float,float]
#	fields = ['query','target','pid','aln','mis','gaps','qstart','qend','tstart','tend','evalue','score']
#	infile = open(inpath)
#	for line in infile:
#		values = line.rstrip().split()
#		yield dict([(field, format(value)) for field, format, value in zip(fields, formats, values)])
#
#def find_best_hits(args, paths):
#	""" Find top scoring alignment for each read """
#	best_hits = {}
#	if args['bam:
#		aln_file = pysam.AlignmentFile(args['bam if args['bam else '%s.bam' % args['out, "rb")
#		for aln in aln_file.fetch(until_eof = True):
#			if aln.is_unmapped:
#				continue
#			elif aln.query_name not in best_hits:
#				best_hits[aln.query_name] = aln
#			elif dict(aln.tags)['AS'] > dict(best_hits[aln.query_name].tags)['AS']:
#				best_hits[aln.query_name] = aln
#	elif args['m8:
#		min_pid = 0.80
#		max_evalue = 1e-5
#		for aln in parse_blast(args['m8):
#			if aln['evalue'] > max_evalue or aln['pid'] < min_pid:
#				continue
#			elif aln['query'] not in best_hits:
#				best_hits[aln['query']] = aln
#			elif best_hits[aln['query']]['score'] < aln['score']:
#				best_hits[aln['query']] = aln
#	return best_hits.values()
#
#def aggregate_alignments(args, paths, alns):
#	""" Group all alignments to each genome cluster """
#	cluster_to_aln = dict([(x.rstrip(),[]) for x in open(paths['clusters']).readlines()])
#	if args['bam:
#		aln_file = pysam.AlignmentFile(args['bam if args['bam else '%s.bam' % args['out, "rb")
#		for aln in alns:
#			cluster_id, genome_id, gene_id, marker_id = aln_file.getrname(aln.reference_id).split('_')
#			cluster_to_aln[cluster_id].append(aln)
#	elif args['m8:
#		for aln in alns:
#			cluster_id, genome_id, gene_id, marker_id = aln['target'].split('_')
#			cluster_to_aln[cluster_id].append(aln)
#	return cluster_to_aln
#
#def compute_avg_mapq(args, alns):
#	""" Compute average map quality for list of alignments """
#	if len(alns) == 0:
#		return 'NA'
#	elif args['bam:
#		return np.mean([1 - dict(aln.tags)['NM']/float(aln.query_length) for aln in alns])
#	elif args['m8:
#		return 'NA'
#
#def compute_avg_pid(args, alns):
#	""" Compute average percent identity for list of alignments """
#	if len(alns) == 0:
#		return 'NA'
#	elif args['bam:
#		return np.mean([1 - dict(aln.tags)['NM']/float(aln.query_length) for aln in alns])
#	elif args['m8:
#		return np.mean([aln['pid']/float(100) for aln in alns])
#
#def alignment_summary(cluster_to_aln, args):
#	""" Write summary to outfile """
#	outfile = open(args['out+'.summary', 'w')
#	fields = ['cluster_id', 'mapped_reads', 'relabun', 'avg_pid', 'avg_mapq']
#	outfile.write('\t'.join(fields)+'\n')
#	total_mapped = sum([len(aln) for aln in cluster_to_aln.values()])
#	for cluster_id, alns in cluster_to_aln.items():
#		mapped_reads = len(alns)
#		relabun = len(alns)/float(total_mapped)
#		avg_pid = compute_avg_pid(args, alns)
#		avg_mapq = compute_avg_mapq(args, alns)
#		record = [str(x) for x in [cluster_id, mapped_reads, relabun, avg_pid, avg_mapq]]
#		outfile.write('\t'.join(record)+'\n')
