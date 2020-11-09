#Import libraries
import http.client
import json
import pandas as pd
from difflib import SequenceMatcher

#Initial Setup
"""access API key can be taken by registering account from https://rajaongkir.com/
This API key using Account starter (limited function)"""

api_key = [YOUR API KEY]
conn = http.client.HTTPSConnection("api.rajaongkir.com")

#Functions scraping city information
"""this function request all list of city information from API, which is saved in json and retrived in take_city() function"""
def req_city():
    headers = { 'key': api_key } #your API key
    conn.request("GET", "/starter/city?", headers=headers)

    res = conn.getresponse()
    data = res.read()
    json_object = json.loads(data) #convert to json (dict)
    conn.close() #dont forget close connection for avoid confusion
    return json_object   

"""this function compute similarity between query by user and list of city"""
def similar_city_string(q, list_city):
    return SequenceMatcher(None, q, list_city).ratio()

"""this function return id of parameter/query city, which take data from function req_city(), if there is no data match
then compute similarity query with all city name, then retrive some cityname that have big value similarity"""
def take_city_id(city_search):
    data_city = req_city()['rajaongkir']['results'] #take list of city
    id_city = 0
    similar_city = [] #this variabel will be filled by similar city name
    for city in data_city:
        if city['city_name'].lower()==city_search.lower(): #pass casesensitive
            id_city=city['city_id']
        else:
            score = similar_city_string(city['city_name'].lower(),city_search.lower()) #compute score similarity
            similar_city.append(city['city_name']) if score>=0.65 else None #tolerance score more than 65% similarity
    
    #return id if have exact city, if not,then return some some city name that have 65% name similarity
    return id_city if id_city !=0 else print(city_search+' tidak ditemukan !! \ndid you mean '+', '.join(map(str, similar_city)))

#Functions scraping cost information
"""This function for computation cost passed some parameter that will be filled from user_interface()"""
def req_cost(origin,destination,weight,courier):
    payload = "origin="+str(origin)+"&destination="+str(destination)+"&weight="+str(weight)+"&courier="+str(courier)
    headers = {
        'key': api_key, #your API key
        'content-type': "application/x-www-form-urlencoded"
        }

    conn.request("POST", "/starter/cost", payload, headers) #request data
    res = conn.getresponse()
    data = res.read()
    json_object = json.loads(data) #convert to json (dict)
    conn.close() #dont forget close connection for avoid confusion
    return json_object

"""this function for user interface where user can interact (input/output) information"""
def user_interface():
    while True: #looping until origin city has same exact name with city from API
      try:
        origin = int(take_city_id(input('Kota/Kabupaten asal\t: ')))
        if origin > 0: break #if origin has value integer and more than 0, than ID is retrived
      except Exception as e:
        print("Silahkan ulang kembali !!\n")
    while True: #looping until origin city has same exact name with city from API
      try:
        destination = int(take_city_id(input('Kota/Kabupaten tujuan \t: ')))
        if destination > 0: break #if origin has value integer and more than 0, than ID is retrived
      except Exception as e:
        print("Silahkan ulang kembali !!\n")
    weight = float(input('Berat barang(Kg) \t: '))*1000
    courier = input('Kurir (JNE/POS/TIKI) \t: ').lower()
    
    #call function req_cost for computing shipping costs
    cost = req_cost(origin,destination,weight,courier)
    
    #condition if some format input not falid or data isn't avaliable
    if cost['rajaongkir']['status']['code'] == 400:
        print('\nInformasi gagal ('+cost['rajaongkir']['status']['description']+')')
        
    #condition if all data valid, then retireve summary information into DataFrame 
    elif cost['rajaongkir']['status']['code'] == 200:
        list_data = []
        for result in cost['rajaongkir']['results'][0]['costs']:
            col_origin = cost['rajaongkir']['origin_details']['type']+' '+cost['rajaongkir']['origin_details']['city_name']+'-'+cost['rajaongkir']['origin_details']['province']+' ('+cost['rajaongkir']['origin_details']['postal_code']+')'
            col_destinat = cost['rajaongkir']['destination_details']['type']+' '+cost['rajaongkir']['destination_details']['city_name']+'-'+cost['rajaongkir']['destination_details']['province']+' ('+cost['rajaongkir']['destination_details']['postal_code']+')'
            col_service = cost['rajaongkir']['results'][0]['code']+'-'+result['service']
            col_description = result['description']
            col_cost = 'Rp.'+str(result['cost'][0]['value'])
            col_etd = result['cost'][0]['etd']+' days'
            list_data.append([col_origin,col_destinat,col_service,col_description,col_cost,col_etd])
        pd_cost= pd.DataFrame(list_data, columns=['Asal','Tujuan','Tipe Kurir', 'Deskripsi tipe', 'Biaya', 'Estimasi pengiriman'])
        display(pd_cost)
    
    #condition else/bad connection request
    else: 
        print('\nBad request')

#Call function
user_interface()