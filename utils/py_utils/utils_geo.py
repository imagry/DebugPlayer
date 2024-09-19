# This files contains functions related to geographic coordinates manipulatios
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from scipy import linalg
from time import sleep
import os
import unittest
from math import isclose
import folium
from mpl_interactions import ioff, panhandler, zoom_factory
# from matplotlib.widgets import Cursor
# from folium.plugins import MarkerCluster
# from IPython.display import IFrame
# from selenium import webdriver
# from gps_to_cartesian import gps_to_cartesian

def wgs842ecef(df_wgs: pd.DataFrame):
    """transform between the geodetic (i.e., (φ, λ, h)e) and rectangular (i.e., (x, y, z)e) ECEF coordinates. 
    φ denotes latitude 
    λ denotes longitude 
    h denotes altitude above the reference ellipsoid. 
    """
    # df is the wgs84 data with size mx3 array and tupples [latitude,longitude,height] with m is the number of data points and each row consist of: [lat, long, height[m]] 
    # lat/long are degrees in decimal(integer) form with signs (+) for N/E and (-) for S/W
    
    a,ecc,f,R_N_funcHandle_lat = get_wgs84_geodetic_model()    
    
    lat = df_wgs[["latitude"]].to_numpy()
    lng = df_wgs[["longitude"]].to_numpy()
    h = df_wgs[["height"]].to_numpy()
    
    cos_lng = np.cos(np.radians(lng))  #cos(longtitude)
    cos_lat = np.cos(np.radians(lat))  #cos(latitude)
    sin_lng = np.sin(np.radians(lng))  #sin(longtitude)
    sin_lat = np.sin(np.radians(lat))  #sin(latitude)
    
    # caculate RN
    ecc2 = ecc**2
    sin_lat_2 = sin_lat**2
    RN_den = np.sqrt(1-ecc2*sin_lat_2)
    RN = a/RN_den
        
    RN_h_times_cos_lat = (RN + h)*cos_lat
    x = RN_h_times_cos_lat*cos_lng
    y = RN_h_times_cos_lat*sin_lng
    z = (RN*(1-ecc2)+h)*sin_lat
    xyz = {'X': np.squeeze(x), 'Y': np.squeeze(y),'Z': np.squeeze(z)}
    
    df_rect = pd.DataFrame(xyz, columns=['X','Y','Z'])
        
    return df_rect


def ecef2enu(df_ecef, XYZ_ref, lat_rad_deg_dec, long_deg_dec_ref):
    # https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#Geodetic_to/from_ENU_coordinates
    
    X = df_ecef[["X"]].to_numpy().squeeze()
    Y = df_ecef[["Y"]].to_numpy().squeeze()
    Z = df_ecef[["Z"]].to_numpy().squeeze()
    
    XYZ_p = np.squeeze(np.stack((X,Y,Z),axis=0))
    
    # right hand side : translated by ref point coordinates
    b =  XYZ_p - np.expand_dims(XYZ_ref,axis=1)
    
    # Build the tranformation matrix based on the ref poiunts ecef position and lat/long
    s_lng = math.sin(np.radians(long_deg_dec_ref))
    c_lng = math.cos(np.radians(long_deg_dec_ref))
    s_lat = math.sin(np.radians(lat_rad_deg_dec))
    c_lat = math.cos(np.radians(lat_rad_deg_dec))
    
    
    w1 = np.array([ -s_lng       ,  c_lng       , 0     ])
    w2 = np.array([ -s_lat*c_lng , -s_lat*s_lng , c_lat ])
    w3 = np.array([  c_lat*c_lng ,  c_lat*s_lng , s_lng ])
   
    W = np.stack((w1,w2,w3),axis=0)
    
    
    xyz_enu = W @ b
    
    df_enu =  pd.DataFrame(xyz_enu.T, columns=['x','y','z'])
    return df_enu

    
def ecef2ned(df_ecef, XYZ_ref, lat_rad_deg_dec, long_deg_dec_ref):
    # https://en.wikipedia.org/wiki/Local_tangent_plane_coordinates
    X = df_ecef[["X"]].to_numpy().squeeze()
    Y = df_ecef[["Y"]].to_numpy().squeeze()
    Z = df_ecef[["Z"]].to_numpy().squeeze()
    
    XYZ_p = np.squeeze(np.stack((X,Y,Z),axis=0))
    
    # right hand side : translated by ref point coordinates
    b =  XYZ_p - np.expand_dims(XYZ_ref,axis=1)
    
    # Build the tranformation matrix based on the ref poiunts ecef position and lat/long
    s_lng = math.sin(np.radians(long_deg_dec_ref))
    c_lng = math.cos(np.radians(long_deg_dec_ref))
    s_lat = math.sin(np.radians(lat_rad_deg_dec))
    c_lat = math.cos(np.radians(lat_rad_deg_dec))
    
    
    w1 = np.array([-s_lat*c_lng , -s_lat*s_lng  ,  c_lat ])
    w2 = np.array([-s_lng       ,  c_lng        ,  0     ])
    w3 = np.array([-c_lat*c_lng , -c_lat*s_lng  , -s_lat ])
   
    W = np.stack((w1,w2,w3),axis=0)
    
    
    xyz_ned = W @ b
    
    df_ned =  pd.DataFrame(xyz_ned.T, columns=['x','y','z'])
    return df_ned    

class TestGPSToCartesian(unittest.TestCase):
    def test_haifa_dist(self):
        
        pt_a_lat = 32.82909
        pt_a_lon = 34.97446
        h_a = 0
        
        pt_b_lat = 32.82815
        pt_b_lon = 34.97670
        h_b = 0
        
        # Expected distance based on google maps
        # https://www.google.com/maps/place/32%C2%B049'30.1%22N+34%C2%B058'57.3%22E/@32.8290408,34.9746617,21z/data=!4m4!3m3!8m2!3d32.82502!4d34.982573
        exp_dist_a_2_b_m = 233.74
        
       
        data = {'latitude': [pt_a_lat, pt_b_lat], 'longitude': [pt_a_lon, pt_b_lon], 'height':[h_a, h_b]}  
        gps_df_example = pd.DataFrame(data)  


        cart_ex = np.asarray(wgs842ecef(gps_df_example)).T
        x,y,z = cart_ex
        
        d_a2b = np.sqrt((x[0]-x[1])**2 + (y[0]-y[1])**2 + (z[0]-z[1])**2)
        self.assertTrue(isclose(d_a2b, exp_dist_a_2_b_m, rel_tol=exp_dist_a_2_b_m*0.05))
        
        
    def test_haifa(self):
        # lat = '48:51:24.6'
        # lon = '2:21:05.4'
        
        # lat_decimal = sum(x / 60 ** n for n, x in enumerate(map(float, lat.split(':'))))
        # lon_decimal = sum(x / 60 ** n for n, x in enumerate(map(float, lon.split(':'))))

        # target values were produced using the online calculator at 
        # https://tool-online.com/en/coordinate-converter.php
        # For conversion between different coordiate systems see also 
        # see also https://coordinates-converter.com/en/decimal/32.780347,35.021667?karte=OpenStreetMap&zoom=11
        lat_decimal = 32.825020 
        lon_decimal = 34.982573
        h = 0
        
        data = np.reshape([lat_decimal,lon_decimal,h],(1,3)) 
        gps_df_example = pd.DataFrame(data, columns= ['latitude','longitude','height'])


        cart_ex = np.asarray(wgs842ecef(gps_df_example)).T
        x,y,z = cart_ex
        self.assertTrue(isclose(x, 4395702.106, rel_tol=1e-3))
        self.assertTrue(isclose(y, 3075911.671, rel_tol=1e-3))
        self.assertTrue(isclose(z, 3437667.463, rel_tol=1e-3))  

def gps_to_cartesian_2(lat, lon, h):
    R = 6371e3  # Earth's radius in meters

    # Convert degrees, minutes, seconds to decimal degrees
    lat_decimal = sum(x / 60 ** n for n, x in enumerate(map(float, lat.split(':'))))
    lon_decimal = sum(x / 60 ** n for n, x in enumerate(map(float, lon.split(':'))))

    # Convert to radians
    lat_rad = math.radians(lat_decimal)
    lon_rad = math.radians(lon_decimal)

    # Calculate Cartesian coordinates
    x = (R + h) * math.cos(lat_rad) * math.cos(lon_rad)
    y = (R + h) * math.cos(lat_rad) * math.sin(lon_rad)
    z = (R + h) * math.sin(lat_rad)

    return x, y, z

def get_wgs84_geodetic_model():
   
    a =  6378137 # Equatorial_radius [m]
    f_inv = 298.257223563 # Reciprocal flattening
    w = 7.292115 * 1e-5 #Angular rate  rad/s
    g_m =  3.986004418 * 1e14 # Gravitational constant GM m^3/s^2
    
    f = 1/ f_inv    # ~ 0.00335281
    b = a*(1 - f)   # ~ 6356752.314m
    ecc = np.sqrt(f*(2 - f))   # ~ 0.08181919.
    
    R_N_funcHandle_lat = lambda x:  a/np.sqrt((1 - pow(ecc*np.sin(x), 2)))

    return a,ecc,f,R_N_funcHandle_lat
    
def map_scale(x_s, y_s, x_f, y_f, p_s,p_f):
    Hx = np.asarray([[1.0, x_s],[1.0, x_f]])
    rx = np.asarray([p_s[0],p_f[0]])
    x_sl = linalg.solve(Hx,rx)
    bx = x_sl[0]
    mx = x_sl[1]

    Hy = np.asarray([[1.0, y_s],[1.0, y_f]])
    ry = np.asarray([p_s[1],p_f[1]])
    y_sl = linalg.solve(Hy,ry)
    by = y_sl[0]
    my = y_sl[1]
    
    return mx,bx,my,by

def procrustes_alignment_by_edge_points(ref_data, tgt_start, tgt_finish):
    from py_utils import utils_LinearAlgebra as lin
    # compute the procrustes transformation that aligns the matrices in terms of LS
    # extract only spatial info
    ref_h = ref_data[0:2,:] 
    # convert to homogeneous coordinates
    ref_h = np.append(ref_h,np.ones((1,ref_h.shape[1])),axis=0)
    #compute the transformation
    X = np.squeeze(np.asarray([[ref_h[:,0]],[ref_h[:,-1]]])).T
    Y = np.squeeze(np.array([tgt_start,tgt_finish])).T
    Y = np.append(Y, np.ones((1,2)),axis=0)
    X_, T = lin.procurustes_tranasformation(X, Y)
    # apply it
    
    ref_algn = T@ref_h
    
    return ref_algn, T

def trip_align_by_endpoints(X, p_start, p_finish, maxIter = 10):    
    # LinearDataAlignment
    pose_dim = np.size(p_start)
    X_aligned = X
    misalign_error = X_aligned[:-1,[0,-1]] - np.column_stack((p_start,p_finish))
    iterCnt = 0
    T_align = np.identity(pose_dim+1)

    while linalg.norm(misalign_error,'fro')>1e-3 and iterCnt < maxIter:
        iterCnt+=1
        X_aligned, T = procrustes_alignment_by_edge_points(X_aligned, p_start, p_finish)
        misalign_error = X_aligned[:-1,[0,-1]] - np.column_stack((p_start,p_finish))
        T_align = T@T_align

    return X_aligned, T_align
    
def trip_view_on_image(image_path, xdata,ydata, titleLabel, pathcolor):
    from matplotlib import image
    #%% Plotting the trajectory from the GPS
    # read the image
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    tripImage = image.imread(image_path)
    # fig_trip, ax_trip = plt.subplots()
    # fig, ax = plt.subplots()

    with plt.ioff():
        fig, ax = plt.subplots()
        
    ax.imshow(np.flipud(tripImage), origin= 'lower')

    fig.suptitle(titleLabel,fontsize = 16)
    # Enable scroll to zoom with the help of MPL
    # Interactions library function like ioff and zoom_factory.    
    plt.scatter(xdata,ydata,s=10, c = xdata**2+ydata**2)
    plt.plot(xdata,ydata,pathcolor,linewidth=1.0)

    disconnect_zoom = zoom_factory(ax)
    # Enable scrolling and panning with the help of MPL
    # Interactions library function like panhandler.
    pan_handler = panhandler(fig)
    # display(fig.canvas)k

    plt.show(block=False)
    plt.pause(0.001)
    return plt    

def trip_view_on_map(trail_coordinates, mapLabel = 'map'):
    #""Trail coordinates - Nx2 array of [lat,long] 
    m_mean = np.mean(trail_coordinates,axis=0)
    m = folium.Map(location=[m_mean[0],m_mean[1]], zoom_start=50)
    folium.PolyLine(trail_coordinates, tooltip=None).add_to(m)
    downsamp_trail_coordinates = trail_coordinates[::100,:]
    for index in range(downsamp_trail_coordinates.shape[0]):
        point = downsamp_trail_coordinates[index,:]
        folium.CircleMarker(point, radius=1,color="red").add_to(m)
    # folium.PolyLine(downsamp_trail_coordinates, tooltip=None, color="red", fill="none", **{"stroke": True, "stroke-dasharray":4}).add_to(m)
    # folium.Marker(m_mean, popup=None).add_to(m)
    # save the map as an HTML file

    #  Add clear marking for beginning and end points of the trip
    path_start = trail_coordinates[0,:]
    path_end = trail_coordinates[-1,:]
    folium.CircleMarker(path_start, radius=3, color="green").add_to(m)
    folium.CircleMarker(path_end, radius=3, color="black").add_to(m)

    os.makedirs('Results/', exist_ok=True)
    mapName = 'Results/'+mapLabel+'.html'
    m.save(mapName)
    return m, mapName
