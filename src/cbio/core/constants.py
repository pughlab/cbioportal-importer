#from sqlalchemy.orm import aliased
from cbio.core.base import config


TAB_STYLE = """
<html>
<head>
<style>
table {
    width:100%;
}
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
}
th, td {
    padding: 5px;
    text-align: left;
}
table#t01 tr:nth-child(even) {
    background-color: #C0C0C0;
}
table#t01 tr:nth-child(odd) {
   background-color:#ffffff;
}
table#t01 th {
    background-color: #6698FF;
    color: white;
}
</style>
</head>
"""


LOG_FILE = config.get("importer", "log_file").replace("'", "")
JAR_PATH = config.get('java_file','jar_path')
SPECIES = config.get("reference_genome", "species")
NCBI_BUILD = config.get("reference_genome", "ncbi_build")
UCSC_BUILD = config.get("reference_genome", "ucsc_build")