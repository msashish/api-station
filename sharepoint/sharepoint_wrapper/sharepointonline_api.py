import requests
import os
import json
from sys import argv
import xml.etree.ElementTree as etree


class SharepointOnlineApi:
    """
        Attempt using user auth for sharepoint online ex: https://anz.sharepoint.com/sites/DLE-IA-Forum
    """

    def __init__(self, url="https://anz.sharepoint.com/sites/DLE-IA-Forum"):
        self.sharepoint_url = url
        user = os.environ.get('user', None)
        secret = os.environ.get('secret', None)
        self.header = self.set_headers(user, secret)
        print(self.header)

    def set_headers(self, user_name, password):
        try:
            print('user = ', user_name)
            auth_url = "https://login.microsoftonline.com/extSTS.srf"
            headers = {'content-type': 'application/x-www-form-urlencoded'}
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
            sharepoint_online_auth_body = sharepoint_online_auth_body.format(user_name, password, self.sharepoint_url)

            # Let's make call to auth url to get the security token
            print("Step1: Getting security token using user authorization")
            response = requests.post(auth_url, data=sharepoint_online_auth_body, headers=headers)
            print(response.content)
            print(response.status_code == requests.codes.ok)
            s = str(response.content)
            if [pos for pos in range(len(s)) if s[pos:].startswith('<wsse:BinarySecurityToken Id="Compact0">')] == []:
                raise Exception
            start = [pos for pos in range(len(s)) if s[pos:].startswith('<wsse:BinarySecurityToken Id="Compact0">')][0]
            finish = [pos for pos in range(len(s)) if s[pos:].startswith('</wsse:BinarySecurityToken>')][0]
            security_token = s[start + 40:finish]
            print("security_token = ", str(security_token))

            # update the security token into header
            sec_dict = {'Authorization': 'Bearer' + security_token}
            headers.update(sec_dict)

            # Now, Lets fetch the cookies to make Call to SharePoint Online
            print("Step2: Getting cookies using security token")
            url = self.sharepoint_url + '/_forms/default.aspx?wa=wsignin1.0'
            response = requests.post(url, data=security_token, headers=headers)
            _Fedauth = 'FedAuth={}'.format(response.cookies['FedAuth'])
            _rtFa = 'rtFa={}'.format(response.cookies['rtFa'])
            print("FedAuth cookie: ", _Fedauth)
            print("rtFa cookie: ", _rtFa)
            _FinalDict = {'Cookie': _Fedauth + ';' + _rtFa}
            headers.update(_FinalDict)
            headers.update(_FinalDict)
            #added below inorder to get response in json format
            headers.update({'Content-Type': 'application/json; odata=verbose',
                            'Accept': 'application/json; odata=verbose'})
            print("Header successfully updated with rtFa and FedAuth cookies")

            # Calling the Sharepoint api Context REST Api using cookies obtained to get X-RequestDigest
            # url = self.sharepoint_url + """/_api/Contextinfo"""
            # response = requests.post(url, headers=headers)
            # s = str(response.content)
            #
            # start = [pos for pos in range(len(s)) if s[pos:].startswith('<d:FormDigestValue>')][0]
            # finish = [pos for pos in range(len(s)) if s[pos:].startswith('</d:FormDigestValue>')][0]
            # digest = s[start + 19:finish]
            #
            # _FinalDict = {'X-RequestDigest': digest}
            # headers.update(_FinalDict)
            # _FinalDict = {'content-type': 'application/json'}
            # headers.update(_FinalDict)

        except Exception as e:
            print(str(e))
            raise e

        return headers

    def get_data_from_SPOnline(self, ListName, TopLevelUrl, ServiceUrlWithFilters, path):
        _DataDict = {}
        try:
            # Now, Getting the List Information from SharePoint Online
            url = TopLevelUrl + ServiceUrlWithFilters
            url = url.format(ListName)
            print(url)
            _index = 0
            ChildDict = {}
            response = requests.get(url, headers=self.header)
            sxml = str(response.content)
            sxml = sxml[2:len(sxml) - 1]  # This is to avoid any ' coming in xml
            print(path)
            target = open(path, 'w')
            target.write(sxml)
            tree = etree.parse(path)
            root = tree.getroot()
            for child in root:
                if str(child).find('entry') > 0:
                    for child1 in child:
                        if str(child1).find('content') > 0:
                            ChildDict[str(_index)] = {}
                            for child2 in child1[0]:
                                val = {child2.tag.split('}')[1]: child2.text}
                                ChildDict[str(_index)].update(val)
                            _DataDict.update(ChildDict)
                            _index += 1
        except Exception as e:
            print('getSPData ' + e)
            # raise e
        return _DataDict

    def get_atom_feed_data_from_sponline(self, ListName, TopLevelUrl, ServiceUrlWithFilters):
        _DataDict = {}
        try:
            # Now, Getting the List Information from SharePoint Online
            url = TopLevelUrl + ServiceUrlWithFilters
            url = url.format(ListName)
            print(url)
            _index = 0
            ChildDict = {}
            response = requests.get(url, headers=self.header)
            sxml = str(response.content)
            sxml = sxml[2:len(sxml) - 1]  # This is to avoid any ' coming in xml
            tree = etree.fromstring(sxml)
            for child in tree:
                if (str(child).find('entry') > 0):
                    for child1 in child:
                        if (str(child1).find('content') > 0):
                            for child2 in child1:
                                if (str(child2).find('properties')):
                                    ChildDict[str(_index)] = {}
                                    for child3 in child2:
                                        val = {child3.tag.replace(
                                            '{http://schemas.microsoft.com/ado/2007/08/dataservices}', ''): child3.text}
                                        ChildDict[str(_index)].update(val)
                                    _DataDict.update(ChildDict)
                                    _index += 1
        except Exception as e:
            print('getSPData ' + e)
        return _DataDict

    def get_title(self):
        title_url = self.sharepoint_url + '/_api/web/title'
        response = requests.get(title_url, headers=self.header)
        title = response.content['d']['Title']
        print(response.content)
        print("Title is : ", title)

    def get_files_in_folder(self, folder_name):
        full_folder = 'Shared Documents/' + folder_name
        files_url = self.sharepoint_url + '/_api/web/GetFolderByRelativeUrl(' + "'" + full_folder + "'" + ')/Files'
        # Should be https://anz.sharepoint.com/sites/DLE-IA-Forum/_api/web/GetFolderByRelativeUrl('Shared Documents/test')/Files
        print("files_url = " + files_url)
        response = requests.get(files_url, headers=self.header)
        for file in response.content['d']['results']:
            print("File name is : ", file['name'])


if __name__ == '__main__':
    sp_online_api = SharepointOnlineApi(url="https://anz.sharepoint.com/sites/DLE-IA-Forum")
    sp_online_api.get_title()
    sp_online_api.get_files_in_folder('test')
    #top_level_url = "https://anz.sharepoint.com/sites/DLE-IA-Forum"
    #_DataDict = sp_online_api.get_atom_feed_data_from_sponline(ListName="general", TopLevelUrl=top_level_url,
    #                                                           ServiceUrlWithFilters="/sites/DLE-IA-Forum/_api/web/lists/getByTitle('{}')/Items")
