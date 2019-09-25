#! /usr/bin/env python

from policy import Policy
from quota import Quota

from rucio.client import Client
from rucio.common.exception import RSENotFound

import json
import sys


class InstitutePolicy(Policy):

    def __init__(self):
        self._default_quota = (10 ** 6)  # 1 MB for testing
        self._client = Client()
        self._CRIC_USERS_API = 'https://cms-cric.cern.ch/api/accounts/user/query/list/?json'

        with open('config_institute_policy.json') as policy_file:
            self._policy = json.load(policy_file)

    def get_policy(self):
        return self._policy

    def get_rse_list(self):
        pass

    def get_cric_url(self):
        return self._CRIC_USERS_API

    def get_default_quota(self):
        return self._default_quota

    def set_default_quota(self, new_quota=None):
        self._default_quota = new_quota

    def get_rse(self, **kwargs):
        if kwargs is not None:
            try:
                rse = self.get_rse_by_country(kwargs['institute'], kwargs['institute_country'])
            except RSENotFound:
                raise
            option = kwargs['option']
            quota = None

            if rse is None:
                sys.stderr.write('User ' + kwargs['username'] + 'no longer belong to CMS (institute is empty)\n')
                return

            if option == 'reset-all':
                quota = self._default_quota
            elif option == 'delete-all':
                quota = None
            elif option == 'set-new-only':
                quota = self._client.get_account_limit(account=kwargs['username'], rse=rse)[rse]
                if quota is None:
                    message = "[quota SET] User {0} has now {1} bytes at the {2} site\n".format(kwargs['username'],
                                                                                                quota,
                                                                                                rse)
                    # sys.stdout.write(message)
                    quota = self._default_quota

                elif quota != self._default_quota:
                    message = "[quota ALREADY SET] User {0} has already {1} bytes at the {2} site and you can not " \
                              "overwrite default quota of {3} bytes. Use 'reset-all' option.\n".format(
                        kwargs['username'], quota,
                        rse, self._default_quota)
                    sys.stderr.write(message)
                    raise Exception

            rse_quota = Quota(rse, quota)
            return rse_quota
        # print '###'
        return

    def get_rse_by_country(self, institute=None, institute_country=None):
        """
        This function returns a site based on the user's institute and institute country.
        If institute = '' the user no longer belong to CMS Experiment.
        """
        if not institute:
            return

        if institute_country == 'US':
            with open('config_institute_policy.json') as institutes_per_rse:
                rses_by_country = json.load(institutes_per_rse)

            institutes_by_country = rses_by_country[institute_country]

            """Currently using the test RSEs like T2_US_MIT_Test
            for testing purposes. In future it will be not needed
            anymore and will be deleted to use the standard RSES."""

            rucio_rses = [r['rse'] for r in self._client.list_rses()]

            for rse_key, institutes_val in institutes_by_country.items():
                if institute in institutes_val:
                    if rse_key + '_Test' not in rucio_rses:
                        # print '-----> ' + rse_key+'_Test'
                        # print rucio_rses
                        raise RSENotFound
                    else:
                        pass
                        # print '... ' + rse_key+'_Test'
                        # print rucio_rses
                    return rse_key + "_Test"

            return u'T1_US_FNAL_Disk' + "_Test"
        else:  # for other policies
            pass

