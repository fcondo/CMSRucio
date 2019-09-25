#! /usr/bin/env python

from abc import ABCMeta, abstractmethod

class Policy():

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_policy(self):
        pass

    @abstractmethod
    def get_rse(self, **kwargs):
        pass

    @abstractmethod
    def get_rse_list(self, **kwargs):
        pass


