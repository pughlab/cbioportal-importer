# _*_ coding:utf-8 _*_

import json
from cbio.core.orm import CancerType
from cbio.core.orm import GeneticEntity, Gene, GeneAlias
from cbio.core.orm import ReferenceGenome, ChromSize
from sqlalchemy import or_, and_, func, desc
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from cbio.core.orm import session_scope
from cbio.core import CancerTypeError
from cbio.core import GeneError, GeneAliasError
from cbio.core import ChromSizeError
from datetime import timedelta, datetime
from cbio.core.base import logger

def get_entrez_gene(ENTREZ_GENE_ID, HUGO_GENE_SYMBOL):
    """
    retrieve gene for a given ENTREZ_GENE_ID
    
    :param: GENE_ALIAS (string) - gene alias for a given gene
    :returns: ENTREZ_GENE_ID if record found otherwise None
    
    """
    with session_scope() as session:
        try:
            return session.query(Gene).filter(Gene.ENTREZ_GENE_ID == int(ENTREZ_GENE_ID))\
                .filter(Gene.HUGO_GENE_SYMBOL == HUGO_GENE_SYMBOL).one()
        except NoResultFound, MultipleResultsFound:
            raise GeneError("No or multiple gene records found: {0}".format(ENTREZ_GENE_ID))


def get_cancer_type(TYPE_OF_CANCER_ID):
    """
    retrieve type_of_cancer for a given TYPE_OF_CANCER_ID

    :param: TYPE_OF_CANCER_ID (Integer) - ID of TYPE_OF_CANCER
    :returns: type_of_cancer record

    """
    with session_scope() as session:
        try:
            return session.query(CancerType) \
                .filter(CancerType.TYPE_OF_CANCER_ID == TYPE_OF_CANCER_ID).one()
        except NoResultFound:
            return None
        except MultipleResultsFound:
            raise CancerTypeError("No or multiple type_of_cancer records found.",TYPE_OF_CANCER_ID)

def gene_exist(ENTREZ_GENE_ID, HUGO_GENE_SYMBOL):
    """
    check if any raw sequence file records exist for a given libcore
    
    :param: ENTREZ_GENE_ID (integer) - ID of ENTREZ_GENE, mandatory
    :param: HUGO_GENE_SYMBOL (String) - HUGO GENE SYMBOL, mandatory
    :returns: True if the record exists, False otherwise
    
    """
    with session_scope() as session:
        try:
            session.query(Gene)\
                    .filter(Gene.ENTREZ_GENE_ID == ENTREZ_GENE_ID) \
                    .filter(Gene.HUGO_GENE_SYMBOL == HUGO_GENE_SYMBOL).one()
            return True
        except NoResultFound:
            return False
        except MultipleResultsFound:
            raise GeneError("Multiple gene records found.", ENTREZ_GENE_ID, HUGO_GENE_SYMBOL)


def gene_alias_exist(ENTREZ_GENE_ID, GENE_ALIAS):
    """
    check if any raw sequence file records exist for a given libcore

    :param: ENTREZ_GENE_ID (integer) - ID of ENTREZ_GENE, mandatory
    :param: GENE_ALIAS (String) - GENE_ALIAS, mandatory
    :returns: True if the record exists, False otherwise

    """
    with session_scope() as session:
        try:
            q = session.query(GeneAlias).filter(GeneAlias.ENTREZ_GENE_ID == int(ENTREZ_GENE_ID))\
                .filter(GeneAlias.GENE_ALIAS == str(GENE_ALIAS))
            return (q.first() != None)
        except NoResultFound:
            return False

def _add_genetic_entity(ENTITY_TYPE="GENE"):
    with session_scope() as session:
        try:
            rs = GeneticEntity()
            rs.ENTITY_TYPE = ENTITY_TYPE
            session.add(rs)
            session.commit()
            return rs.ID
        except Exception as e:
            raise GeneError("falied to add a new genetic entity with ENTITY_TYPE {0} ".format(ENTITY_TYPE))


def _add_gene(GENETIC_ENTITY_ID, ENTREZ_GENE_ID, HUGO_SYMBOL, LENGTH=None, CYTOBAND=None):
    """
    add a new record to the gene table from a give gene

    :param: ENTREZ_GENE_ID (Integer) - ENTREZ GENE ID, mandatory
    :param: GENETIC_ENTITY_ID (Integer) - GENETIC ENTITY ID, mandatory
    :param: HUGO_GENE_SYMBOL (String) - HUGO_GENE_SYMBOL, mandatory
    :returns: id of gene if new record added successfully, None otherwise

    """
    with session_scope() as session:
        try:
            rs = Gene()
            rs.ENTREZ_GENE_ID = ENTREZ_GENE_ID
            rs.HUGO_GENE_SYMBOL = HUGO_SYMBOL
            rs.GENETIC_ENTITY_ID = GENETIC_ENTITY_ID
            rs.CYTOBAND = CYTOBAND
            rs.LENGTH = LENGTH
            session.add(rs)
            session.commit()
        except Exception as e:
            raise GeneError("failed add gene record for ENTREZ_GENE_ID {0}" \
                            .format(ENTREZ_GENE_ID), ENTREZ_GENE_ID, HUGO_SYMBOL)

def _update_gene(ENTREZ_GENE_ID, HUGO_SYMBOL, GENETYPE, CYTOBAND, LENGTH):
    """
    add a new record to the gene table from a give gene

    :param: ENTREZ_GENE_ID (Integer) - ENTREZ GENE ID, mandatory
    :param: GENETIC_ENTITY_ID (Integer) - GENETIC ENTITY ID, mandatory
    :param: HUGO_GENE_SYMBOL (String) - HUGO_GENE_SYMBOL, mandatory
    :returns: id of gene if new record added successfully, None otherwise

    """
    with session_scope() as session:
        try:
            rs = get_entrez_gene(ENTREZ_GENE_ID, HUGO_SYMBOL)
            rs.TYPE = GENETYPE
            rs.CYTOBAND = CYTOBAND
            rs.LENGTH = LENGTH
            session.add(rs)
            session.commit()
        except Exception as e:
            raise GeneError("failed update gene record for ENTREZ_GENE_ID {0}" \
                            .format(ENTREZ_GENE_ID), ENTREZ_GENE_ID, HUGO_SYMBOL)

def _add_gene_alias(ENTREZ_GENE_ID, GENE_ALIAS):
    """
    add a new record to the gene_alias table from a given gene

    :param: ENTREZ_GENE_ID (Integer) - ENTREZ GENE ID, mandatory
    :param: GENE_ALIAS (string) - GENE_ALIAS, mandatory
    :returns: None

    """
    with session_scope() as session:
        try:
            rs = GeneAlias()
            rs.ENTREZ_GENE_ID = int(ENTREZ_GENE_ID)
            rs.GENE_ALIAS = GENE_ALIAS
            session.add(rs)
            session.commit()
        except Exception as e:
            raise GeneAliasError("failed add gene alias record.", ENTREZ_GENE_ID, GENE_ALIAS)

def add_gene(genes):
    """
    load new genes to the gene table from a TSV file
    
    :param: gene_file (String) - path to gene file including file name, mandatory
    :returns: None
    
    """
    with open(genes) as fh:
        data = json.load(fh)
        for dic in data:
            try:
                logger.info(dic)
                if not gene_exist(dic['entrez_gene_id'], dic['hugo_gene_symbol']):
                    GENETIC_ENTITY_ID = _add_genetic_entity()
                    _add_gene(GENETIC_ENTITY_ID, dic['entrez_gene_id'], dic['hugo_gene_symbol'] )
            except GeneError as ge:
                logger.error(ge.message)
                continue


def update_gene(genes):
    """
    load new genes to the gene table from a TSV file

    :param: gene_file (String) - path to gene file including file name, mandatory
    :returns: None

    """
    with open(genes) as fh:
        for line in fh:
            if line.startswith('#'):continue
            try:
                ENTREZ_GENE_ID, HUGO_GENE_SYMBOL, GENETIC_ENTITY_ID, TYPE, CYTOBAND, LENGTH  = line.strip().split('\t')
                logger.info("updating gene {0}".format(line))
                _update_gene(ENTREZ_GENE_ID, HUGO_GENE_SYMBOL, TYPE, CYTOBAND, LENGTH)
            except GeneError as ge:
                logger.error(ge.message)
                continue

def add_gene_alias(gene_alias_file):
    """
    load new genes to the gene table from a TSV file

    :param: gene_file (String) - path to gene file including file name, mandatory
    :returns: None

    """
    with open(gene_alias_file) as fh:
        data = json.load(fh)
        for dic in data:
            try:
                logger.info(dic)
                if not gene_alias_exist(dic['entrez_gene_id'], dic['gene_alias']):
                    logger.info("adding new gene alias for {0}".format(dic['entrez_gene_id']))
                    _add_gene_alias(dic['entrez_gene_id'], dic['gene_alias'])
            except GeneAliasError as ge:
                logger.error(ge.message)
                continue

def _add_type_of_cancer(TYPE_OF_CANCER_ID, NAME, DEDICATED_COLOR, PARENT='tissue'):
    """
    add a new type of cancer to the type_of_cancer table from a cancer type

    :param: TYPE_OF_CANCER_ID (Integer) - ID of TYPE_OF_CANCER, mandatory
    :param: NAME (String) - name of type of cancer, mandatory
    :param: DEDICATED_COLOR (String) - DEDICATED COLOR, mandatory
    :returns: id of cancer type if new record added successfully, None otherwise

    """
    if get_cancer_type(TYPE_OF_CANCER_ID): return
    with session_scope() as session:
        try:
            logger.info("adding a new cancer type: TYPE_OF_CANCER_ID={0}, NAME={1},  DEDICATED_COLOR={2}".\
                        format(TYPE_OF_CANCER_ID, NAME, DEDICATED_COLOR))
            rs = CancerType()
            rs.TYPE_OF_CANCER_ID = TYPE_OF_CANCER_ID
            rs.NAME = NAME
            rs.DEDICATED_COLOR = DEDICATED_COLOR
            rs.CLINICAL_TRIAL_KEYWORDS = ''
            rs.PARENT = PARENT
            rs.SHORT_NAME = ''
            session.add(rs)
            session.flush()
        except Exception as e:
            raise CancerTypeError("failed add cancer type record for TYPE_OF_CANCER_ID {0}" \
                            .format(TYPE_OF_CANCER_ID), TYPE_OF_CANCER_ID)


def add_cancer_types(cancer_types):
    """
    load new cancer type to the type_of_canver table from a json file

    :param: cancer_types (String) - path to cancer type json file including file name, mandatory
    :returns: None

    """
    with open(cancer_types) as json_file:
        data = json.load(json_file)
        for dic in data:
            try:
                logger.info(dic)
                _add_type_of_cancer(dic['id'], dic['name'], dic['color'])
            except CancerTypeError as ce:
                logger.error(ce.message)
                continue


def _add_chrom_size(chrom_id, chrom_name, chrom_size, ref_genome_id):
    """
    add a new record to the gene_alias table from a given gene

    :param: chrom_id (integer) - id of chromosome, mandatory
    :param: chrom_name (string) - name of chromosome, mandatory
    :param: chrom_size(integer) - size of chromosome, mandatory
    :param: ref_genome_id (integer) - id of reference genome, mandatory
    :returns: None

    """
    with session_scope() as session:
        try:
            rs = ChromSize()
            rs.chrom_id = chrom_id
            rs.chrom_name = chrom_name
            rs.size = chrom_size
            rs.reference_genome_id = ref_genome_id
            session.add(rs)
            session.commit()
        except Exception as e:
            raise ChromSizeError("failed add chromosome size record.", ref_genome_id)

def add_chrom_sizes(chrom_size_dict, ref_genome_id):
    try:
        for chrom_name, chrom_size in chrom_size_dict.iteritems():
            if chrom_name == 'X':
                chrom_id = 23
            elif chrom_name == 'Y':
                chrom_id = 24
            else:
                chrom_id = int(chrom_name)
            _add_chrom_size(chrom_id, chrom_name, chrom_size, ref_genome_id)
    except ChromSizeError as e:
        logger.error(e.message)

def get_chrom_sizes(ref_genome_id):
    with session_scope() as session:
        try:
            q = session.query(ChromSize).filter(ChromSize.reference_genome_id == ref_genome_id).order_by(ChromSize.chrom_id)
            chrom_sizes = [ chrom.size for chrom in q.all() ]
            logger.info(chrom_sizes)
            return chrom_sizes
        except Exception as e:
            logger.error(e.message)
            return None