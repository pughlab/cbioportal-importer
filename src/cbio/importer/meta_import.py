__author__ = 'priti'

# ----------------------------------------------------------------------------
# Import
# ----------------------------------------------------------------------------


import argparse
from cbio.core.base import logger
from cbio.core.constants import JAR_PATH, UCSC_BUILD, NCBI_BUILD, SPECIES
import sys

import cbioportal_importer
import validate_data


# ----------------------------------------------------------------------------
# Global variables
# ----------------------------------------------------------------------------

class Color(object):
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------

def interface():
    parser = argparse.ArgumentParser(description='cBioPortal meta Importer')
    parser.add_argument('-s', '--study_directory', type=str, required=True,
                        help='path to directory.')
    portal_mode_group = parser.add_mutually_exclusive_group()
    portal_mode_group.add_argument('-u', '--url_server',
                                   type=str,
                                   default='http://localhost/cbioportal',
                                   help='URL to cBioPortal server. You can '
                                        'set this if your URL is not '
                                        'http://localhost/cbioportal')
    portal_mode_group.add_argument('-p', '--portal_info_dir',
                                   type=str,
                                   help='Path to a directory of cBioPortal '
                                        'info files to be used instead of '
                                        'contacting the web API')
    #  temporary workaround to simplify import process when no web-server is running. TODO: replace by solution for #1466
    portal_mode_group.add_argument('-n', '--no_portal_checks', default=False,
                                       action='store_true',
                                       help='Skip tests requiring information '
                                            'from the cBioPortal installation')
    parser.add_argument('-P', '--portal_properties', type=str,
                        help='portal.properties file path (default: assumed hg19)',
                        required=False)
    parser.add_argument('-g', '--reference_genome', action='store_true',
                        help='load reference genome info from args',
                        required=False)
    parser.add_argument('-jar', '--jar_path', type=str, required=False,
                        help='Path to scripts JAR file (default: $PORTAL_HOME/scripts/target/scripts-*.jar)')
    parser.add_argument('-html', '--html_table', type=str,
                        help='path to html report')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='report status info messages while validating')
    parser.add_argument('-o', '--override_warning', action='store_true',
                        help='override warnings and continue importing')

    parser = parser.parse_args()
    return parser


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    # Parse user input
    args = interface()
    # supply parameters that the validation script expects to have parsed
    args.error_file = False
    if args.reference_genome:
        args.genome_build = UCSC_BUILD
        args.ncbi_build = NCBI_BUILD
        args.species = SPECIES

    if not args.jar_path:
        args.jar_path = JAR_PATH

    study_dir = args.study_directory

    # Validate the study directory.
    logger.info("Starting validation...")
    try:
        exitcode = validate_data.main_validate(args)
    except KeyboardInterrupt:
        logger.info("Process interrupted. " + Color.END)
        logger.info("#" * 71)
        raise
    except:
        logger.error("!" * 71)
        logger.error(Color.RED + "Error occurred during validation step:" + Color.END)
        raise
    finally:
        # make sure all log messages are flushed
        for log_handler in logger.handlers:
            log_handler.close()
        logger.handlers = []

    # Depending on validation results, load the study or notify the user
    try:
        logger.info("#" * 71)
        if exitcode == 1:
            logger.error(Color.RED + "One or more errors reported above. Please fix your files accordingly" + Color.END)
            logger.error("!" * 71)
        elif exitcode == 3:
            if args.override_warning:
                logger.error(Color.BOLD + "Overriding Warnings. Importing study now" + Color.END)
                logger.error("#" * 71)
                cbioportal_importer.main(args)
                exitcode = 0
            else:
                logger.error(Color.BOLD + "Warnings. Please fix your files or import with override warning option" + Color.END)
                logger.error("#" * 71)
        elif exitcode == 0:
            logger.error(Color.BOLD + "Everything looks good. Importing study now" + Color.END)
            logger.error("#" * 71)
            cbioportal_importer.main(args)
    except KeyboardInterrupt:
        logger.info(Color.BOLD + "\nProcess interrupted. You will have to run this again to make sure study is completely loaded." + Color.END)
        logger.info("#" * 71)
        raise
    except:
        logger.error("!" * 71)
        logger.error(Color.RED + "Error occurred during data loading step. Please fix the problem and run this again to make sure study is completely loaded." + Color.END)
        raise
    sys.exit(exitcode)

if __name__ == "__main__":
    main()