#! /usr/bin/env python

from rucio.client import Client
from rucio.common.exception import AccountNotFound

from institute_policy import InstitutePolicy
from cric_user import CricUser

import getopt
import sys
import json
import urllib2

client = Client()
policy = InstitutePolicy()

cric_user_list = []


def load_cric_users(policy, dry_run):
    if not dry_run:
        worldwide_cric_users = json.load(urllib2.urlopen(policy.get_cric_url()))
    else:
        sys.stdout.write('\t- dry_run version with the new fake user loaded\n')
        with open('fake_cric_users.json') as json_file:
            worldwide_cric_users = json.load(json_file)
    return worldwide_cric_users


def map_cric_users(policy, country, option, dry_run):
    worldwide_cric_users = load_cric_users(policy, dry_run)

    for key, user in worldwide_cric_users.items():
        institute_country = user['institute_country'].encode("utf-8")

        if country in institute_country:
            dn = user['dn'].encode("utf-8")
            institute = user['institute'].encode("utf-8")
            email = user['email'].encode("utf-8")
            username = user['profiles'][0]['login'].encode("utf-8")

            if username == 'perichmo':
                continue

            cric_user = CricUser(username, email, dn, institute, institute_country, policy, option)
            cric_user_list.append(cric_user)
            try:
                client.get_account(username)
            except AccountNotFound:
                client.add_account(username, 'USER', email)
                # sys.stdout.write("\t- Added account " + username + "\n")

            rses_list = cric_user.get_rses_list()
            for rse in rses_list:
                rse_name = rse.get_site_name()
                rse_quota = rse.get_quota()
                if rse_quota is None:
                    client.delete_account_limit(username, rse_name)
                else:
                    client.set_account_limit(username, rse_name, rse_quota)


def usage():
    print "Command:\tuser_to_site_mapping.py [-o] [-d]"
    print "Options:"
    print "\t-h, --help"
    print "\t-o, --option=\tset-new-only|reset-all|delete-all"
    print "\t-d, --dry_run=\tt|f"


def main():
    option = 'set-new-only'
    dry_run = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:o:d:", ["help", "option=", "dry_run="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-o", "--option"):
            option = a
        elif o in ("-d", "--dry_run"):
            dry_run = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            usage()
            sys.exit(2)

    if option not in ['set-new-only', 'delete-all', 'reset-all']:
        usage()
        sys.exit(2)

    map_cric_users(policy, 'US', option, dry_run)


if __name__ == '__main__':
    main()

