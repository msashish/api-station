
Step0: Create an account in themoviedb

    https://developers.themoviedb.org/3/getting-started/authentication
    https://www.themoviedb.org/settings/api  (msashish)

Step1: Create API Key. Auth Token also gets created.

    Method1: Use API Key with parameter named 'api-key'
    Method2: Use Token with session header bearer
        In the code here, we have generated Token and set environment variable TMDB_TOKEN
  
Step2: Explore and code for list of end points:

    Setup environment variable TMDB_TOKEN and then start using wraper
    https://www.themoviedb.org/documentation/api

    export TMDB_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyYjMxYTRjOGJmZDgxZTc1M2FmZDMyNTdhMTZiMjNlYSIsInN1YiI6IjVlMzZlODgyMGMyNzEwMDAxNTcxZDc5MyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.qPIUmZqIcHr56qsxHhVmGlf4jznfnKIcwk0Y04ni7Dc"

Step3: How to test ? We use pytest framework here and not unittest

    pwd --> on moviedb
    prox --> to turn on proxy. Else will get socket.gaierror
    delete files in vcr_cassettes if it throws error
    python example.py
    pytest tests/test_tmdbwrapper.py -s (remove -s if u dont want messages printed)
    