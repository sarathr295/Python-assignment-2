import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

UK_LIMS = (57.985,-10.592,50.681,1.685) #UK map boundary

#Reading sensor data and making appropriate changes
def sensor_data():
    sensor_df = pd.read_csv('GrowLocations.csv') #read csv and load as a dataframe
    sensor_loc_df = sensor_df.iloc[:,[0,1,2]] #take only relevant columns
    sensor_loc_df = sensor_loc_df.drop_duplicates(subset = ['Serial']).reset_index(drop=True) #keep only unique rows .i.e. one sensor per coordinates
    sensor_loc_df = sensor_loc_df.rename(columns={'Serial':'SensorID','Latitude':'Longitude','Longitude':'Latitude'}) #relabeling correct column names
    sensor_loc_df['SensorID'] = sensor_loc_df['SensorID'].str.split('.').str[0] #cleaning sensorid names
    sensor_loc_df = sensor_loc_df.drop(sensor_loc_df[(sensor_loc_df.Longitude > 1.6842) | (sensor_loc_df.Longitude < -10.592)].index) #setting longitude boundaries
    sensor_loc_df = sensor_loc_df.drop(sensor_loc_df[(sensor_loc_df.Latitude > 57.985) | (sensor_loc_df.Latitude < 50.681)].index) #setting lattitude boundaries
    return sensor_loc_df

#Convert the geo-coordinates to the pixels of an Image
#Algorithm is referred from: https://gamedev.stackexchange.com/questions/33441/how-to-convert-a-number-from-one-min-max-set-to-another-min-max-set/33445
def scale_to_img(lat_lon,img_dim):
    bounds = (UK_LIMS[2], UK_LIMS[0]) #longitude bounds
    new = (0, img_dim[1]) #considrs the height of image
    y = ((lat_lon[0] - bounds[0]) * (new[1] - new[0]) / (bounds[1] - bounds[0])) + new[0] #calculates the y pixel

    bounds = (UK_LIMS[1], UK_LIMS[3]) #latitude bounds
    new = (0, img_dim[0]) #considers the width of image
    x = ((lat_lon[1] - bounds[0]) * (new[1] - new[0]) / (bounds[1] - bounds[0])) + new[0] #calculates the x pixel

    #y axis needs to be inverted to get true height
    return int(x),img_dim[1]-int(y)

#Create Map andp plot sensor locations
#Algorithm is referred from: https://towardsdatascience.com/simple-gps-data-visualization-using-python-and-open-street-maps-50f992e9b676
def make_map():
    sensor_loc_df = sensor_data()
    sensor_gps_data = tuple(zip(sensor_loc_df['Latitude'].values, sensor_loc_df['Longitude'].values)) #extracting the lats and longs to a tuple
    basemap = Image.open('map7.png', 'r') #opens the image and sets as basemap
    pixel_pts = []
    for coords in sensor_gps_data:
        (p1,p2) = scale_to_img(coords,(basemap.size[0],basemap.size[1])) #finding the x,y pixels for each lat,long
        pixel_pts.append((p1,p2)) #all tuples are stored into a single list

    map_plot = ImageDraw.Draw(basemap) #start drawing on the basemap
    for pts in pixel_pts:
        map_plot.ellipse([pts[0],pts[1],pts[0]+10,pts[1]+10], fill = (66,163,5)) #for every x,y and its boundary of 10px, an ellipse is drawn on top of the base map

    x_ticks = map(lambda x: round(x, 4),np.linspace(UK_LIMS[1], UK_LIMS[3], num=7)) #creating custom x-axis
    y_ticks = map(lambda x: round(x, 4),np.linspace(UK_LIMS[2], UK_LIMS[0], num=8)) #creating custom y-axis
    y_ticks = sorted(y_ticks,reverse = True) #needs to be inverted
    img,axiss = plt.subplots(figsize=(10,10))
    #Creating the plot
    axiss.imshow(basemap)
    axiss.set_xlabel('Longitude')
    axiss.set_ylabel('Latitude')
    axiss.set_xticklabels(x_ticks)
    axiss.set_yticklabels(y_ticks)
    plt.savefig('output_map.png')
    plt.show() #displays the plot

make_map()
