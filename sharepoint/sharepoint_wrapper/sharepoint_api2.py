import json
import os

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.client_request import ClientRequest
from office365.runtime.utilities.request_options import RequestOptions


class SharepointApi:
    """
    Attempt using user credentials auth
    """

    def __init__(self, url="https://contentspace.global.anz.com"):
        # https://contentspace.global.anz.com/teams/dataplatformprogram/DLET/_layouts/15/appregnew.aspx
        # https://contentspace.global.anz.com/teams/dataplatformprogram/DLET/
        self.base_url = url
        self.ctx_auth = AuthenticationContext(url)
        user=os.environ.get('user', None)
        secret=os.environ.get('secret', None)
        self.token_flag = self.ctx_auth.acquire_token_for_user(user,secret)
        print(user)
        print('ctx_auth = ', self.ctx_auth)

    def get_title(self):
        if self.token_flag:
            request = ClientRequest(self.ctx_auth)
            title_url = RequestOptions("{0}/_api/web/".format(self.base_url))
            title_url.set_header('Accept', 'application/json')
            title_url.set_header('Content-Type', 'application/json')
            data = request.execute_request_direct(title_url)
            result_dict = json.loads(data.content)
            web_title = result_dict['Title']
            print("Web title: ", web_title)
        else:
            print("Not proceeding further as failed to get token")


if __name__ == '__main__':
    app = SharepointApi("https://contentspace.global.anz.com")
    app.get_title()
