# Author: Siqi Cao
# A program to extract key-value paired entities from PDF form.
# Functions:
#    step1: get_valid_data(url) fetches json from a given endpoint.
#    step2: extract_entities(json_input) creates a dictionary with all entities exist in keyValuePairs.
#    step3: scan_left_page(json_input, entities) extract entities on the left side from each page.
import requests
import unittest
from unittest import mock
import main
from random import choice
# create a key class to handle duplicate entity key names
class Key(object):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return "'" + self.name + "'"


# (step 1) fetch the json from a given endpoint
def get_valid_data(url):
    response = requests.get(url)
    # GET request is successful
    if response.status_code == 200:
        return response.json()    # json dict object
    else:
        return "Error " + str(response.status_code) + ": Failed to retrieve data from url"


# (step 2) input JSON, create a dictionary containing all the extracted entities from keyValuePairs
def extract_entities(json_input):
    entities_mp = {}

    # valid json input
    if isinstance(json_input, dict):
        # extract keyValuePairs list from json
        source = json_input["keyValuePairs"]    # a list of dict, each represents a pair of bounding boxes

        # iterate all key-value pairs in keyValuePairs
        for item in source:
            key = Key(item["key"]["content"])
            # if a value doesn't exist for a key, use None for the value
            if "value" not in item.keys():
                value = None
            else:
                value = item["value"]["content"]

            entities_mp[key] = value

    return entities_mp


# (step 3) create a dictionary containing the key-value pairs that exist on the left half of the page
def scan_left_page(json_input):
    res = {}

    # valid json input
    if isinstance(json_input, dict):
        pivot = json_input["ocrResults"]["readResults"][0]["width"] / 2.0    # middle width for page
        # extract keyValuePairs list from json
        source = json_input["keyValuePairs"]

        for item in source:
            # first value in boundingBox represents the x coordinate for upper left corner
            upper_left_corner_x_coordinate = item["key"]["boundingRegions"][0]["boundingBox"][0]
            # 7th value in boundingBox represents the x coordinate for lower left corner
            lower_left_corner_x_coordinate = item["key"]["boundingRegions"][0]["boundingBox"][6]
            if upper_left_corner_x_coordinate < pivot and lower_left_corner_x_coordinate < pivot:
                key = Key(item["key"]["content"])
                # if a value doesn't exist for a key, use None for the value
                if "value" not in item.keys():
                    value = None
                else:
                    value = item["value"]["content"]

                res[key] = value

    return res


def main():
    url = "https://lazarus-assessment-674xeilgrq-uc.a.run.app/"

    # step 1: fetch json from given endpoint
    data = get_valid_data(url)
    #print(data)

    # step 2: extract all entities from keyValuePairs
    all_entities = extract_entities(data)
    #print(all_entities)

    # step 3: extract entities exist on the left half of the page
    left_page_entities = scan_left_page(data)
    #print(left_page_entities)


# Unit tests
class TestMain(unittest.TestCase):
    # run before all tests
    def setUp(self):
        main.url = "https://lazarus-assessment-674xeilgrq-uc.a.run.app/"
        main.data = get_valid_data(main.url)
        main.source = main.data["keyValuePairs"]    # extract keyValuePairs list
        main.pivot = main.data["ocrResults"]["readResults"][0]["width"] / 2.0    # middle width for page


    # test whether all entities are extracted
    @mock.patch('main.input')
    def testExtractAllEntities(self, mock_input):
        data = main.data
        source = main.source

        # extract all entities
        all_entities = extract_entities(data)
        # length of keyValuePairs would be equal to length of all extracted entities
        self.assertEqual(len(source), len(all_entities))


    @mock.patch('main.input')
    def testLeftScan(self, mock_input):
        data = main.data
        source = main.source

        # extract left page entities
        left_page_entities = scan_left_page(data)

        # select a random entity from left side of page
        key = choice(list(left_page_entities))
        key_name = key.name

        # find entity's leftest x coordinate on page
        for item in source:
            if item["key"]["content"] == key_name:
                upper_left_corner_x_coordinate = item["key"]["boundingRegions"][0]["boundingBox"][0]
                # left x coordinate should be less than middle width pivot
                self.assertTrue(upper_left_corner_x_coordinate < main.pivot)
                break


if __name__ == '__main__':
    main()
    unittest.main()
