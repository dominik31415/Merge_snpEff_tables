# Merge_snpEff_tables.py
# version 1.0
#
# August 10, 2016
#
# Authors: Dominik Geissler & Hai D.T. Nguyen
# Correspondence: geissler_dominik@hotmail.com, hai.nguyen.1984@gmail.com
#
# This script will read in multiple tables from the output of snpEff, a gene list of all 
# genes in the reference genome and produce a merged table. This is useful for finding the
# genes with high/low number of variants or to count how many variants a gene has across different
# samples.
# 
# REQUIREMENTS
#
# 1. Pandas has to be installed. 
# In Ubuntu, you can install it by typing "sudo apt-get install python-pandas"
# If using MacOS X, you can try this command "sudo easy_install pandas"
#
# 2. Generate tables from snpEff.  The test dataset was generated with SnpEff 4.2.
# (http://snpeff.sourceforge.net)
#
# This script assumes an input of the form:
# python Merge_snpEff_tables.py \
# --input 'strain6602_snpEff_genes_small_dataset.txt' 'strain6574_snpEff_genes_small_dataset.txt' 'strain6686_snpEff_genes_small_dataset.txt' \
# --genes 'gene_list.txt' --output 'merged_datasets.txt'
#
# It assumes 'GeneId','TranscriptId' in gene_list.txt are each only used once 
# The file names of the input is important because the script will generate the merged
# table such that the text before the first underscore (i.e. strain6602, strain6574, strain6686, etc.) will
# will be used to identify where the data comes from.

import argparse
import pandas as pd
#from pandas import DataFrame
#import os

# resolving arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input", dest = 'input_files' , type=str, help="name of an input file, multiple files separated by blank", nargs='*',required=True)
parser.add_argument("--output", dest = 'output_file' , type=str, help="name of the output file", nargs=1,required=True)
parser.add_argument("--genes", dest = 'genes_file' , type=str, help="name of the genes file", nargs=1,required=True)
args = parser.parse_args()


#loading files
selected_properties_1 = ['#GeneName',	'GeneId','TranscriptId'] #name-type entries
selected_properties_2 =['variants_impact_HIGH', 'variants_impact_LOW', 'variants_impact_MODERATE', 'variants_impact_MODIFIER'] #values
data = pd.DataFrame()
for fname in args.input_files:
	h = pd.read_table(fname,engine='python',header=1,usecols=selected_properties_1+selected_properties_2)
	#rename columns to include strain name
	sname,tmp = fname.split("_",1) #assumes file names as 'STRAIN_foobar.txt'
	column_names = { x:(sname+'_'+x) for x in selected_properties_2}
	h = h.rename(index = str, columns = column_names)
	#merge into previus table
	if data.empty:
		data = h
	else:
		data = pd.merge(data,h,how='outer', on = selected_properties_1)

#add other gene list
h = pd.read_table(args.genes_file[0],header=0)
data = pd.concat([data,h],ignore_index=True)
data = pd.DataFrame.drop_duplicates(data,keep='first',subset='GeneId')

#rearrange columns
cols = selected_properties_1  + [x for x in data if not (x in selected_properties_1)]
data = data[cols]

#save data
data.to_csv(path_or_buf=args.output_file[0], sep='\t',index=False)

