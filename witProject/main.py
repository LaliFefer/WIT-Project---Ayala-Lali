#import click
import os
import json

def init():
    wit_directory='.wit'
    if not os.path.exists(wit_directory):
        os.makedirs(wit_directory)
    current_file=os.listdir('.')

    metadata_path = os.path.join(wit_directory,'metadata.json')
    with open(metadata_path,'w') as metadata_file:
        json.dump(current_file,metadata_file)

    print("open")


def add(path):


def commit(message):


def status():
