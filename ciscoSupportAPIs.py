#!/usr/bin/env Python
__author__ = "Bradley Rose"
__version__ = "0.1"
"""
This API was built around the Cisco Support API documentation located here: https://developer.cisco.com/site/support-apis/
Please see usage details in the readme provided!
"""

import requests
import json

# Disable requests' warnings for insecure connections
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class API:
    def __init__(self):
        self.token = ""

    def get(self, url):
        """
        Description
        -----------
        HTTP GET operations on a provided URL.

        Parameters
        ----------
        url: string
            A provided URL string for a particular resource.

        Returns
        -------
        If HTTP status code == 200:
            data: dictionary
                Dictionary of key:value pairs of all attributes of resource where GET operation was performed.
        else:
            status_code: string
                HTTP status code to identify result.
        """
        request = requests.get(url, headers={'Authorization':'Bearer ' + self.token})

        if request.status_code == 200:
            return request.json()
        else:
            return request.status_code

    def authenticate(self, APIkey, APIsecret):
        """
        Description
        -----------
        Authenticate to Cisco Support API: EoX. Obtain/Create API Key & Secret from https://apiconsole.cisco.com.

        Parameters
        ----------
        Key: string
            API Key (User) for EoX API.
        Secret: string
            API Secret (Password) for EoX API.

        Returns
        -------
        access_token: string
            Bearer token to be used for further EoX API requests.
        token_type: string
            String is equal to "Bearer" to identify token type.
        expires_in: int
            Time (in seconds) that this access token will be valid for. This is set to one hour from the moment of authentication.
        """

        request = requests.post("https://cloudsso.cisco.com/as/token.oauth2", headers={'Content-Type':'application/x-www-form-urlencoded'}, data={'grant_type': 'client_credentials', 'client_id': APIkey, 'client_secret': APIsecret})

        if request.status_code == 200:
            self.token = request.json()['access_token']
            return request.json()
        else:
            return request.status_code

    def getEoxByModel(self, models):
        """
        Description
        -----------
        Obtain EoX data by list of models.

        Parameters
        ----------
        types: list
            List of device models to pass to EoX API for review.

        Returns
        -------
        PaginationResponseRecord: dict
            Keys: {
                PageIndex: int, 
                LastIndex: int, 
                TotalRecords: int, 
                PageRecords: int
            }
        EOXRecord: list
            List of dictionaries for each serial number submitted. Each list object contains a dictionary element with the following:
            Keys: {
                EOLProductID: string,
                ProductIDDescription: string, 
                ProductBulletinNumber: string,
                LinkToProductBulletinURL: string,
                EOXExternalAnnouncementDate: dict {
                    value: string,
                    dateFormat: string
                },
                EndOfSaleDate: dict {
                    value: string,
                    dateFormat: string
                },
                EndOfSWMaintenanceReleases: dict {
                    value: string,
                    dateFormat: string
                },
                EndOfSecurityVulSupportDate: dict {
                    value: string,
                    dateFormat: string
                },
                EndOfRoutineFailureAnalysisDate: dict {
                    value: string,
                    dateFormat: string
                },
                EndOfServiceContractRenewal: dict {
                    value: string,
                    dateFormat: string
                },
                LastDateOfSupport: dict{
                    value: string,
                    dateFormat: string
                },
                EndOfSvcAttachDate: dict {
                    value: string,
                    dateFormat: string
                },
                UpdatedTimeStamp: dict{
                    value: string,
                    dateFormat: string
                },
                EOXMigrationDetails: dict {
                    PIDActiveFlag: string,
                    MigrationInformation: string,
                    MigrationOption: string,
                    MigrationProductId: string,
                    MigrationProductName: string,
                    MigrationStrategy: string,
                    MigrationProductInfoURL: string
                },
                EOXInputType: string,
                EOXInputValue: string
            }
        """
        apiUrl = "https://api.cisco.com/supporttools/eox/rest/5/EOXByProductID/1/"
        url = apiUrl + ",".join(models)
        results = self.get(url)
        return results

    def getSN2InfoBySerial(self, serials):
        """
        Description
        -----------
        Obtain SN2INFO data by list of serial numbers.

        Parameters
        ----------
        serials: list
            List of serial numbers of devices to pass to EoX API for review.

        Returns
        -------
        serial_numbers: list
            List of dictionaries for each serial number submitted. Each list object contains a dictionary element with the following:
            Keys {
                sr_no: string,
                is_covered: string,
                coverage_end_date: string
            }
        """
        apiUrl = "https://api.cisco.com/sn2info/v2/coverage/status/serial_numbers/"
        url = apiUrl + ",".join(serials)
        results = self.get(url)
        return results