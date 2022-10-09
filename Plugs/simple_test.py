import tinytuya


import json

f = open('devices.json')
devices = json.load(f)         # returns JSON object as a dict

i = 1

d = tinytuya.OutletDevice(devices[i].get('id'), devices[i].get('ip'), devices[i].get('key'))
d.set_version(3.3) 
result = d.updatedps([18,19,20]) 
print(result)
print(devices[i].get('name'))
data = d.status() 

print(devices[i].get('name'))
print("I: ", data.get('dps').get('18'))
print("V: ", data.get('dps').get('20') / 10)
print("S: ", data.get('dps').get('1'))

f.close()                   # Closing file
