import requests
import os
import urllib3
import sys
import argparse
sys.path.append(os.getcwd())
import clr
import harriet.cli

from pathlib import Path
import harriet.setup

clr.AddReference("ADFSAuth16")
clr.AddReference("HtmlAgilityPack")
from ClaimAuth import *

BST_START_TAG =  """<wsse:BinarySecurityToken Id="Compact0" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">"""
BST_END_TAG = '</wsse:BinarySecurityToken>'
urllib3.disable_warnings()
logger = harriet.setup.get_logger()  # pylint: disable=locally-disabled, invalid-

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
    """

    def __init__(self, url="https://contentspace.global.anz.com"):
        self.sharepoint_url = url
        self._user = os.environ.get('user', None)
        self._secret = os.environ.get('secret', None)

        if None in (self._user, self._secret):
            print("Essential environment variables are not set. Please check user, and secret ")
            raise Exception
        self.header = self.set_headers()

    def set_headers(self):
        print('Setting header to http requests for user ', self._user)
        try:
            # Lets fetch the cookies & update header
            _fed_auth_cookie = self.get_cookies()
            headers = {'Cookie': _fed_auth_cookie}
            # Update header so that we get response in json
            headers.update({'Content-Type': 'application/json; odata=verbose',
                            'Accept': 'application/json; odata=verbose'})
        except Exception as e:
            print(str(e))
            raise e

        return headers

    def get_cookies(self):
        print("    Getting FedAuth cookie")
        cookies = ADFSAuth.Auth(self.sharepoint_url, self._user, self._secret, "GLOBAL")
        print("    Success in getting FedAuth cookie")
        return str(cookies.get_Item('FedAuth'))

    def get_title(self, site):
        title_url = self.sharepoint_url + site + '/_api/web/title'
        response = requests.get(title_url, headers=self.header, verify=False)
        title = response.json()["d"]["Title"]
        print("    Title is : ", title)

    def get_files_in_folder(self, site,  folder_name):
        files_url = self.sharepoint_url + site + '/_api/web/GetFolderByServerRelativeUrl(' + "'" + folder_name + "'" + ')/Files'
        response = requests.get(files_url, headers=self.header, verify=False)
        for file in response.json()["d"]["results"]:
            print("    Files in folder {}  : {}".format(folder_name, file["Name"]))

    def get_file_from_folder(self, site, folder_name, file_name):
        output_file_name = Path(os.getcwd(), file_name)
        file_url = self.sharepoint_url + site + '/_api/web/GetFolderByServerRelativeUrl(' + "'" + folder_name + "'" + ')/Files(' + "'" + file_name + "'" + ')/$value'
        response = requests.get(file_url, headers=self.header, verify=False)
        with open(output_file_name, "wb") as f:
            f.write(response.content)
        # print("    File {} downloaded at {}".format(file_name, output_file_name))
        return output_file_name

    @staticmethod
    def call_harriet(input_excel, output='output'):
        print("Calling harriet")
        args = argparse.Namespace()
        args.excel = input_excel
        args.base_path = output
        harriet.cli.main(args)

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
    input = sp_onprem_api.get_file_from_folder(args.site, args.folder, args.ia)
    if Path(input).is_file():
        try:
            sp_onprem_api.call_harriet(input)
        finally:
            os.remove(input)
