# EasyMap
A module designed for quickly generating maps from a dataframe

This module is designed for rapid creation of simple HTML maps based off of scraped dataframes

It has the ability to generate coordinates for addresses and then plot them on map

Currently you can use:

run:
    yelp-scrape.py
    
    url_make(item,location)
    get_data(urls)

To perform a Yelp scrape and load information into a dataframe.
The dataframe then uses a backhand way to pull coordinates from googles geojson api
The module uses Folium to quickly create and render an html map with optional extra features

