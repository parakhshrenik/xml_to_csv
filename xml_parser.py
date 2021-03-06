from io import BytesIO
import zipfile
import xml.etree.ElementTree as ET
import hashlib
import pandas as pd
import requests
from upload_to_s3 import upload_to_s3
import os
import logger

def _check_output_dir_exists():
    if not os.path.exists('output'):
        os.makedirs('output')

class MyParser:
    """
    MyParser class has to intelligence to
        - Download the xml and verify using checksum
        - unzip the downloaded xml
        - parse the xml for csv rows
        - convert the rows to a pandas dataframe
        - dump the dataframe to a csv file completing the xml to csv conversion
    """

    def __init__(self, zip_url, checksum):
        self.logger = logger.get_logger()
        self.logger.info("xml_parser:: MyParser class instantiated")
        """ The constructor expects the download link for the xml and expected MD5 of the zipped content"""
        self.url = zip_url
        self.zip_checksum = checksum
        self.zipped_content = None
        self.xml_content = None
        self.xml_filename = None
        self.csv_rows_nodes = list()
        self.csv_rows = list()

    def zip_downloader(self):
        """Downloads the zipped xml in memory and verifies the download using MD5 checksum"""
        self.logger.info("xml_parser:: About to download xml zip")
        zipped_content = requests.get(self.url).content
        downloaded_zip_hash = (hashlib.md5(zipped_content).hexdigest())
        self.logger.info(f"xml_parser:: xml zip downlaoded successfully, MD5 has is {downloaded_zip_hash}")
        if downloaded_zip_hash == self.zip_checksum:
            self.zipped_content = zipped_content
            self.logger.info("xml_parser:: the checksums matches, xml zip downloaded properly")
        else:
            self.logger.error(f"xml_parser:: The checksums don't match, expected is {self.zip_checksum}, downloaded "
                              f"file checksum is {downloaded_zip_hash}")
            raise Exception("Something went wrong while downloading. The hashes don't match")

    def unzip_file(self):
        """unzips the zipped xml content in memory. Returns the root of the xml tree"""
        zip_handle = zipfile.ZipFile(BytesIO(self.zipped_content))
        self.xml_filename = zip_handle.namelist()[0]
        self.logger.info(f"xml_parser::unzipped xml, filename is {self.xml_filename}")
        self.xml_content = zip_handle.read(self.xml_filename)
        self.root = ET.fromstring(self.xml_content)
        self.logger.info(f"xml_parser:: the root node of the xml is {self.root.tag}")
        return self.root

    def set_csv_rows(self, node):
        """
        A recursive method to iterate through the child nodes of the xml
        If a node is found with TermntRcrd is found, it gets appended to the list of rows
        """
        if len(node) == 0:
            return None
        if node.tag.endswith("TermntdRcrd"):
            self.csv_rows_nodes.append(node)
        else:
            for child_node in node:
                self.set_csv_rows(child_node)

    def iterate_csv_nodes(self):
        """
        Iterates through each row, finds the relevant columns
        Creates a dict for each row and append the dict to csv_rows
        """
        ns = self.csv_rows_nodes[0].tag.split('TermntdRcrd')[0]
        self.logger.info(f"xml_parser:: The namespace for the csv rows is {ns}")
        for attrbt in self.csv_rows_nodes:
            # for attrbt in row:

            new_row = dict()
            new_row['Id'] = attrbt.find(ns + 'FinInstrmGnlAttrbts').find(ns + 'Id').text
            new_row['FullNm'] = attrbt.find(ns + 'FinInstrmGnlAttrbts').find(ns + 'FullNm').text
            new_row['ClssfctnTp'] = attrbt.find(ns + 'FinInstrmGnlAttrbts').find(ns + 'ClssfctnTp').text
            new_row['CmmdtyDerivInd'] = attrbt.find(ns + 'FinInstrmGnlAttrbts').find(ns + 'CmmdtyDerivInd').text
            new_row['NtnlCcy'] = attrbt.find(ns + 'FinInstrmGnlAttrbts').find(ns + 'NtnlCcy').text
            new_row['Issr'] = attrbt.find(ns + 'Issr').text

            self.csv_rows.append(new_row)

    def xml_to_csv(self):
        """
        A dataframe is created from the csv_rows
        A new csv file is created with required headers
        The dataframe is dumped to the csv file
        """
        self.iterate_csv_nodes()
        pandas_cols = ["Id", "FullNm", "ClssfctnTp", "CmmdtyDerivInd", "NtnlCcy", "Issr"]
        csv_cols = ["FinInstrmGnlAttrbts.Id", "FinInstrmGnlAttrbts.FullNm", "FinInstrmGnlAttrbts.ClssfctnTp",
                    "FinInstrmGnlAttrbts.CmmdtyDerivInd", "FinInstrmGnlAttrbts.NtnlCcy", "Issr"]
        df = pd.DataFrame(self.csv_rows, columns=pandas_cols)
        self.logger.info("xml_parser:: rows are not converted to a dataframe")
        _check_output_dir_exists()
        with open('output/output.csv', 'a', newline='') as converted_csv:
            converted_csv.write(",".join(csv_cols))
            df.to_csv(converted_csv, header=False, index=False)
        self.logger.info("xml_parser:: CSV File created successfully")
        upload_to_s3('shrenik4234', 'output/output.csv', 'output/output.csv')
