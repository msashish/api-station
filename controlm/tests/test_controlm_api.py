import unittest

from controlm.api.controlm_api import ControlmAPI


# set controlm password in environment variable controlm_password
# export controlm_password=xyz
class TestControlmAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.controlm_api = ControlmAPI("your_username")

    def test_get_jobs_status(self):
        self.controlm_api.get_jobs_status(limit=5)

    def test_get_jobname_status(self):
        self.controlm_api.get_jobname_status(jobname='BIHAU_T1_SRC_AMB_VW_PRD_VAL')

    def test_get_application_jobs_status(self):
        self.controlm_api.get_application_jobs_status(application='BIH_SOBIH')

    def test_get_deploy_jobs(self):
        self.controlm_api.get_depoy_jobs(format='xml', ctm='DCMAU02', folder='BIH_FIN10_IN_EOD')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.controlm_api.logout()
