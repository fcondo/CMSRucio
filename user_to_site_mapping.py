from rucio.client import Client

import json
import urllib2

CRIC_URL = 'https://cms-cric.cern.ch/api/accounts/user/query/list/?json'
cric_global_user_data = json.load(urllib2.urlopen(CRIC_URL))
cric_US_user = {}

client = Client()
rses_tmp = client.list_rses('country=US')
rses = []

for r in rses_tmp:
	rses.append(r['rse'])

DEFAULT_RSE_SIZE = 1  # Tb

CALIFORNIA = ['California Institute of Technology', 'Lawrence Livermore Nat. Laboratory',
              'University of California Davis', 'University of California  Los Angeles']

FLORIDA = ['Florida International University', 'Florida State University',
           'Florida Institute of Technology', 'University of Florida', 'University of Puerto Rico']

MIT = ['Boston University', 'Brown University', 'Fairfield University', 'Massachusetts Inst. of Technology', 'Northeastern University']

NEBRASKA = ['University of Colorado Boulder', 'University of Iowa', 'Kansas State University',
            'The University of Kansas', 'University of Nebraska Lincoln']

PURDUE = ['Carnegie-Mellon University', 'Ohio State University', 'Purdue University', 'The State University of New York SUNY']

UCSD = ['University of California Riverside', 'Univ. of California Santa Barbara', 'Univ. of California San Diego']

WISCONSIN = ['University of Minnesota', 'University of Rochester', 'Wayne State University', 'University of Wisconsin Madison']

FNAL = ['Fermi National Accelerator Lab.']

VANDERBILT = ['Vanderbilt University']

def get_US_rse_site(institute, institute_country):

    if not institute:       # institute = "", the user no longer belong to CMS
        return

    if "US" not in institute_country:
        return

    if institute in CALIFORNIA:
        return 'T2_US_Caltech_Test'
    elif institute in FLORIDA:
        return 'T2_US_Florida_Test'
    elif institute in MIT:
        return 'T2_US_MIT_Test'
    elif institute in NEBRASKA:
        return 'T2_US_Nebraska_Test'
    elif institute in PURDUE:
        return 'T2_US_Purdue_Test'
    elif institute in UCSD:
        return 'T2_US_UCSD_Test'
    # elif institute in VANDERBILT:
    #     return 'T2_US_Vanderbilt_Test'
    elif institute in WISCONSIN:
        return 'T2_US_Wisconsin_Test'
    else:
        return 'T1_US_FNAL_Disk_Test'  # FNALLPC ?

def get_US_accounts():

    # i = 0

    for key, user in cric_global_user_data.items():
        name = key.encode("utf-8")
        dn = user['dn'].encode("utf-8")
        institute = user['institute'].encode("utf-8")
        institute_country = user['institute_country'].encode("utf-8")
        email = user['institute'].encode("utf-8")
        # hypernews = ' '.encode("utf-8")

        # if i > 10:  # testing
          #   break

        if "US" in institute_country:
            if name not in cric_US_user:
                rse_key = get_US_rse_site(institute, institute_country)
                tmp = create_dict_entry(name, dn, email, institute, institute_country)

            cric_US_user.update(tmp)

            # print("User: {} DN: {} Institute: {} Country: {} HN: {}").format(name, dn, institute, institute_country, hypernews)
            # i = i + 1

    # for key, val in cric_US_user.items():
    #     print(key, val)
    #
    #     print(len(cric_US_user))
    #     print(i)

def create_dict_entry(name, dn, email, institute, institute_country):
    rse_key = get_US_rse_site(institute, institute_country)
    entry = {
        name: {
            "dn": dn,
            "institute": institute,
            "institute_country": institute_country,
            "email": email,
            # "hypernews": hypernews,
            "RSES": {
                rse_key: DEFAULT_RSE_SIZE,
                'rse_default': 0
            }
        }
    }
    return entry

'''def list_t2_rses():
    """Note that your institute may also have a Tier3 with associated storage space,
       contact your institute leader for more information. """

    for rse in rses_tmp:
        if ("T2" in rse['rse'] and "US" in rse['rse']) or "FNAL" in rse['rse']:
            rses.append(rse['rse'])

    # for r in rses:
    #     print(r)
    # print(len(rses))
'''

def print_mapping(limit=10):
    i = 0
    for user_key, val in cric_US_user.items():
        user_institute = val['institute']
        print('User {} from {} has:').format(user_key, user_institute)
        # print(val['RSES'])

        for rse_name, rse_size in val['RSES'].items():
            print('\t-{} : {} TB').format(rse_name, rse_size)

        # print('User {} from {} has {} TB at RSE: {}').format(user_key, user_institute, user_quota, user_rse)
        i = i + 1
        if i >= limit:
            break

def get_user_rses(name):
    user_val = cric_US_user[name]
    for rse_name, rse_size in user_val['RSES'].items():
        print('User {} has now {} TB at {}').format(name, rse_size, rse_name)

def set_user_rse(name, rse, quota):
    user_val = cric_US_user[name]
    user_rse = user_val['RSES']
    user_rse[rse] = quota

get_US_accounts()
print_mapping()
print('____________________________________')
get_user_rses('aditya.verma@cern.ch')
set_user_rse('aditya.verma@cern.ch', 'rse_default', 5)
get_user_rses('aditya.verma@cern.ch')

