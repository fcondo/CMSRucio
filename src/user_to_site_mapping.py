from rucio.client import Client
from rucio.common.exception import RSENotFound, RSEOverQuota, AccountNotFound

import sys
import json
import urllib2

# rucio Client
client = Client()

# dictionary with US-based only CRIC users, their RSEs and the corresponding quotas
cric_user = {}

DEFAULT_RSE_SIZE = 1  # Tb

# dictionary of Tier-2's dictionaries grouped by main country, needed for the user-to-site mapping
rses_by_country = {
    "US": {
        'T2_US_Caltech': ['California Institute of Technology', 'Lawrence Livermore Nat. Laboratory',
                          'University of California Davis', 'University of California  Los Angeles'],

        'T2_US_Florida': ['Florida International University', 'Florida State University',
                          'Florida Institute of Technology', 'University of Florida', 'University of Puerto Rico'],

        'T2_US_MIT': ['Boston University', 'Brown University', 'Fairfield University',
                      'Massachusetts Inst. of Technology', 'Northeastern University'],

        'T2_US_Nebraska': ['University of Colorado Boulder', 'University of Iowa', 'Kansas State University',
                           'The University of Kansas', 'University of Nebraska Lincoln'],

        'T2_US_Purdue': ['Carnegie-Mellon University', 'Ohio State University',
                         'Purdue University', 'The State University of New York SUNY'],

        'T2_US_UCSD': ['University of California Riverside', 'Univ. of California Santa Barbara',
                       'Univ. of California San Diego'],

        'T2_US_Wisconsin': ['University of Minnesota', 'University of Rochester', 'Wayne State University',
                            'University of Wisconsin Madison'],

        'T1_US_FNAL_Disk': ['Fermi National Accelerator Lab.'],

        'T2_US_Vanderbilt': ['Vanderbilt University'],
    }
}


# return a site based on the user's institute and institute country
def mapping_by_country(institute, country):
    if not institute:  # institute = "", the user no longer belong to CMS Experiment
        return
    # select rse and institutes in the given country
    institutes_by_country = rses_by_country[country]

    for rse_key, institutes_val in institutes_by_country.items():
        # if the institute belongs to the list, return the RSE = key
        if institute in institutes_val:
            return rse_key + "_Test"


def user_to_site_mapping_by_country(country):
    # get all the CRIC user profiles in JSON format
    cric_url = 'https://cms-cric.cern.ch/api/accounts/user/query/list/?json'
    cric_global_user = json.load(urllib2.urlopen(cric_url))

    for key, user in cric_global_user.items():
        institute_country = user['institute_country'].encode("utf-8")

        if country in institute_country:
            name = key.encode("utf-8")
            dn = user['dn'].encode("utf-8")
            institute = user['institute'].encode("utf-8")
            email = user['institute'].encode("utf-8")

            # check for duplicates
            if name not in cric_user:
                # utility function
                tmp = create_dict_entry(name, dn, email, institute, institute_country)
                if not tmp:
                    continue
                # update the dictionary
                cric_user.update(tmp)


# return a dictionary entry
def create_dict_entry(name, dn, email, institute, institute_country):
    # obtain the right RSE for the current user based on its institute
    rse_key = mapping_by_country(institute, institute_country)

    if not rse_key:  # user no longer in CMS
        return

    entry = {
        name: {
            "dn": dn,
            "institute": institute,
            "institute_country": institute_country,
            "email": email,
            "RSES": {
                rse_key: DEFAULT_RSE_SIZE,
                'rse_default': 0
            }
        }
    }
    return entry


# get user information
def get_user(name):
    try:
        info = cric_user[name]
    except KeyError:
        raise AccountNotFound
    return info


# get the current quota given a user and one of its RSE
def get_user_quota(name, rse=None):
    # check if user is in CRIC
    try:
        user_val = cric_user[name]
    except KeyError:
        # sys.stderr.write("Account not found in CRIC\n")      
        raise AccountNotFound
    
    if user_val is None:
        # sys.stderr.write("Account not found in CRIC\n")
        raise AccountNotFound

    # check if rse is None
    if rse is None:
        # sys.stderr.write("RSE is None\n")
        raise RSENotFound

    # check if user has quota on that RSE
    if rse not in user_val['RSES']:
        # sys.stderr.write("User has no quota on this RSE\n")
        raise RSENotFound

    # check if account exists in Rucio
    try:
        account = client.whoami()['account']
        client.get_account(account)
    except AccountNotFound:
        sys.stderr.write("Account not found in Rucio\n")
        raise

    # chekf it the RSE actually exists
    try:
        client.get_rse(rse)['rse']
    except RSENotFound:
        sys.stderr.write("RSE not found\n")
        raise RSENotFound

    return user_val['RSES'][rse]


# set a new quota for a certain RSE for a given user
def set_user_quota(name, rse, quota):
    # check if user is in CRIC
    try:
        user_val = cric_user[name]
    except KeyError:
        raise AccountNotFound

    if user_val is None:
        # sys.stderr.write("Account not found in CRIC\n")
        raise AccountNotFound

    # check if account exists in Rucio
    try:
        account = client.whoami()['account']
        client.get_account(account)
    except AccountNotFound:
        sys.stderr.write("Account not found in Rucio\n")
        raise
    # check if rse is None
    if rse is None:
        # sys.stderr.write("RSE is None\n")
        raise RSENotFound

    # check if the RSE actually exists
    try:
        client.get_rse(rse)['rse']
    except RSENotFound:
        # sys.stderr.write("RSE does not exists\n")     
        raise

    # check if user has quota on that RSE
    if rse not in user_val['RSES']:
        # sys.stderr.write("User has no quota on this RSE\n")
        raise RSENotFound

    old_quota = get_user_quota(name, rse)

    if old_quota is not None and (quota <= 0 or quota < int(old_quota)):
        template = "Old quota is {0}. Invalid new quota is {1}\n"
        message = template.format(old_quota, quota)
        # sys.stderr.write(message) 
        raise RSEOverQuota

    user_val["RSES"][rse] = quota


user_to_site_mapping_by_country('US')

