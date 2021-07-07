"""
Download the xml from this link
From the xml, please parse through to the first download link whose file_type is DLTINS and download the zip
Extract the xml from the zip.
Convert the contents of the xml into a CSV with the following header:
"""
import requests
import xml.etree.ElementTree as ET
import logger

class DLTINS_Link:
    """
    This class is to get the link to the DLTINS file and the checksum of the file
    The base URL must be passed while creating an object.
    """
    def __init__(self, url):
        """
        :param url: Constrcutor expects the URL to the base XML file.
        Sets up the parameter which is hard-coded based on the given wiki.
        """
        self.logger = logger.get_logger()
        self.logger.info("dltins_link:: DLTINS_Link class")
        self.base_url = url
        self.params = {'q': '*',
                       "fq": "publication_date:[2021-01-17T00:00:00Z TO 2021-01-19T23:59:59Z]",
                       "wt": "xml",
                       "indent": "true",
                       "rows": 100,
                       "start": 0}
        self.download_link = None
        self.checksum = None

    def download_from_link(self):
        """Downloads the xml content from the given url using the default params set in init"""
        try:
            self.logger.info("dltins_link:: About to download XML from the provided link")
            xml_content = requests.get(self.base_url, params=self.params).text
            self.logger.info("dltins_link:: XML successfully downloaded")
            return xml_content
        except Exception as e:
            self.logger.error(f"dltins_link:: Something went wrong, downloading xml from {self.base_url}")
            raise Exception(f"Invalid link/Link not working. Please try again later: {e}")

    def parse_xml(self, xml_content):
        """
        :param xml_content: - The base xml content which has links to multiple docs

        :returns True if successful alongwith the download link for the zipped xml content and its checksum
                False if the data isn't found in the provided base xml content
        """

        root = ET.fromstring(xml_content)
        for doc in root.iter('doc'):
            for string in doc:
                if string.attrib["name"] == "file_type" and string.text == "DLTINS":
                    self.logger.info("dltins_link:: str child with file_type DLTINS found")
                    break
            for string in doc:
                if string.attrib["name"] == "download_link":
                    self.download_link = string.text
                    self.logger.info(f"dltins_link:: Download link for XML content is {self.download_link}")

                if string.attrib["name"] == "checksum":
                    self.checksum = string.text
                    self.logger.info(f"dltins_link:: XML checksum should be {self.checksum}")
            break
        if not self.download_link or not self.checksum:
            self.logger.error("dltins_link:: Download Link or Checksum not found")
            return False, None, None
        else:
            return True, self.download_link, self.checksum
