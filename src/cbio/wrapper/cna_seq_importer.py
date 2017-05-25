import argparse
from cbio.core.base import logger
import os, glob
from string import Template
from cbio.core.constants import GEN_REF_ID, JAR_PATH

INSTALLATION_ROOT = os.path.dirname(__file__)

def interface():
    parser = argparse.ArgumentParser(description=' Segment data for import into the cBioPortal')
    parser.add_argument('-i', '--study_identifier', type=str, required=True,
                        help='identifier of cancer study.')
    parser.add_argument('-s', '--study_directory', type=str, required=True,
                        help='path to directory.')
    parser.add_argument('-g', '--reference_genome_id', type=str, required=False,
                        help='Reference genome version. Default: assumed hg19)')
    parser.add_argument('-e', '--file_extension', type=str, required=False,
                        help='cna seqment file extension',
                        default="seg")
    parser.add_argument('-desc', '--description', type=str, required=True,
                        help='description on cancer study')
    parser.add_argument('-f', '--seg_data_filename', type=str, required=False,
                        help='cna segment data file', default='data_cna_seg.txt')
    parser.add_argument('-sf', '--sample_data_filename', type=str, required=False,
                        help='sample data file', default='data_samples.txt')
    parser.add_argument('-c', '--create_cast_lists', action='store_true',
                        help='create case list')
    parser.add_argument('-cn', '--case_list_name', type=str, required=False,
                        help='case list name.', default="All Tumors")
    parser = parser.parse_args()
    return parser

def get_template(template_file):

    with open(os.path.join(INSTALLATION_ROOT, "templates", template_file), "r") as fi:
        return Template(fi.read())

def make_meta_file(file_name, content):
    with open(file_name, 'w') as fo:
        fo.write(content)

def main():
    # Parse user input
    args = interface()

    study_dir = args.study_directory
    if args.create_cast_lists:
        from cbio.core import DirectoryExists
        from cbio.utils import make_dirs
        try:
            make_dirs(os.path.join(study_dir, 'case_lists'))
        except DirectoryExists:
            raise
    try:
        sample_list = list()
        # make meta files
        logger.info("generating meta_cna_seg.txt file...")
        meta_content = get_template("meta_cna_seg.txt").substitute(dict(cancer_study_identifier=args.study_identifier,
                              reference_genome_id=args.reference_genome_id if args.reference_genome_id else GEN_REF_ID,
                              description=args.description,
                              data_filename=args.seg_data_filename))
        make_meta_file(os.path.join(args.study_directory, "meta_cna_seg.txt"), meta_content)
        logger.info("generating meta_samples.txt file..")
        meta_content = get_template("meta_samples.txt").substitute(dict(cancer_study_identifier=args.study_identifier,
                              data_filename=args.sample_data_filename))
        make_meta_file(os.path.join(args.study_directory, "meta_samples.txt"), meta_content)

        with open(os.path.join(study_dir, args.seg_data_filename), 'w') as outfile, \
                open(os.path.join(study_dir, args.sample_data_filename), 'w') as outsfile:

            outfile.write('ID\tchrom\tloc.start\tloc.end\tnum.mark\tseg.mean\n')
            outsfile.write('#Patient Identifier\tSample Identifier\tSubtype\n')
            outsfile.write('#Patient identifier\tSample identifier\tSubtype description\n')
            outsfile.write('#STRING\tSTRING\tSTRING\n')
            outsfile.write('#1\t1\t1\n')
            outsfile.write('PATIENT_ID\tSAMPLE_ID\tSUBTYPE\n')

            for fname in glob.iglob(os.path.join(study_dir, '*.{0}'.format(args.file_extension))):
                with open(fname) as f:
                    lines = [line.rstrip('\n').replace('chr','') for line in f]
                for line in lines:
                    if 'ID' in line: continue
                    logger.info("processing {0}".format(line))
                    parts = line.split("\t")
                    items = parts[0].split("_")

                    if parts[0] not in sample_list:
                        sample_list.append(parts[0])
                        outsfile.write('{0}\t{1}\t{2}\n'.format(items[0], parts[0],
                                                    'tumour' if items[1] == 'T' else 'patient-derived cell line'))
                    outfile.write('{0}\n'.format('\t'.join(parts)))


        if args.create_cast_lists and len(sample_list) > 0:
            meta_content = get_template("cases_all.txt").substitute(
                                    dict(cancer_study_identifier=args.study_identifier,
                                        stable_id = "_".join([args.study_identifier,"ALL"]),
                                        case_list_name = args.case_list_name,
                                        case_list_description=args.description,
                                        case_list_ids='\t'.join(sample_list)))
            make_meta_file(os.path.join(study_dir, 'case_lists', 'cases_all.txt'), meta_content)

    except:
        logger.error("!" * 71)
        logger.error("Error occurred during generating meta_cna_seq file")
        raise
    finally:
        # make sure all log messages are flushed
        for log_handler in logger.handlers:
            log_handler.close()
        logger.handlers = []

if __name__ == "__main__":
    main()