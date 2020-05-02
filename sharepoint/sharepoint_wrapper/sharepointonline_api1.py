import requests
import os
import xml.etree.ElementTree as etree


class SharepointOnlineApi:
    """
        Attempt using user auth for sharepoint online ex: https://anz.sharepoint.com/sites/DLE-IA-Forum
    """

    def __init__(self, url="https://anz.sharepoint.com"):
        self.sharepoint_url = url
        user = os.environ.get('user', None)
        secret = os.environ.get('secret', None)
        self.header = self.set_headers(user, secret)
        #print(self.header)

    def set_headers(self, user_name, password):
        try:
            print('user = ', user_name)
            #print('request version', requests.__version__)
            proxy = "https://{}:{}@gblproxy.lb.service.anz:80".format('sheelava', password)
            #os.environ['https_proxy'] = "http://gblproxypac.lb.service.anz:80"
            #os.environ['http_proxy'] = "http://gblproxypac.lb.service.anz:80"
            #proxy = "http://gblproxy.lb.service.anz:80"
            #print(proxy)
            os.environ['http_proxy'] = proxy
            os.environ['https_proxy'] = proxy
            auth_url = "https://login.microsoftonline.com/extSTS.srf"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
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
            #print(sharepoint_online_auth_body)
            response = requests.post(auth_url, data=sharepoint_online_auth_body, headers=headers)
                #print(response.status_code == requests.codes.ok)
            s = str(response.content)
            #print(response.status_code)
            #print(s)
            #if [pos for pos in range(len(s)) if s[pos:].startswith('<wsse:BinarySecurityToken Id="Compact0">')] != []:
                   # break
                #raise Exception
            print("Success in getting security token. But not over yet.....")
            #start = [pos for pos in range(len(s)) if s[pos:].startswith('<wsse:BinarySecurityToken Id="Compact0">')][0]
            start_tag = """<wsse:BinarySecurityToken Id="Compact0" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">"""
            start = [pos for pos in range(len(s)) if s[pos:].startswith(start_tag)][0]
            finish = [pos for pos in range(len(s)) if s[pos:].startswith('</wsse:BinarySecurityToken>')][0]
            #security_token = s[start + 40:finish]
            security_token = s[start + 135:finish]
            #print("security_token = ", str(security_token))

            # update the security token into header
            sec_dict = {'Authorization': 'Bearer' + security_token}
            headers.update(sec_dict)

            # Now, Lets fetch the cookies to make Call to SharePoint Online
            print("Step2: Getting FedAuth and rtFa cookies using security token")
            url = self.sharepoint_url + '/_forms/default.aspx?wa=wsignin1.0'
            response = requests.post(url, data=security_token, headers=headers)
            _Fedauth = 'FedAuth={}'.format(response.cookies['FedAuth'])
            _rtFa = 'rtFa={}'.format(response.cookies['rtFa'])
            #print("FedAuth cookie: ", _Fedauth)
            #print("rtFa cookie: ", _rtFa)
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

    def get_title(self):
        title_url = self.sharepoint_url + '/sites/DLE-IA-Forum/_api/web/title'
        response = requests.get(title_url, headers=self.header)
        #print(response.json())
        title = response.json()["d"]["Title"]
        print("Title is : ", title)

    def get_files_in_folder(self, folder_name):
        full_folder = "Shared Documents/" + folder_name
        files_url = self.sharepoint_url + '/sites/DLE-IA-Forum/_api/web/GetFolderByServerRelativeUrl(' + "'" + full_folder + "'" + ')/Files'
        # Should be https://anz.sharepoint.com/sites/DLE-IA-Forum/_api/web/GetFolderByRelativeUrl('Shared Documents/test')/Files
        #print("files_url = " + files_url)
        response = requests.get(files_url, headers=self.header)
        #print(response.json()["d"]["results"])
        for file in response.json()["d"]["results"]:
            print("Files in folder {}  : {}".format(full_folder, file["Name"]))


if __name__ == '__main__':
    #sp_online_api = SharepointOnlineApi(url="https://anz.sharepoint.com/sites/DLE-IA-Forum")
    sp_online_api = SharepointOnlineApi(url="https://anz.sharepoint.com")
    print("Now running few inquiries on sharepoint")
    sp_online_api.get_title()
    sp_online_api.get_files_in_folder('test')
    #top_level_url = "https://anz.sharepoint.com/sites/DLE-IA-Forum"
