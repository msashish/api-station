
Step0: setup environment variables 

    export controlm_password=
    
    controlm needs us to first use either of below to get a token
        requests.post(login_url, json={"username": user, "password": xyz) 
        requests.Session().post(login_url, json={"username": user, "password": xyz) 
        
    token will then be used to update session.headers
    
 

Step1: create an api instance
    
    controlm_api = ControlmAPI("username")
    Method1: Use API Key with parameter named 'api-key'
    Method2: Use Token with session header bearer
  
 Step2: use api wrapper

    controlm_api.get_jobs_status(limit=5)
    controlm_api.get_jobname_status(jobname='job anme')
    controlm_api.get_application_jobs_status(application='application name')
    controlm_api.get_depoy_jobs(format='xml', ctm='DCMAU02', folder='folder name')
    controlm_api.logout()
