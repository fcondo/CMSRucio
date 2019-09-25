#! /usr/bin/env python


class Quota:

    def __init__(self, site_name, quota):
        self._site_name = site_name
        self._quota = quota

    def get_site_name(self):
        return self._site_name

    def get_quota(self):
        return self._quota

    def set_site_name(self, site_name):
        self._site_name = site_name

    def set_quota(self, new_quota):
        self._quota = new_quota


