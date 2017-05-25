from __future__ import division
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Sequence, UniqueConstraint
from sqlalchemy import Integer, BigInteger, Text, Boolean, DateTime, Enum
from sqlalchemy import text, Unicode
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects import mysql

from .base import config

########################################################################################################################
#
# database connection and session handling
#
########################################################################################################################


def create_session():
    return sessionmaker(
        bind=create_engine(
            URL(drivername='mysql+mysqldb',
                username=config.get('cbioportal_db', 'username'),
                password=config.get('cbioportal_db', 'password'),
                host=config.get('cbioportal_db', 'host'),
                database=config.get('cbioportal_db', 'name'),
                port=3306
                ),
            echo=False),
        autoflush=False,
        autocommit=False
    )()

@contextmanager
def session_scope(commit=True):
    """
    Provide a transactional scope around a series of operations.
    """
    session = create_session()

    try:
        yield session
        if commit:
            session.commit()
        else:
            session.rollback()
    except:
        session.rollback()
        raise
    finally:
        session.close()

########################################################################################################################
#
# ORM Objects
#
########################################################################################################################

Base = declarative_base()


class CancerType(Base):

    __tablename__ = 'type_of_cancer'

    TYPE_OF_CANCER_ID = Column(Unicode(256, collation='utf8_bin'), primary_key=True)
    NAME = Column(Unicode(256, collation='utf8_bin'), nullable=False)
    CLINICAL_TRIAL_KEYWORDS = Column(Unicode(256, collation='utf8_bin'), nullable=True)
    DEDICATED_COLOR = Column(Unicode(256, collation='utf8_bin'), nullable=False)
    SHORT_NAME = Column(Unicode(256, collation='utf8_bin'), nullable=True)
    PARENT = Column(Unicode(256, collation='utf8_bin'), nullable=True)

    def __repr__(self):
        return "<CancerType('{NAME}')>".format(**self.__dict__)


class GeneticEntity(Base):

    __tablename__ = 'genetic_entity'

    ID = Column(Integer, primary_key=True)
    ENTITY_TYPE = Column(Text, nullable=False)

    def __repr__(self):
        return "<GeneticEntity('{ID}')>".format(**self.__dict__)


class Gene(Base):

    __tablename__ = 'gene'

    ENTREZ_GENE_ID = Column(mysql.INTEGER(11), primary_key=True)
    HUGO_GENE_SYMBOL = Column(Unicode(256, collation='utf8_bin'), nullable=False)
    GENETIC_ENTITY_ID = Column(Integer, nullable=False)
    TYPE = Column(Unicode(256, collation='utf8_bin'), nullable=True)
    CYTOBAND = Column(Unicode(256, collation='utf8_bin'), nullable=True)
    LENGTH = Column(Integer, nullable=True)

    def __repr__(self):
        return "<Gene({HUGO_GENE_SYMBOL}, {ENTREZ_GENE_ID})>".format(**self.__dict__)

class GeneAlias(Base):

    __tablename__ = 'gene_alias'

    ENTREZ_GENE_ID = Column(mysql.INTEGER(11), ForeignKey('gene.ENTREZ_GENE_ID'), primary_key=True)
    GENE_ALIAS = Column(Text, primary_key=True)

    def __repr__(self):
        return "<GeneAlias({GENE_ALIAS}, {ENTREZ_GENE_ID})>".format(**self.__dict__)

class ReferenceGenome(Base):

    __tablename__ = 'reference_genome'

    reference_genome_id = Column(mysql.INTEGER(11), primary_key=True)
    species = Column(Unicode(64, collation='utf8_bin'), nullable=True)
    name = Column(Unicode(64, collation='utf8_bin'), nullable=True)
    build_name = Column(Unicode(64, collation='utf8_bin'), nullable=True)
    genome_size = Column(mysql.BIGINT(20), nullable=True)
    URL = Column(Unicode(256, collation='utf8_bin'), nullable=True)
    version = Column(Unicode(64, collation='utf8_bin'), nullable=True)
    release_date = Column(mysql.DATETIME, nullable=True)
    current = Column(mysql.TINYINT(4), nullable=True)

    def __repr__(self):
        return "<ReferenceGenome('{name}')>".format(**self.__dict__)

class ChromSize(Base):

    __tablename__ = 'chrom_size'

    reference_genome_id = Column(mysql.INTEGER(11), primary_key=True)
    chrom_id = Column(mysql.INTEGER(11), primary_key=True)
    chrom_name = Column(mysql.CHAR(2), nullable=True)
    size = Column(mysql.BIGINT(20), nullable=True)

    #reference_genome = relationship(ReferenceGenome, backref=backref('chrom_size', order_by=chrom_id))

    def __repr__(self):
        return "<ChromSize('{chrom_name}')>".format(**self.__dict__)