# cbioportal-importer
python package to load cancer genomics data sets into the cbioportal database. ; not live
## A Quickstart Quide for Building the cbioportal importer
1. check out cbioportal importer from github
```git clone https://github.com/pughlab/cbioportal-importer.git```
2. change to the root directory of the cbioporter_importer
3. run ```python bootstrap.py``` to generate the bin direcotry
4. run ```bin/buildout``` to install requires packages
5. type ```bin/cbio-impo -s your-dataset-dir -P portal.properties -n -o -g``` to upload your dataset 
to the cbioportal
