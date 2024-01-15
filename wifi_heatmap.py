import pymongo

Mongo_client = pymongo.MongoClient(host='127.0.0.1')
coll = Mongo_client['magic_wifi_box']['data']
latest_doc = coll.find_one(sort=[('$natural', pymongo.DESCENDING)])
list_temp = []
data_temp = {'x': latest_doc['local_info']['x'], 'y': latest_doc['local_info']['y'],
             'rssi': latest_doc['radiotap']['dbm_antsignal']}
list_temp.append(data_temp)
msg = str({"data": list_temp})

print(msg)