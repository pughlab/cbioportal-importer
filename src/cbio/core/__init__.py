"""
Defines customized Exceptions used by the cbio importer
"""
class FilenameParseError(Exception):
    pass

class DirectoryExists(Exception):

    def __init__(self, message, path):
        self.message = message
        self.path = path

class GeneError(Exception):

    def __init__(self, message, GENETIC_ENTITY_ID, ENTREZ_GENE_ID):
        self.message = message
        self.GENETIC_ENTITY_ID = GENETIC_ENTITY_ID
        self.ENTREZ_GENE_ID = ENTREZ_GENE_ID

class GeneAliasError(Exception):

    def __init__(self, message, ENTREZ_GENE_ID, GENE_ALIAS):
        self.message = message
        self.ENTREZ_GENE_ID = ENTREZ_GENE_ID
        self.GENE_ALIAS = GENE_ALIAS

class CancerTypeError(Exception):

    def __init__(self, message, TYPE_OF_CANCER_ID):
        self.TYPE_OF_CANCER_ID = TYPE_OF_CANCER_ID

class ChromSizeError(Exception):

    def __init__(self, message, ref_genome_id):
        self.message = message
        self.ref_genome_id = ref_genome_id