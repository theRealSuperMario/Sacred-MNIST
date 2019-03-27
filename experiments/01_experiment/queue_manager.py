#!/usr/bin/python3
from __future__ import division, print_function, unicode_literals
from pymongo import MongoClient
from time import sleep
import argparse
import os
import re

client = MongoClient()
db = client.sacred # sacred database

def get_exname():
    ex_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    return ex_name

regx = re.compile(".*{}".format(get_exname()), re.IGNORECASE)


def start_experiment(config):
    from train_convnet import ex # TODO: REPLACE this with your file name
    ex.run(config_updates=config)


def check_for_work():
    try:
        find_filter = {'status': 'QUEUED', "experiment.base_dir" : regx}
        queued_run = db.runs.find(find_filter)[0]
        # queued_run = db.runs.find({'status': 'QUEUED', "experiment" : {"base_dir"}})[0]
    except IndexError:
        return None
    config = queued_run['config']
    print("Starting an experiment with the following configuration:")
    print(config)
    db.runs.delete_one({'_id': queued_run['_id']})
    start_experiment(config)


def main_loop():
    while True:
        check_for_work()
        sleep(10)


def print_dict(d, indentation=2):
    for key, value in sorted(d.items()):
        if type(value) == dict:
            print(" "*indentation + key + ":")
            print_dict(value, indentation=indentation+2)
        else:
            print(" "*indentation + key + ": " + str(value))


def list_experiments(status='QUEUED'):
    print("These Experiments have the status '" + status + "':")
    find_filter = {'status': status, "experiment.name" : regx}
    for ex in db.runs.find(find_filter):
        print("Experiment No " + str(ex['_id']))
        print_dict(ex['config'], indentation=2)
        print("----------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage queued Sacred experiments.\n" +
                                                 "If called without parameters the queue_manager will fetch " +
                                                 "experiments from the database and run them.")
    parser.add_argument('-l', '--list', action='store_true', help="Show the list of queued experiments.")
    parser.add_argument('-c', '--clear', action='store_true', help="Clear the list of queued experiments.")
    args = parser.parse_args()
    if args.clear:
        list_experiments()
        yes = {'yes', 'y', 'ye'}
        no = {'no', 'n'}

        choice = input("Do you want do delete all these experiments? \n {} \n {} \n \n".format(yes, no)).lower()
        if choice in yes:
            print('DELETING')
            find_filter = {'status': "QUEUED", "experiment.name": regx}
            db.runs.delete_many(find_filter)
        elif choice in no:
            print('NOT DELETING')
        else:
            print("Please respond with 'yes' or 'no'")

    if args.list:
        list_experiments()
    elif not args.clear:
        main_loop()
