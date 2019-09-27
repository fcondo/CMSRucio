#! /usr/bin/env python

import getopt
import sys
import json
import urllib2

from rucio.client import Client
from rucio.common.exception import AccountNotFound

from institute_policy import InstitutePolicy
sys.path.insert(1, './tests')
from policy_test import TestPolicy
from cric_user import CricUser


client = Client()
institute_policy = InstitutePolicy()
test_policy = TestPolicy()
cric_user_list = []

"""
This function loads the JSON file by CRIC API or by local file depending on the dry_run option.
"""

def load_cric_users(policy, dry_run):
    if not dry_run:
        worldwide_cric_users = json.load(urllib2.urlopen(policy.CRIC_USERS_API))
    else:
        sys.stdout.write('\t- dry_run version with the new fake user loaded\n')
        with open('fake_cric_users.json') as json_file:
            worldwide_cric_users = json.load(json_file)
    return worldwide_cric_users

"""
For each CRIC user build a CricUser object with all the info needed to apply the US CMS policy in Rucio.
"""

def map_cric_users(country, option, dry_run):
    worldwide_cric_users = load_cric_users(institute_policy, dry_run)

    for key, user in worldwide_cric_users.items():            
        if option == 'delete-all':
            try:
                username = user['profiles'][0]['login'].encode("utf-8")
            except Exception,KeyError:
                continue
            for rse, val in client.get_account_limits(username).items(): 
                client.delete_account_limit(username, rse)

        institute_country = user['institute_country'].encode("utf-8")
        institute = user['institute'].encode("utf-8")
        dn = user['dn'].encode("utf-8")
        email = user['email'].encode("utf-8")
        account_type = "USER"
        policy = ''
        try:
            username = user['profiles'][0]['login'].encode("utf-8")
            if not institute or not institute_country:
                policy = test_policy
                message = "TestPolicy applied to the user {0} (missing info for the US CMS policy)\n".format(username)
                #sys.stdout.write(message)
                raise Exception
            elif country != "" and country in institute_country:
                if username == 'perichmo':
                    continue
                policy = institute_policy
        except Exception, KeyError:
            continue

        cric_user = CricUser(username, email, dn, account_type, institute, institute_country, policy, option)
        cric_user_list.append(cric_user)
        set_rucio_limits(cric_user)


"""
This function sets the Rucio limits, and if needed it also create a Rucio account.
"""
def set_rucio_limits(cric_user):
    try:
        client.get_account(cric_user.username)
    except AccountNotFound:
        client.add_account(cric_user.username, cric_user.account_type, cric_user.email)
    for rse in cric_user.rses_list:
        client.set_account_limit(cric_user.username, rse.sitename, rse.quota)


def get_cric_user(username):
    for user in cric_user_list:
        if user.username == username:
            return user
    raise KeyError

"""
This function modify the policy of one user.
"""
def change_cric_user_policy(username, policy):
    cric_user = get_cric_user(username)
    cric_user.change_policy(policy)
    set_rucio_limits(cric_user)


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

    map_cric_users('US', option, dry_run)


if __name__ == '__main__':
    main()

