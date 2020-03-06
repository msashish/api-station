import os
import requests
import urllib.parse
import pprint


class ControlmAPI:

    def __init__(self, user, url="your/url/here"):
        self.url = url
        self.session = requests.Session()

        self.session.headers.update(
            {"Authorization": f"Bearer {self.login(user)}"}
        )

    def login(self, user):
        login_url = urllib.parse.urljoin(self.url, "session/login")
        response = self.session.post(login_url,
                                     json={"username": user, "password": os.environ.get('controlm_password', None)})

        # If the response was successful, no Exception will be raised
        response.raise_for_status()

        return response.json()["token"]

    def logout(self):
        logout_url = urllib.parse.urljoin(self.url, "session/logout")
        response = self.session.post(logout_url)

        # If the response was successful, no Exception will be raised
        response.raise_for_status()

    def get_jobs_status(self, limit=10):
        jobs_status_url = urllib.parse.urljoin(self.url, "run/jobs/status")
        response = self.session.get(jobs_status_url, params={'limit': limit})
        if response.status_code != 200:
            print(response.status_code)
            print(response.json())

        # If the response was successful, no Exception will be raised
        print(f"Listing {limit} jobs and their statuses: ")
        print('-' * 80)
        response.raise_for_status()
        for job_status in response.json()["statuses"]:
            pprint.pprint(job_status)
            print('-' * 80)

    def get_jobname_status(self, jobname):
        jobs_status_url = urllib.parse.urljoin(self.url, "run/jobs/status")
        response = self.session.get(jobs_status_url, params={'jobname': jobname})
        if response.status_code != 200:
            print(response.status_code)
            print(response.json())
        pprint.pprint(response.json()["statuses"])

    def get_application_jobs_status(self, application, limit=10):
        jobs_status_url = urllib.parse.urljoin(self.url, "run/jobs/status")
        response = self.session.get(jobs_status_url, params={'application': application, 'limit': limit})
        if response.status_code != 200:
            print(response.status_code)
            print(response.json())

        # If the response was successful, no Exception will be raised
        print(f"Listing {limit} jobs and their statuses: ")
        print('-' * 80)
        response.raise_for_status()
        for job_status in response.json()["statuses"]:
            pprint.pprint(job_status)
            print('-' * 80)

    def get_depoy_jobs(self, format, ctm, folder, limit=10):
        deploy_jobs_url = urllib.parse.urljoin(self.url, "deploy/jobs")
        response = self.session.get(deploy_jobs_url, params={'format': format, 'ctm': ctm, 'folder': folder})
        if response.status_code != 200:
            print(response.status_code)
            print(response.json())

        # If the response was successful, no Exception will be raised
        print(response)
        response.raise_for_status()
