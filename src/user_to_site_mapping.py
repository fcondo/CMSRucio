from rucio.client import Client

import json
import urllib2

# get all the CRIC user profiles in JSON format
CRIC_URL = 'https://cms-cric.cern.ch/api/accounts/user/query/list/?json'
cric_global_user_data = json.load(urllib2.urlopen(CRIC_URL))
# dictionary with US-based only CRIC users, their RSEs and the corresponding quotas
cric_US_user = {}

client = Client()
# filter the RSES to select the US ones
rses_tmp = client.list_rses('country=US')

# list containing all the US rses
rses = []

for r in rses_tmp:
	rses.append(r['rse'])

DEFAULT_RSE_SIZE = 1  # Tb

# list of US Tier-2's grouped by main institute. Needed for the user-to-site mapping 
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

# return a US Site based on the user's institute and institute country 
def get_US_rse_site(institute, institute_country):

    if not institute:       # institute = "", the user no longer belong to CMS Experiment
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
        return 'T1_US_FNAL_Disk_Test'

def get_US_accounts():

    for key, user in cric_global_user_data.items():
	institute_country = user['institute_country'].encode("utf-8")
        
        if "US" in institute_country:
	    name = key.encode("utf-8")
            dn = user['dn'].encode("utf-8")
            institute = user['institute'].encode("utf-8")
            email = user['institute'].encode("utf-8")
        
	    # check for duplicates
            if name not in cric_US_user:
		# obtain the right RSE for the current user based on its institute
                rse_key = get_US_rse_site(institute, institute_country)
		# utility function
                tmp = create_dict_entry(name, dn, email, institute, institute_country)
	    	
		# update the dictionary
            	cric_US_user.update(tmp)

# return a dictionary entry
def create_dict_entry(name, dn, email, institute, institute_country):
    rse_key = get_US_rse_site(institute, institute_country)
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
    i = 0
    for user_key, val in cric_US_user.items():
        user_institute = val['institute']
        print('User {} from {} has:').format(user_key, user_institute)
        # print(val['RSES'])

        for rse_name, rse_size in val['RSES'].items():
            print('\t-{} : {} TB').format(rse_name, rse_size)
  
        i = i + 1
        if i >= limit:
            break

# debugging function
def get_user_rses(name):
    user_val = cric_US_user[name]
    for rse_name, rse_size in user_val['RSES'].items():
        print('User {} has now {} TB at {}').format(name, rse_size, rse_name)

# set a new quota for a certain RSE for a given user
def set_user_rse(name, rse, quota):
    user_val = cric_US_user[name]
    user_rse = user_val['RSES']
    user_rse[rse] = quota

get_US_accounts()
print_mapping()

# testing
#get_user_rses('test')
#set_user_rse('test', 'rse_default', 5)
#get_user_rses('test')

