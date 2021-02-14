__author__ = 'Tim MacDonald'
__version__ = '0.2'
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
import requests
import time
from logzero import logger
import logzero

try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib

# API RATE Limit constants
MAX_TRIES = 10
NUMBER_OF_CALLS = 1
# per
PERIOD = 5  # in seconds

def backoff(func):
    def limited(*args, **kwargs):
        delay = PERIOD / NUMBER_OF_CALLS
        tries = 0
        lastException = None
        while tries < MAX_TRIES:
            tries += 1
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429: # rate limited
                    logger.debug("Rate limited, sleeping for {0}s".format(delay))
                    time.sleep(delay)
                    delay *= 2
                    lastException = e
                    continue
                else:
                    raise
        logger.debug("Rate limited function still failed after {0} retries.".format(MAX_TRIES))
        raise lastException

    return limited

class SumoLogic_Orgs:

    def __init__(self,
                 accessId,
                 accessKey,
                 parent_deployment,
                 endpoint="https://organizations.sumologic.com/api",
                 cookieFile='cookies_org.txt',
                 log_level='info',
                 log_file=None):

        self.log_level = log_level
        self.set_log_level(self.log_level)
        if log_file:
            logzero.logfile(str(log_file))
        self.session = requests.Session()
        self.session.auth = requests.auth.HTTPBasicAuth(accessId, accessKey)
        self.session.headers = {'content-type': 'application/json', 'accept': 'application/json'}
        cj = cookielib.FileCookieJar(cookieFile)
        self.session.cookies = cj
        self.endpoint = endpoint
        self.parent_deployment = parent_deployment
        if self.endpoint[-1:] == "/":
          raise Exception("Endpoint should not end with a slash character")

    def set_log_level(self, log_level):
        if log_level == 'info':
            self.log_level = log_level
            logzero.loglevel(level=20)
            return True
        elif log_level == 'debug':
            self.log_level = log_level
            logzero.loglevel(level=10)
            logger.debug("[Sumologic Orgs SDK] Setting logging level to 'debug'")
            return True
        else:
            raise Exception("Bad Logging Level")
            logger.info("[Sumologic Orgs SDK] Attempt to set undefined logging level.")
            return False

    def get_log_level(self):
        return self.log_level

    @backoff
    def delete(self, method, params=None, headers=None, data=None):
        logger.debug("DELETE: " + self.endpoint + method)
        logger.debug("Headers:")
        logger.debug(json.dumps(headers, indent=4))
        logger.debug("Params:")
        logger.debug(json.dumps(params, indent=4))
        logger.debug("Body:")
        logger.debug(json.dumps(data, indent=4))
        r = self.session.delete(self.endpoint + method, params=params, headers=headers, data=data)
        logger.debug("Response:")
        logger.debug(r)
        logger.debug("Response Body:")
        logger.debug(r.text)
        if r.status_code != 200:
            r.reason = r.text
        r.raise_for_status()
        return r

    @backoff
    def get(self, method, params=None, headers=None):
        logger.debug("GET: " + self.endpoint + method)
        logger.debug("Headers:")
        logger.debug(json.dumps(headers, indent=4))
        logger.debug("Params:")
        logger.debug(json.dumps(params, indent=4))
        r = self.session.get(self.endpoint + method, params=params, headers=headers)
        logger.debug("Response:")
        logger.debug(r)
        logger.debug("Response Body:")
        logger.debug(r.text)
        if r.status_code != 200:
            r.reason = r.text
        r.raise_for_status()
        return r

    @backoff
    def post(self, method, data, headers=None, params=None):
        logger.debug("POST: " + self.endpoint + method)
        logger.debug("Headers:")
        logger.debug(json.dumps(headers, indent=4))
        logger.debug("Params:")
        logger.debug(json.dumps(params, indent=4))
        logger.debug("Body:")
        logger.debug(json.dumps(data,indent=4))
        r = self.session.post(self.endpoint + method, data=json.dumps(data), headers=headers, params=params)
        logger.debug("Response:")
        logger.debug(r)
        logger.debug("Response Body:")
        logger.debug(r.text)
        if r.status_code != 200:
            r.reason = r.text
        r.raise_for_status()
        return r

    @backoff
    def put(self, method, data, headers=None, params=None):
        logger.debug("PUT: " + self.endpoint + method)
        logger.debug("Headers:")
        logger.debug(json.dumps(headers, indent=4))
        logger.debug("Params:")
        logger.debug(json.dumps(params, indent=4))
        logger.debug("Body:")
        logger.debug(json.dumps(data, indent=4))
        r = self.session.put(self.endpoint + method, data=json.dumps(data), headers=headers, params=params)
        logger.debug("Response:")
        logger.debug(r)
        logger.debug("Response Body:")
        logger.debug(r.text)
        if r.status_code != 200:
            r.reason = r.text
        r.raise_for_status()
        return r

    def get_deployments(self):
        headers = {'parentDeploymentId': self.parent_deployment}
        r = self.get('/v1/deployments', headers=headers)
        return r.json()

    # valid status filters are "Active", "Inactive", "All"
    def get_orgs(self, limit=1000, token=None, status_filter='Active'):
        headers = {'parentDeploymentId': self.parent_deployment}
        params = {'status': str(status_filter),
                  'limit': int(limit)}
        if token:
            params['token'] = str(token)
        r = self.get('/v1/organizations', params=params, headers=headers)
        return r.json()

    def get_orgs_sync(self, limit=1000, status_filter='Active'):
        results = []
        r = self.get_orgs(limit=limit, status_filter=status_filter)
        results = results + r['data']
        while r['next']:
            r = self.get_orgs(limit=limit, token=r.json['next'], status_filter=status_filter)
            results = results + r['data']
        return results

    def create_org(self, org_details_json):
        headers = {'parentDeploymentId': self.parent_deployment}
        r = self.post('/v1/organizations', org_details_json, headers=headers)
        return r.json()

    def get_org_details(self, org_id):
        headers = {'parentDeploymentId': self.parent_deployment}
        r = self.get('/v1/organizations/' + str(org_id), headers=headers)
        return r.json()

    def deactivate_org(self, org_id):
        headers = {'parentDeploymentId': self.parent_deployment}
        r = self.delete('/v1/organizations/' + str(org_id), headers=headers)
        return r

    def update_org(self, org_id, baselines):
        headers = {'parentDeploymentId': self.parent_deployment}
        r = self.put('/v1/organizations/' + str(org_id), baselines, headers=headers)
        return r.json()

    def get_parent_org_info(self):
        headers = {'parentDeploymentId': self.parent_deployment}
        r = self.get('/v1/organizations/parentOrg', headers=headers)
        return r.json()


