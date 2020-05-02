import requests
import os
import argparse
import harriet.cli

from pathlib import Path
import harriet.setup

logger = harriet.setup.get_logger()  # pylint: disable=locally-disabled, invalid-
BST_START_TAG =  """<wsse:BinarySecurityToken Id="Compact0" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">"""
BST_END_TAG = '</wsse:BinarySecurityToken>'


class SharepointOnlineApi:
    """
        Work with sharepoint online programatically ex: https://anz.sharepoint.com/sites/DLE-IA-Forum
        Features covered:
            Get title of a sharepoint online page
            List files in a particular folder
        pre-requisite
            user should have access to sharepoint online
            set user=<LAN id>
            set secret=<password>
            set email=<email id> (Can be eliminated if we get a service account)
            I am using proxy https://gblproxy.lb.service.anz:80
    """

    def __init__(self, url="https://anz.sharepoint.com"):
        self.sharepoint_url = url
        _user = os.environ.get('user', None)
        _secret = os.environ.get('secret', None)
        _email = os.environ.get('email', None)

        if None in (_email, _user, _secret):
            print("Essential environment variables are not set. Please check user, secret, and email")
            raise Exception

        self.set_proxy(_user, _secret)
        self.header = self.set_headers(_email, _secret)

    @staticmethod
    def set_proxy(user_name, password):
        _proxy = "https://{}:{}@gblproxy.lb.service.anz:80".format(user_name, password)
        os.environ['http_proxy'] = _proxy
        os.environ['https_proxy'] = _proxy

    def set_headers(self, email, password):
        print('Setting header to http requests for user ', email)
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            # update the security token into header
            _security_token = self.get_security_token(headers, email, password)
            headers.update({'Authorization': 'Bearer' + _security_token})

            # Now, Lets fetch the cookies & update header
            _cookies_dict = self.get_cookies(headers, _security_token)
            headers.update(_cookies_dict)

            # Update header so that we get response in json
            headers.update({'Content-Type': 'application/json; odata=verbose',
                            'Accept': 'application/json; odata=verbose'})

            print("    Success")
        except Exception as e:
            print(str(e))
            raise e

        return headers

    def get_security_token(self, headers, email, password):
        print("    Step1: Getting security token using user authorization")
        auth_url = "https://login.microsoftonline.com/extSTS.srf"
        sharepoint_online_auth_body = """<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
                                xmlns:a="http://www.w3.org/2005/08/addressing"
                                xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
                            <s:Header>
                                <a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/02/trust/RST/Issue</a:Action>
                                <a:ReplyTo>
                                <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
                                </a:ReplyTo>
                                <a:To s:mustUnderstand="1">https://login.microsoftonline.com/extSTS.srf</a:To>
                                <o:Security s:mustUnderstand="1"
                                xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                                <o:UsernameToken>
                                    <o:Username>{}</o:Username>
                                    <o:Password>{}</o:Password>
                                </o:UsernameToken>
                                </o:Security>
                            </s:Header>
                            <s:Body>
                                <t:RequestSecurityToken xmlns:t="http://schemas.xmlsoap.org/ws/2005/02/trust">
                                <wsp:AppliesTo xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy">
                                    <a:EndpointReference>
                                    <a:Address>{}</a:Address>
                                    </a:EndpointReference>
                                </wsp:AppliesTo>
                                <t:KeyType>http://schemas.xmlsoap.org/ws/2005/05/identity/NoProofKey</t:KeyType>
                                <t:RequestType>http://schemas.xmlsoap.org/ws/2005/02/trust/Issue</t:RequestType>
                                <t:TokenType>urn:oasis:names:tc:SAML:1.0:assertion</t:TokenType>
                                </t:RequestSecurityToken>
                            </s:Body>
                            </s:Envelope>
                            """
        sharepoint_online_auth_body = sharepoint_online_auth_body.format(email, password, self.sharepoint_url)

        # Let's make call to auth url to get the security token
        response = requests.post(auth_url, data=sharepoint_online_auth_body, headers=headers)
        s = str(response.content)
        # start = [pos for pos in range(len(s)) if s[pos:].startswith('<wsse:BinarySecurityToken Id="Compact0">')][0]
        start = [pos for pos in range(len(s)) if s[pos:].startswith(BST_START_TAG)][0]
        finish = [pos for pos in range(len(s)) if s[pos:].startswith(BST_END_TAG)][0]
        # security_token = s[start + 40:finish]
        print("    Success")
        return s[start + 135:finish]

    def get_cookies(self, headers, security_token):
        print("    Step2: Getting FedAuth and rtFa cookies using security token")
        url = self.sharepoint_url + '/_forms/default.aspx?wa=wsignin1.0'
        response = requests.post(url, data=security_token, headers=headers)
        _Fedauth = 'FedAuth={}'.format(response.cookies['FedAuth'])
        _rtFa = 'rtFa={}'.format(response.cookies['rtFa'])
        return {'Cookie': _Fedauth + ';' + _rtFa}

    def get_title(self):
        title_url = self.sharepoint_url + '/sites/DLE-IA-Forum/_api/web/title'
        response = requests.get(title_url, headers=self.header)
        title = response.json()["d"]["Title"]
        print("    Title is : ", title)

    def get_files_in_folder(self, folder_name):
        full_folder = "Shared Documents/" + folder_name
        files_url = self.sharepoint_url + '/sites/DLE-IA-Forum/_api/web/GetFolderByServerRelativeUrl(' + "'" + full_folder + "'" + ')/Files'
        response = requests.get(files_url, headers=self.header)
        for file in response.json()["d"]["results"]:
            print("    Files in folder {}  : {}".format(full_folder, file["Name"]))

    def download_file_from_folder(self, folder_name, file_name):
        full_folder = "Shared Documents/" + folder_name
        output_file_name = Path("P:\My Documents\DLE\github", file_name)
        file_url = self.sharepoint_url + '/sites/DLE-IA-Forum/_api/web/GetFolderByServerRelativeUrl(' + "'" + full_folder + "'" + ')/Files(' + "'" + file_name + "'" + ')/$value'
        response = requests.get(file_url, headers=self.header)
        with open(output_file_name, "wb") as f:
            f.write(response.content)
        #print("    File {} downloaded at {}".format(file_name, output_file_name))
        return output_file_name

    @staticmethod
    def call_harriet(input_excel, output='output'):
        print("Calling harriet")
        args = argparse.Namespace()
        args.excel = input_excel
        args.base_path = output
        print(args.excel)
        harriet.cli.main(args)


if __name__ == '__main__':
    sp_online_api = SharepointOnlineApi(url="https://anz.sharepoint.com")
    print("Now running few inquiries on sharepoint online")
    input = sp_online_api.download_file_from_folder('test', 'IA_CAP_to_BIH_Batch_AU.xlsx')
    sp_online_api.call_harriet(input)
