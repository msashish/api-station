import requests,json,urllib
from requests_ntlm import HttpNtlmAuth

from sharepoint.sharepoint_wrapper import user, secret


class SharepointApi:

    def __init__(self, domain='GLOBAL'):
        # "DOMAIN\username",password
        self.auth = HttpNtlmAuth(domain + "\\" + user, secret)
        self.base_url = "https://contentspace.global.anz.com"
        #self.base_url = "https://contentspace.global.anz.com/teams/dataplatformprogram/DLET"
        self.headers = {'accept': "application/json;odata=verbose", "content-type": "application/json;odata=verbose"}
        self.headers['X-RequestDigest'] = self.getToken()

    def getToken(self):
        contextinfo_api = self.base_url+"/_api/contextinfo"
        response = requests.post(contextinfo_api, auth=self.auth, headers=self.headers)
        response = json.loads(response.text)
        digest_value = response['d']['GetContextWebInformation']['FormDigestValue']
        return digest_value

    def get_library(self, lib_name='Interface Agreements'):
        folder_path = '/DLET/' + lib_name + '/' + lib_name
        lib_url = self.base_url + "_api/web/GetFolderByServerRelativeUrl({})".format(folder_path)
        print(lib_url)
        response = requests.get(lib_url, auth=self.auth, headers=self.headers)
        print(response.text)

