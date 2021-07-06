import pytest
from dltins_link import DLTINS_Link
from xml_parser import MyParser


def test_download_from_link():
    base_url = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select"
    obj = DLTINS_Link(base_url)
    print(obj.download_from_link())
    assert obj.download_from_link() == open('test_data/select.xml').read()


def test_download_from_link_exception():
    base_url = "https://incorrectwebsite.xyz.abcd.com"
    obj = DLTINS_Link(base_url)
    with pytest.raises(Exception):
        obj.download_from_link()


def test_parse_xml():
    base_url = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select"
    obj = DLTINS_Link(base_url)
    ret_val1, ret_val2, ret_val3 = obj.parse_xml(open("test_data/select.xml").read())
    assert ret_val1 == True
    assert ret_val2 == "http://firds.esma.europa.eu/firds/DLTINS_20210117_01of01.zip"
    assert ret_val3 == "852b2dde71cf114289ad95ada2a4e406"

def test_parse_corrupt_xml():
    base_url = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select"
    obj = DLTINS_Link(base_url)
    ret_val1, ret_val2, ret_val3 = obj.parse_xml(open("test_data/corrupt_select.xml").read())
    print (obj.download_link)
    print (obj.checksum)
    assert ret_val1 == False
    # assert ret_val2 == "http://firds.esma.europa.eu/firds/DLTINS_20210117_01of01.zip"
    # assert ret_val3 == "852b2dde71cf114289ad95ada2a4e406"


def test_zipped_content():
    url = "http://firds.esma.europa.eu/firds/DLTINS_20210117_01of01.zip"
    checksum = "852b2dde71cf114289ad95ada2a4e406"
    obj = MyParser(url, checksum)
    obj.zip_downloader()


def test_zipped_content_exception():
    url = "http://firds.esma.europa.eu/firds/DLTINS_20210117_01of01.zip"
    incorrect_checksum = "852b2dde71cf114289ad95ada2a43333"
    obj = MyParser(url, incorrect_checksum)
    with pytest.raises(Exception):
        obj.zip_downloader()


