import os
import requests
import re
import time
import logging
import json

from requests import Session
from requests.compat import urljoin, urlparse, urlsplit


#logging.basicConfig(level=0)


class Resource(object):

    def __init__(self, uri, api):
        logging.info(f"init.uri: {uri}")
        self.api = api
        self.uri = uri
        split = urlsplit((self.api.base_url + self.uri))
        self.scheme = split[0]
        self.host = split[1]
        self.url = split[2]
        self.id = None
        self.session = Session()
        self.session.headers.update(self.api.get_token())
        self.attrs = {}
        
    def __getattr__(self, name):
        """
        Resource attributes (eg: user.name) have priority
        over inner rerouces (eg: users(id=123).applications)
        """
        #logging.info("getattr.name: %s" % name)
        # Reource attrs like: user.name
        if name in self.attrs:
            return self.attrs.get(name)
        #logging.info("self.url: %s" % self.url)
        # Inner resoruces for stuff like: GET /users/{id}/applications
        key = self.uri + '/' + name
        self.api.resources[key] = Resource(uri=key, api=self.api)
        return self.api.resources[key]

    def __call__(self, id=None):
        #logging.info("call.id: %s" % id)
        #logging.info("call.self.url: %s" % self.url)
        if id == None:
            return self
        self.id = str(id)
        key = self.uri + '/' + self.id
        self.api.resources[key] = Resource(uri=key, api=self.api)
        return self.api.resources[key]

    # GET /resource
    # GET /resource/id?arg1=value1&...
    def get(self, **kwargs):
        if self.id == None:
            url = self.scheme + "://" + self.host + self.url
        else:
            url = self.api.base_url + self.url + '/' + str(self.id)

        return self.session.get(url, params=kwargs)
 
    # POST /resource
    def post(self, body=None, json=None, **kwargs):
        url = self.scheme + "://" + self.host + self.url
        return self.session.post(url, params=kwargs , data=body, json=json)


    # PUT /resource/id
    def put(self, body=None, json=None, **kwargs):
        url = self.scheme + "://" + self.host + self.url
        return self.session.put(url, params=kwargs , data=body, json=json)

    # DELETE /resource/id
    def delete(self, id, **kwargs):
        url = self.scheme + "://" + self.host + self.url + '/' + str(id)
        return self.session.delete(url, params=kwargs)


class API(object):

    def __init__(self, base_url, auth=None):
        self.base_url = base_url + '/' if not base_url.endswith('/') else base_url
        self.api_path = urlparse(base_url).path
        self.resources = {}
        self.auth = auth

    def __getattr__(self, name):
        #logging.info("API.getattr.name: %s" % name)
        
        key = name
        if not key in self.resources:
            #logging.info("Creating resource with uri: %s" % key)
            self.resources[key] = Resource(uri=key, api=self)
        return self.resources[key]

    def get_token(self):
        return {'Authorization':f'Bearer {self.auth}'}
