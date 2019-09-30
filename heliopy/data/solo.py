"""
Methods for downloading in-situ data from Solar Orbiter.
"""
import requests

from heliopy.data import util

tap_url = 'http://soardev.esac.esa.int/soar-sl-tap-beta/tap'


class _soloDownloader(util.Downloader):
    """
    Parameters
    ----------
    intervals : callable
        Intervals function
    """
    def __init__(self, intervals):
        self.intervals = intervals

    def local_dir(self, interval):
        pass

    def download(self, interval):
        data_url = f'{tap_url}/data'

    def load_local_file(self, interval):
        pass
