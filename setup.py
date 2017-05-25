from setuptools import setup, find_packages

setup(
    name="cbio_importer",
    description="Python package for cbioportal importer",
    version='1.0.0.dev0',
    package_dir = {'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pyyaml',
        'jinja2',
        'sqlalchemy',
        'ssh',
        'PyMySQL',
    ],
    entry_points={
    "console_scripts": [
        'cbio_impo = cbio.importer.meta_import:main',
        'gen_or_can_impo = cbio.importer.gene_or_can_type_importer:main',
        'cna_seq_impo = cbio.wrapper.cna_seq_importer:main',
        'meta_study_impo = cbio.wrapper.meta_study_importer:main',
        'ref_genome_impo = cbio.importer.ref_genome_importer:main',
    ]
    }
)
