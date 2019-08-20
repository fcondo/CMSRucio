from rucio.client import Client

import json
import urllib2

# rucio Client
client = Client()

# dictionary with US-based only CRIC users, their RSEs and the corresponding quotas
cric_user = {}

DEFAULT_RSE_SIZE = 1  # Tb

# dictionary of US Tier-2's lists grouped by main institute (key = RSE).  Needed for the user-to-site mapping
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

        'T1_US_FNAL_Disk': ['Fermi National Accelerator Lab.']

        # , 'T2_US_Vanderbilt': ['Vanderbilt University']
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
            return rse_key


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

    if not rse_key: # user no longer in CMS
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


# debugging function
def print_mapping(limit=10):
    
    for user_key, val in cric_user.items()[:limit]:
        user_institute = val['institute']
        print 'User {} from {} has:'.format(user_key, user_institute)
        
        for rse_name, rse_size in val['RSES'].items():
            print '\t-{} : {} TB'.format(rse_name, rse_size)


# debugging function
def get_user_rses(name):
    user_val = cric_user[name]
    for rse_name, rse_size in user_val['RSES'].items():
        print'User {} has now {} TB at {}'.format(name, rse_size, rse_name)


# set a new quota for a certain RSE for a given user
def set_user_rse(name, rse, quota):
    user_val = cric_user[name]
    user_rse = user_val['RSES']
    user_rse[rse] = quota


user_to_site_mapping_by_country('US')

print_mapping()

# testing
# username = ""
# get_user_rses('username')
# set_user_rse('username', 'rse_default', 5)
# get_user_rses('username')

