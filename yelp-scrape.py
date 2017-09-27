from bs4 import BeautifulSoup
import pandas as pd
import requests
import folium
import numpy as np
#gmapkey = 'AIzaSyCVa0F3Q5sKoVEo-QitjTeAc3K-vbA9RqA'

#gmaps = googlemaps.Client(key = gmapkey)


def nicify(name):
    ''' Make string names for yelp URLs'''
    o_name = name.strip()
    o_name = '+'.join(name.split())
    o_name = str(o_name)
    return o_name

def url_make(item,location):
    ''' Returns a list of the URLs to pull the top 50 results for a given item in a city'''
    URLS = []
    it = nicify(item)
    loc = '+'.join(location.split())
    list_orders = ['ns=1','start=10','start=20','start=30','start=40']
    base_url = 'https://www.yelp.com/search?find_desc='+it+'&find_loc='+loc+'&'
    for suffix in list_orders:
        URLS.append(base_url+suffix)
    return URLS

def get_data(URLS):
    data = []
    for url in URLS:
        r = requests.get(url)

        soup = BeautifulSoup(r.content,'lxml')
        for item in soup.findAll("li", {"class": "regular-search-result"}):
            try:
                name = item.find("a", {"class": "biz-name"}).contents[0]  #NAME
            except:
                name = 'Unknown'
            try:
                reviews = item.find("span", {"class": "review-count rating-qualifier"}).contents[0]  # #Reviews
            except:
                reviews = ''
            try:
                rating = item.find("img", {"class": "offscreen"})  #RATING
            except:
                rating = -1
            try:
                price = item.find("span", {"class": "business-attribute price-range"}).contents[0]  #PRICE
            except:
                price = ''
            try:
                neighborhood = item.find("span", {"class": "neighborhood-str-list"}).contents[0] #NEIGHBORHOOD, nice feature
            except:
                neighborhood = ''
            try:
                address = item.find("address").contents
                street_address = address[0]
                city_default = address[2]
            except:
                street_address = ''
                city_default = ''

            data.append({"Name": name, "Reviews": reviews, "Rating": str(rating)[10:13], "Price": price,"Neighborhood": neighborhood, "Street address": street_address,"City address":city_default})


    for i in range(0, len(data)):
        data[i]['Name'] = str(data[i]['Name'].get_text())
        data[i]['Neighborhood'] = str(data[i]['Neighborhood'].strip())
        data[i]['Street address'] = str(data[i]['Street address'].strip())
        data[i]['City address'] = str(data[i]['City address'].rstrip())
        data[i]['Reviews'] = int(str(data[i]['Reviews']).split()[0])
        data[i]['Rating'] = float(data[i]['Rating'])
        data[i]['Price'] = len(data[i]['Price'])


    df = pd.DataFrame(data)

    return df






def total_reviews(df):
    '''Get total number of reviews made for results'''
    total_reviews = df['Reviews'].sum()
    return total_reviews

def im_frugal(df):
    '''Drop expensive places (price >2), make sure that you set a new copy of df equal to this'''
    df = df.drop(df['Price'] >= 3)
    return df



def top_neighborhood(df):
    '''Easily see which neighborhood (if provided) has most results'''
    best_neighborhood = df.groupby(['Neighborhood'],sort=True)

    best = 0
    best_n = ''
    for key, item in best_neighborhood:
        nums = len(best_neighborhood.get_group(key))
        if nums >best and str(key) != '':
            best = nums
            best_n = key
    return(best_n)




#dataframe export
def geo_df_loader(df):
    nice_df = pd.DataFrame(columns =['Name','geojson_s_address','geojson_c_address'])
    nice_df['Name'] = df[['Name']].copy()
    nice_df['geojson_s_address'] = df['Street address'].map(str)
    nice_df['geojson_c_address'] = df['City address'].map(str)
    return(nice_df)



def get_geo(row):
    s_address = row['Street address']#.map(str)
    c_address = row['City address']#.map(str)
    street_buffer = s_address.split()
    street = '+'.join(street_buffer)
    city_buffer = c_address.split(',')[0].split()
    city = '+'+'+'.join(city_buffer)
    state_buffer = c_address.split(',')[-1].strip()
    state = '+'+str(state_buffer)
    #print(street, city,state)
    response = requests.get(str('https://maps.googleapis.com/maps/api/geocode/json?address='+street+','+city+','+state))

    resp_json_payload = response.json()
    try:
        #print(resp_json_payload['results'][0]['geometry']['location'])
        coordinate = resp_json_payload['results'][0]['geometry']['location']
        return(coordinate)
    except:
        return(None)









def MapCreator(latitudes,longitudes,df):
    m = folium.Map(location=[latitudes[0],longitudes[0]])
    tooltip = 'Click me!'
    for index,i in enumerate(latitudes):
        popup_text = df.loc[index]['Name']
        popup_str = '<i>'+popup_text+'</i>'
        print(popup_str)
        if i != -1:
            folium.Marker([latitudes[index], longitudes[index]], popup=popup_str).add_to(m)
    m.save('index.html')

if __name__ == "__main__":
    urls = url_make('coffee','Baltimore')
    df = get_data(urls)
    latitudes = []
    longitudes = []
    listcoords = []
    for index, row in df.iterrows():

        # print(row['Street address'])
        # print(row['City address'])
        # print(get_geo(row))
        try:
            temp = get_geo(row)
            latitudes.append(temp['lat'])
            longitudes.append(temp['lng'])
        except:
            latitudes.append(-1)
            longitudes.append(-1)
    MapCreator(latitudes,longitudes,df)