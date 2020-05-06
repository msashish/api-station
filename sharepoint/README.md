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

## Sharepoint wrapper for sharepoint O365 (online) 

    Sharepoint O365/Online is the cloud variant and can be reached at https://anz.sharepoint.com
    
    Link to sample IA site https://anz.sharepoint.com/sites/DLE-IA-Forum
    
## Setup below variables 
    
    On Windows   - avoid quotes
        set user=    (give your Global user id. For ex: sheelava)  
        set email=   (give your email id. For ex: ashish.sheelavantar@anz.com)
        set secret=  (give your password)
        
    On Mac/*nix
        export user=  
        export email=
        export secret=

## Run wrapper

    python sharepointonline_api.py

    Copy sharepoint_harriet_api.py to harriet root directory (along side harriet.sh) and then, 
    python sharepoint_harriet_api.py -u "https://anz.sharepoint.com" -s "/sites/DLE-IA-Forum" -f "test" -ia "IA_CAP_to_BIH_Batch_AU.xlsx"

## Pending improvements
    avoid proxy
    Try below libraries & reduce loc
        Office365 --> https://pypi.org/project/Office365-REST-Python-Client/
        O365
