import abc
import requests

import astropy.table
import sunpy.net.base_client
from sunpy.net import attr
from . import attrs
from .attr_walker import walker

from heliopy.data import cdasrest


class SPDFQueryResponse(sunpy.net.base_client.BaseQueryResponse):
    def __init__(self, table=None):
        self.table = table or astropy.table.Table()
        self._client = None

    def __len__(self):
        return len(self.table)

    def __getitem__(self, item):
        return type(self)(self.table[item])

    def build_table(self):
        """
        Return an `astropy.table.Table` representation of the query response.
        """
        return self.table

    def _append_result(self, result, nvars, dataset):
        """
        Append a list of results from the API.
        This method translates the API names into ones similar to the query attrs.

        Parameters
        ----------
        results : `list`
            A list of dicts as returned by the dataset search API.
        """
        new_result = [
            [dataset],
            [astropy.time.Time(result['StartTime']).iso],
            [astropy.time.Time(result['EndTime']).iso],
            [result['Length']],
            [nvars]
        ]
        new_table = astropy.table.Table(
            data=new_result,
            names=['Dataset', 'Start time', 'End time', 'Rows', 'Columns'])
        self.table = astropy.table.vstack(new_table, self.table)

    @property
    def client(self):
        """
        An instance of `BaseClient` used to generate the results.
        """
        if self._client is None:
            self.client = SPDFClient()
        return self._client

    @client.setter
    def client(self, value):
        self._client = client

    @property
    def blocks(self):
        return list(self.table.iterrows())

    def response_block_properties(self):
        """
        Returns a set of class attributes on all the response blocks.

        Returns
        -------
        s : `set`
            List of strings, containing attribute names in the response blocks.
        """
        raise NotImplementedError()


class SPDFClient(sunpy.net.base_client.BaseClient):
    def search(self, *args):
        """
        Search for datasets provided by the Space Physics Data Facility.
        """
        query = attr.and_(*args)
        queries = walker.create(query)

        results = SPDFQueryResponse()
        for quer in queries:
            dataset = quer['dataset']
            var_info = cdasrest.get_variables(dataset)
            vars = [v['Name'] for v in var_info['VariableDescription']]
            url = cdasrest.get_cdas_url(quer['startTime'], quer['endTime'], vars, dataset)
            params = {'format': 'cdf', 'cdfVersion': 3}
            response = requests.get(
                url, params=params, headers=cdasrest.CDAS_HEADERS)
            # If there's not a remote file, continue
            if 'FileDescription' not in response.json():
                continue
            results._append_result(response.json()['FileDescription'][0], len(vars), dataset)

        return results

    def fetch():
        pass

    @classmethod
    def _can_handle_query(cls, *query):
        # Import here to prevent circular imports
        from sunpy.net import attrs as a

        required = {attrs.Dataset, a.Time}
        query_attrs = {type(x) for x in query}
        if not required.issubset(query_attrs) and not query_attrs.issubset(required):
            return False
        return True
