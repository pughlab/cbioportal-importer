from cbio.core.pgsql import add_cancer_types, add_gene, add_gene_alias
from cbio.core.pgsql import update_gene
from argparse import Namespace
from cbio.core.base import logger
import argparse

def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gene",
                        help="import hugo genes", action="store_true", type=str, required=False)
    parser.add_argument("-c", "--cancer_type",
                        help="import type of cancer", action="store_true")
    parser.add_argument("-a", "--gene_alias",
                        help="import gene alias", action="store_true")
    parser.add_argument("-u", "--update_gene",
                        help="update hugo genes", action="store_true")
    parser.add_argument("-f", "--file",
                        help="path to gene or gene alias or cancer type file", type=str, required=True)
    parser.add_argument("-t", "--test",
                        help="in bebug mode, no records added to the DB", action="store_true")

    return parser, parser.parse_args()

def main():
    parser, args = get_args()

    if args.gene:
        logger.info("gene file: {0}".format(args.file))
        add_gene(args.file)
    elif args.cancer_type:
        logger.info("cancer type file: {0}".format((args.file)))
        add_cancer_types(args.file)
    elif args.gene_alias:
            logger.info("gene alias file: {0}".format(args.file))
            add_gene_alias(args.file)
    elif args.update_gene:
            logger.info("hugo gene file: {0}".format(args.file))
            update_gene(args.file)
    else:
        parser.print_help()
        return

if __name__ == "__main__":
    main()

