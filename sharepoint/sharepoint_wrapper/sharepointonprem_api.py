import requests
import os
import urllib3
import sys
import argparse
sys.path.append(os.getcwd())
import clr

from pathlib import Path

clr.AddReference("ADFSAuth16")
clr.AddReference("HtmlAgilityPack")
from ClaimAuth import *

BST_START_TAG =  """<wsse:BinarySecurityToken Id="Compact0" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">"""
BST_END_TAG = '</wsse:BinarySecurityToken>'
urllib3.disable_warnings()

class SharepointOnPremApi:
    """
        Work with sharepoint on-premises programatically ex: https://contentspace.global.anz.com
        Features covered:
            Get title of a sharepoint  page
            List files in a particular folder
            Run harriet
        pre-requisite
            user should have access to sharepoint on-premises
            set user=<LAN id>
            set secret=<password>
            I am using proxy https://gblproxy.lb.service.anz:80
    """

    def __init__(self, url="https://contentspace.global.anz.com"):
        self.sharepoint_url = url
        self._user = os.environ.get('user', None)
        self._secret = os.environ.get('secret', None)

        if None in (self._user, self._secret):
            print("Essential environment variables are not set. Please check user, and secret ")
            raise Exception

        self.set_proxy()
        self.header = self.set_headers()

    def set_proxy(self):
        _proxy = "https://{}:{}@gblproxy.lb.service.anz:80".format(self._user, self._secret)
        os.environ['http_proxy'] = _proxy
        os.environ['https_proxy'] = _proxy

    def set_headers(self):
        print('Setting header to http requests for user ', self._user)
        try:
            # Lets fetch the cookies & update header
            _fed_auth_cookie = self.get_cookies()
            headers = {'Cookie': _fed_auth_cookie}
            # Update header so that we get response in json
            headers.update({'Content-Type': 'application/json; odata=verbose',
                            'Accept': 'application/json; odata=verbose'})
            print("    Success")
        except Exception as e:
            print(str(e))
            raise e

        return headers

    def get_cookies(self):
        print("    Step2: Getting FedAuth cookie")
        cookies = ADFSAuth.Auth(self.sharepoint_url, self._user, self._secret, "GLOBAL")
        print("    Success in getting FedAuth cookie")
        print(cookies.get_Item('FedAuth'))
        return str(cookies.get_Item('FedAuth'))

    def get_title(self, site):
        title_url = self.sharepoint_url + site + '/_api/web/title'
        response = requests.get(title_url, headers=self.header, verify=False)
        title = response.json()["d"]["Title"]
        print("    Title is : ", title)

    def get_files_in_folder(self, site,  folder_name):
        full_folder = "Shared Documents/" + folder_name
        files_url = self.sharepoint_url + site + '/_api/web/GetFolderByServerRelativeUrl(' + "'" + full_folder + "'" + ')/Files'
        response = requests.get(files_url, headers=self.header, verify=False)
        for file in response.json()["d"]["results"]:
            print("    Files in folder {}  : {}".format(full_folder, file["Name"]))

    def download_file_from_folder(self, folder_name, file_name):
        full_folder = "Shared Documents/" + folder_name
        output_file_name = Path("P:\My Documents\DLE\github", file_name)
        file_url = self.sharepoint_url + '/sites/DLE-IA-Forum/_api/web/GetFolderByServerRelativeUrl(' + "'" + full_folder + "'" + ')/Files(' + "'" + file_name + "'" + ')/$value'
        response = requests.get(file_url, headers=self.header, verify=False)
        with open(output_file_name, "wb") as f:
            f.write(response.content)
        print("    File {} downloaded at {}".format(file_name, output_file_name))

def get_arguments() -> argparse.Namespace:
    """ Return command line arguments."""

    parser = argparse.ArgumentParser(
        prog="python sharepoint_harriet_api.py",
        usage="%(prog)s [-h] [--url] [--site] [--folder] [--ia]",
    )

    parser.add_argument(
        "--url","-u",
        dest='url',
        type=str,
        default="https://contentspace.global.anz.com"
    )
    parser.add_argument(
        "--site", "-s",
        dest='site',
        type=str,
        default="/teams/dataplatformprogram/DLET"
    )
    parser.add_argument(
        "--folder", "-f",
        dest='folder',
        type=str,
        help="folder name in sharepoint site"
    )
    parser.add_argument(
        "--ia", "-ia",
        dest='ia',
        type=str,
        help="IA file name"
    )

    return parser.parse_args()

if __name__ == '__main__':
    args = get_arguments()
    sp_onprem_api = SharepointOnPremApi(url=args.url)
    print("Now running few inquiries on sharepoint on-premises")
    sp_onprem_api.get_title(args.site)
    sp_onprem_api.get_files_in_folder(args.site, args.folder)
    #sp_onprem_api.download_file_from_folder(args.folder, args.ia)
