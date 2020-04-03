from heliopy.data.cdaweb import SPDFClient
import heliopy.data.cdaweb.attrs as a

client = SPDFClient()
query = a.Time('2018-11-01', '2018-11-01 01:00:00') & a.Dataset('PSP_SWP_SPC_L3I')
res = client.search(query)
print(res)
