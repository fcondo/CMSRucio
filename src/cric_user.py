#! /usr/bin/env python

# from rse_limit import RSE_limit
from rucio.common.exception import RSENotFound

class CricUser:

    def __init__(self, username, email, dn, institute, institute_country, policy, option):
        self._username = username
        self._email = email
        self._dn = dn
        self._institute = institute
        self._institute_country = institute_country
        self._policy = policy
        self._rses_list = []
        try:
            self._rses_list.append(self._policy.get_rse(username=username, institute=self._institute,
                                                        institute_country=self._institute_country, option=option))
        except RSENotFound:
            raise
        except Exception:
            pass

    def get_username(self):
        return self._username

    def get_email(self):
        return self._email

    def get_dn(self):
        return self._dn

    def get_policy(self):
        return self._policy

    def get_institute(self):
        return self._institute

    def get_institute_country(self):
        return self._institute_country

    def get_rses_list(self):
        return self._rses_list

    def get_rse(self, site_name):
        for rse in self._rses_list:
            if rse.get_site_name() == site_name:
                return rse

    def get_rse_quota(self, site_name):
        for rse in self._rses_list:
            if rse.get_site_name() == site_name:
                return rse.get_quota()

    def add_rse(self, rse):
        self._rses_list.append(rse)

    def delete_rse_by_name(self, site_name):
        for rse in self._rses_list:
            if rse.get_site_name() == site_name:
                del rse

    def set_username(self, username):
        self._username = username

    def set_email(self, email):
        self._email = email

    def set_dn(self, dn):
        self._dn = dn

    def set_institute(self, institute):
        self._institute = institute

    def set_institute_country(self, institute_country):
        self._institute_country = institute_country

    def set_rse_quota(self, site_name, new_quota):
        for rse in self._rses_list:
            if rse.get_site_name() == site_name:
                rse.set_limit(new_quota)

