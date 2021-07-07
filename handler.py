from dltins_link import DLTINS_Link
from xml_parser import MyParser
import logger

if __name__ == "__main__":
    log = logger.get_logger()
    try:
        # BASE_URL = sys.argv[1]
        BASE_URL = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select"
        log.info(f"handler:: The base url to download the xml is {BASE_URL}")

    except Exception as e:
        log.error(f"No URL to the XML file was provided")
        raise Exception(f"Please provide the URL to the base URL : {e}")

    downloader = DLTINS_Link(BASE_URL)
    base_xml = downloader.download_from_link()
    success, download_link, checksum = downloader.parse_xml(base_xml)
    if success:
        parser = MyParser(download_link, checksum)
        parser.zip_downloader()
        root_node = parser.unzip_file()

        parser.set_csv_rows(root_node[1])
        parser.xml_to_csv()
