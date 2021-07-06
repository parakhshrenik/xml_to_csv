from dltins_link import DLTINS_Link
from xml_parser import MyParser

if __name__ == "__main__":
    try:
        # BASE_URL = sys.argv[1]
        BASE_URL = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select"

    except Exception as e:
        raise Exception(f"Please provide the URL to the base URL : {e}")

    downloader = DLTINS_Link(BASE_URL)
    base_xml = downloader.download_from_link()
    success, download_link, checksum = downloader.parse_xml(base_xml)
    print(success, download_link, checksum)
    if success:
        parser = MyParser(download_link, checksum)
        parser.zip_downloader()
        root_node = parser.unzip_file()

        parser.set_csv_rows(root_node[1])
        print(len(parser.csv_rows_nodes))
        parser.xml_to_csv()
