import argparse
from cbio.core.base import logger
import os
from string import Template

INSTALLATION_ROOT = os.path.dirname(__file__)

def interface():
    parser = argparse.ArgumentParser(description='Cancer study meta file for import into the cBioPortal')
    parser.add_argument('-i', '--study_identifier', type=str, required=True,
                        help='identifier of cancer study.')
    parser.add_argument('-s', '--study_directory', type=str, required=True,
                        help='path to directory.')
    parser.add_argument('-t', '--type_of_cancer', type=str, required=True,
                        help='type of cancer)')
    parser.add_argument('-n', '--name', type=str, required=True,
                        help='name of cancer study')
    parser.add_argument('-desc', '--description', type=str, required=True,
                        help='description on cancer study')
    parser.add_argument('-c', '--citation', type=str, required=False,
                        help='cancer study citation')
    parser.add_argument('-p', '--pmid', type=str, required=False,
                        help='cancer study pmid')
    parser.add_argument('-g', '--group', type=str, required=False,
                        help='cancer study group')
    parser.add_argument('-sn', '--short_name', type=str, required=False,
                        help='short name of cancer study')
    parser.add_argument('-a', '--add_global_case_list', action='store_true',
                        help='set global case list to true')

    parser = parser.parse_args()
    return parser


def main():
    # Parse user input
    args = interface()

    study_dir = args.study_directory

    try:
        # open the file
        logger.info("generating meta_study.txt file...")
        sample_list = list()

        with open(os.path.join(INSTALLATION_ROOT, "templates/meta_study.txt"), "r") as fi:
            src = Template(fi.read())

        # do the substitution
        src = src.substitute(dict(type_of_cancer=args.type_of_cancer,
                                  cancer_study_identifier=args.study_identifier,
                                  name=args.name,
                                  description=args.description,
                                  citation=args.citation if args.citation else '',
                                  pmid=args.pmid if args.pmid else '',
                                  groups=args.group,
                                  short_name=args.short_name,
                                  add_global_case_list=args.add_global_case_list))

        with open(os.path.join(study_dir, 'meta_study.txt'), 'w') as fo:
            fo.write(src)

    except:
        logger.error("!" * 71)
        logger.error("Error occurred during generating meta_study file")
        raise
    finally:
        # make sure all log messages are flushed
        for log_handler in logger.handlers:
            log_handler.close()
        logger.handlers = []

if __name__ == "__main__":
    main()