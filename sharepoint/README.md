# Basics: 
    1) Using add-in policy by accessing via postman
        https://docs.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azureacs
    
    2) Uisng NTLM authorisation (not sure if setup in ANZ)
    
    3) Using Office365-REST-Python-Client
    https://pypi.org/project/Office365-REST-Python-Client/
    Office365-REST-Python-Client supports following auth flows
        1) app principals auth (refer Granting access using SharePoint App-Only for a details): 
                AuthenticationContext.ctx_auth.acquire_token_for_app(client_id, client_secret)
                Prequisite: needs add-in policy app registered
        2) user credentials auth: 
                AuthenticationContext.ctx_auth.acquire_token_for_user(username, password)

# Setup
    export user='----'
    export secret='----'

    export client_id="81cebe26-df96-4185-a6b6-a7307492d087"
    export client_secret="joLi19zxx8x317jekWlf9CydqcYIL0wShlTNAHzgpJ0="

# run tests
    cd sharepoint
    pytest tests/test_sharepoint_api.py -s

    pwd --> /Users/sheelava/Documents/main/github/api-station/sharepoint
    python sharepoint_wrapper/sharepoint_api2.py
    python sharepoint_wrapper/sharepoint_api3.py

# run for sharepoint online:
    cd /Users/sheelava/Documents/main/github/api-station/sharepoint
    export user='----'
    export secret='----'
    python sharepoint_wrapper/sharepointonline_api1.py
    
    export user, email, secret
    python sharepoint_wrapper/sharepointonline_api.py