import unittest

from sharepoint.sharepoint_wrapper.sharepoint_api import SharepointApi


class TestSharepointAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.sharepoint_api = SharepointApi('GLOBAL')

    def test_get_list_of_libraries(self):
        self.sharepoint_api.get_library()
