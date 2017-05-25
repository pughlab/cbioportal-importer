from cbio.core.pgsql import add_cancer_types, add_gene, add_gene_alias
from cbio.core.pgsql import update_gene
from cbio.core.pgsql import add_chrom_sizes, get_chrom_sizes
from argparse import Namespace
from cbio.core.base import logger
import argparse
import requests
import re

def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--ref_genome",
                        help="load new reference genome", action="store_true")
    parser.add_argument("-c", "--chrom_size",
                        help="load chromosome sizes", action="store_true")
    parser.add_argument('-n', '--genome_name', type=str,
                        help='reference genome build name, e.g. hg38',
                        required=True)
    parser.add_argument("-r", "--read_chrom_size",
                        help="read chromosome sizes from DB", action="store_true")
    parser.add_argument("-t", "--test",
                        help="in bebug mode, no records added to the DB", action="store_true")

    return parser, parser.parse_args()

def main():
    parser, args = get_args()


    if args.chrom_size:
        logger.info("loading chromosome size for {0} reference genome".format(args.genome_name))
        chrom_size_dict = load_chromosome_lengths(args.genome_name)
        if args.genome_name == 'hg38':
            ref_genome_id = 2
        elif args.genome_name == 'mm10':
            ref_genome_id = 3
        else:
            ref_genome_id = 1
        if not args.read_chrom_size:
            try:
                add_chrom_sizes(chrom_size_dict, ref_genome_id)
            except:
                raise Exception("falied to add chromosome size for genome {0}".format(args.genome_name))
        else:
            logger.info("retrieve chromosome size for reference genome {0}".format(args.genome_name))
            try:
                chrom_sizes = get_chrom_sizes(ref_genome_id)
            except:
                raise Exception("failed to retrieve chromosome size for genome {0}".format((args.genome_name)))

def load_chromosome_lengths(genome_build):
    """Get the length of each chromosome from USCS and return a dict.

    The dict will not include unplaced contigs, alternative haplotypes or
    the mitochondrial chromosome.
    """

    chrom_size_dict = {}
    chrom_size_url = (
        'http://hgdownload.cse.ucsc.edu'
        '/goldenPath/{build}/bigZips/{build}.chrom.sizes').format(
        build=genome_build)
    logger.debug("Retrieving chromosome lengths from '%s'",
                 chrom_size_url)
    r = requests.get(chrom_size_url)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise IOError('Error retrieving chromosome lengths from UCSC: ' +
                      e.message)

    for line in r.text.splitlines():
        try:
            # skip comment lines
            if line.startswith('#'):
                continue
            cols = line.split('\t', 1)
            if not (len(cols) == 2 and
                        cols[0].startswith('chr')):
                raise IOError()
            # skip unplaced sequences
            if cols[0].endswith('_random') or cols[0].startswith('chrUn_'):
                continue
            # skip entries for alternative haplotypes
            if re.search(r'_hap[0-9]+$', cols[0]):
                continue
            # skip the mitochondrial chromosome
            if cols[0] == 'chrM':
                continue

            # remove the 'chr' prefix
            chrom_name = cols[0][3:]
            if len(chrom_name) > 2: continue
            try:
                chrom_size = int(cols[1])
            except ValueError:
                raise IOError()
            chrom_size_dict[chrom_name] = chrom_size
        except IOError:
            raise IOError(
                "Unexpected response from {url}: {line}".format(
                    url=chrom_size_url, line=repr(line)))

    return chrom_size_dict