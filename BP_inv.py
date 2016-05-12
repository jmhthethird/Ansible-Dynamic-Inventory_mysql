#!./bin/python

import sys
import os
import argparse
import MySQLdb
from ConfigParser import SafeConfigParser
import json

"""argparse items"""
parser = argparse.ArgumentParser(description="BP Ansible Inventory")
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Verbose output, will break usage if called by ansible')
parser.add_argument('--list', action='store_true', help='list all hosts')
parser.add_argument('--host', action='store', help='list hostvars')
args = parser.parse_args()


def connect_to_db():
    parser = SafeConfigParser()
    if os.path.isfile("db.ini"):
        parser.read('db.ini')
        dbhost = parser.get('db', 'host')
        dbuser = parser.get('db', 'user')
        dbname = parser.get('db', 'db')
        dbpass = parser.get('db', 'pass')
        conn = MySQLdb.connect(
            host=dbhost, user=dbuser, db=dbname, passwd=dbpass)
    return conn


def query_db(conn):
    c = conn.cursor()
    if args.list:
        parser = SafeConfigParser()
        parser.read("dbquery.ini")
        dbquery = parser.get('query', 'list')
        c.execute(dbquery)
    if args.host:
        # TODO: restructure this. make it select ...(all things)... from
        # ...(things)... where {dict key: hostname or something} like {dict
        # value: <value sent to --host>}
        parser = SafeConfigParser()
        parser.read("examples/dbquery.ini")
        dbquery = parser.get('query', 'host')
        c.execute(dbquery)
    data = c.fetchall()
    return data


def list_all_machines(conn):
    result = query_db(conn)
    if args.verbose:
        print "Result:", result, "\n"
        print "len(result):", len(result)
    data = {}

    for row in result:
        data[row[1]] = {}
        data[row[2]] = {}
        data[row[5]] = {}
        data[row[6]] = {}
        data[row[7]] = {}
        data[row[1]]['hosts'] = []
        data[row[2]]['hosts'] = []
        data[row[5]]['hosts'] = []
        data[row[6]]['hosts'] = []
        data[row[7]]['hosts'] = []
        if args.verbose:
            print "Row:", row  # row your boat

    dictlist = list(data.keys())

    if args.verbose:
        print "\nDict key list:", dictlist
        lendict = len(dictlist)
        print "len(dictlist):", lendict

    for x in dictlist:
        for row in result:
            if row[1] == x:
                data[row[1]]['hosts'].append(row[0])
            if row[2] == x:
                data[row[2]]['hosts'].append(row[0])
            if row[5] == x:
                data[row[5]]['hosts'].append(row[0])
            if row[6] == x:
                data[row[6]]['hosts'].append(row[0])
            if row[7] == x:
                data[row[7]]['hosts'].append(row[0])
    data['_meta'] = {}
    data['_meta']['hostvars'] = {}
    return data


def main():
    conn = connect_to_db()
    if args.list == True:
        bp_dict = list_all_machines(conn)
        print json.dumps(bp_dict,indent=4, sort_keys=True)
    if args.host:
        sys.exit("--host disabled. Please use --list. This feature will be enabled at a future date.")

if __name__ == '__main__':
    main()
