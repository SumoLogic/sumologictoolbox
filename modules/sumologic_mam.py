import json
import requests
import time

from logzero import logger


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

class SumoLogic_MAM:

    def __init__(self, accessId, accessKey, endpoint="https://auth.sumologic.com/api", cookieFile='cookies_org.txt'):
        #uncomment this to set debug logging, or set it in your main code.
        #logzero.loglevel(level=20)
        self.session = requests.Session()
        self.session.auth = requests.auth.HTTPBasicAuth(accessId, accessKey)
        self.session.headers = {'content-type': 'application/json', 'accept': 'application/json'}
        cj = cookielib.FileCookieJar(cookieFile)
        self.session.cookies = cj
        self.endpoint = endpoint
        if self.endpoint[-1:] == "/":
          raise Exception("Endpoint should not end with a slash character")

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

    def get_deployments(self, partner_name):
        headers = {'partnerName': str(partner_name)}
        r = self.get('/v1/deployments', headers=headers)
        return json.loads(r.text)['deployments']

    # valid status filters are "Active", "Inactive", "All"
    # valid product name filters are 'SUMO-CF-TRIAL', 'SUMO-CF-FREE', 'SUMO-CF-PRO', 'SUMO-CF-ENT'
    def get_orgs(self, partner_name, deployment_id, status_filter="All", product_name_filter=None):
        headers = {'partnerName': str(partner_name)}
        params = {'status': status_filter}
        if product_name_filter:
            params['productName'] = product_name_filter
        r = self.get('/v1/deployments/' + str(deployment_id) + '/orgs', headers=headers, params=params)
        return json.loads(r.text)['organizations']

    def create_org(self, partner_name, deployment_id, org_details_json):
        headers = {'partnerName': str(partner_name)}
        r = self.post('/v1/deployments/' + str(deployment_id) + '/orgs', org_details_json, headers=headers)
        return r

    def create_credits_org(self, partner_name, deployment_id, email, org_name, first_name, last_name, product_name,
                   start_date, credit_units):
        subscription = {'subscriptionType': 'CreditsSubscription',
                        'productName': str(product_name),
                        'startDate': str(start_date),
                        'creditUnits': int(credit_units)
                        }
        body = {'email': str(email),
                'organizationName': str(org_name),
                'firstName': str(first_name),
                'lastName': str(last_name),
                'subscription': subscription
                }
        r = self.create_org(partner_name, deployment_id, body)
        return r

    def create_cloudflex_org(self, partner_name, deployment_id, email, org_name, first_name, last_name, product_name,
                   start_date, frequent_tier, continuous_tier, metrics, total_storage):
        subscription = {'subscriptionType': 'CloudFlexSubscription',
                        'productName': str(product_name),
                        'startDate': str(start_date),
                        'ingestBasic': int(frequent_tier),
                        'ingestEnhanced': int(continuous_tier),
                        'metrics': int(metrics),
                        'totalStorage': int(total_storage)
                        }
        body = {'email': str(email),
                'organizationName': str(org_name),
                'firstName': str(first_name),
                'lastName': str(last_name),
                'subscription': subscription
                }
        r = self.create_org(partner_name, deployment_id, body)
        return r

    def get_org_details(self, partner_name, deployment_id, org_id):
        headers = {'partnerName': str(partner_name)}
        r = self.get('/v1/deployments/' + str(deployment_id) + '/orgs/' + str(org_id), headers=headers)
        return json.loads(r.text)

    def cancel_subscription(self, partner_name, deployment_id, org_id):
        headers = {'partnerName': str(partner_name)}
        r = self.delete('/v1/deployments/' + str(deployment_id) + '/orgs/' + str(org_id) + '/subscription', headers=headers)
        return r

    def update_org(self, partner_name, deployment_id, org_id,  org_details_json):
        headers = {'partnerName': str(partner_name)}
        r = self.put('/v1/deployments/' + str(deployment_id) + '/orgs/' + str(org_id) + '/subscription', org_details_json, headers=headers)
        return r

    def update_credits_org(self, partner_name, deployment_id, org_id, sub_type, product_name, start_date, credit_units):
        body = {'productName': str(product_name),
                'subscriptionType': str(sub_type),
                'startDate': str(start_date),
                'creditUnits': int(credit_units)
                }
        r = self.update_org(partner_name, deployment_id, org_id, body)
        return r

    def update_cloudflex_org(self, partner_name,
                             deployment_id,
                             org_id,
                             sub_type,
                             product_name,
                             start_date,
                             frequent_tier,
                             continuous_tier,
                             metrics,
                             total_storage):

        body = {'productName': str(product_name),
                'subscriptionType': str(sub_type),
                'startDate': str(start_date),
                'ingestBasic': int(frequent_tier),
                'ingestEnhanced': int(continuous_tier),
                'metrics': int(metrics),
                'totalStorage': int(total_storage)
                }
        r = self.update_org(partner_name, deployment_id, org_id, body)
        return r
