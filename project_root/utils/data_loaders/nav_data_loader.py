
def load_trip_gps_data(trip_path, coordinates_type, sample_spacing = 1, tangent_frame = "ENU"):
    # read position from gps data 
    filepathGPS =  trip_path +'/'+ 'gps.csv'
    # gps_header = ['time_stamp','latitude','longtitude','height','speed','sensor_time_counter']
    
    # Set the data types of your columns
    dtypes = {
        'latitude': 'float64',
        'longitude': 'float64',
        'height': 'float64',
        'time_stamp': 'float64'
        # Add more columns as needed
    }
    
    df_gps = pd.read_csv(filepathGPS, header=0, dtype=dtypes)
    df_wgs84 = df_gps[['latitude','longitude','height']].iloc[::sample_spacing,:]
    Xwgs84_long_lat = np.asarray(df_wgs84[['longitude','latitude','height']]).T
    time_vec_ = np.squeeze(np.asarray(df_gps[['time_stamp']].iloc[::sample_spacing,:]).T)
    # Xwgs84_h = np.append(Xwgs84,np.ones((1,Xwgs84.shape[1])),axis = 0)
    
    # adding the time_stamp column to the result
    Xwgs84_long_lat_ = np.hstack((Xwgs84_long_lat.T, time_vec_.reshape(-1, 1)))
    Xwgs84_long_lat = Xwgs84_long_lat_.T
  
    if coordinates_type=="wgs_84":
        return Xwgs84_long_lat
    
    # Then: coordinates_type=="both" or coordinates_type=="rect":
    # convert gps path from wgs84 to rectangular coordinates
    # a,e,f,RN_at_lat = geo.get_wgs84_geodetic_model()

    # print( abs(RN_at_lat(np.radians(34))  - RN_at_lat(np.radians(32)))/RN_at_lat(np.radians(32)))
    # geoModelParams = {'a':a,'e':e,'f':f,'RN_h':RN_at_lat}
    
    df_ecef = geo.wgs842ecef(df_wgs84[['longitude','latitude','height']])
    
    # set first coordinate as ENU reference point
    XYZ_ref = df_ecef.iloc[0,:]
    if tangent_frame=="ENU":
        df_tangent = geo.ecef2enu(df_ecef,XYZ_ref, df_wgs84['latitude'].iloc[0], df_wgs84['longitude'].iloc[0])
    elif tangent_frame=="NED":
        df_tangent = geo.ecef2ned(df_ecef,XYZ_ref, df_wgs84['latitude'].iloc[0], df_wgs84['longitude'].iloc[0])
    else:
        SystemError("Bad tangent_frame name \n")
        
    # xyz_enu = np.asarray(df_enu).T
    # # change into homogeneous coordinates     
    # X_rect_h = np.append(X_rect,np.ones((1,X_rect.shape[1])),axis = 0)
    
    # Adding time_stamp column
    df_tangent['time_stamp'] = time_vec_

    if coordinates_type=="rect":
        return df_tangent
    else: # coordinates_type == 'both'
        return Xwgs84_long_lat, df_tangent