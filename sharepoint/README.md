# Basics: 
    1) Using add-in policy by accessing via postman
        https://docs.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azureacs
    
    2) Using NTLM authorisation
    
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



# run tests
    cd sharepoint
    pytest tests/test_sharepoint_api.py -s

    pwd to correct directory sharepoint
    python sharepoint_wrapper/sharepoint_api2.py
    python sharepoint_wrapper/sharepoint_api3.py

    
## Setup below variables 
    
    On Windows   - avoid quotes
        set user=    (give your Global user id.)  
        set email=   (give your email id.)
        set secret=  (give your password)
        
    On Mac/*nix
        export user=  
        export email=
        export secret=

## Run wrapper

    python sharepointonline_api.py

## Pending improvements
    avoid proxy
    Try below libraries & reduce loc
        Office365 --> https://pypi.org/project/Office365-REST-Python-Client/
        O365
