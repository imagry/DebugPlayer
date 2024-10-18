class VehicleConfigBase():
    def __init__(self, vehicle_name = None,
                 vehicle_type = None,
                 vehicle_model= None, 
                 vehicle_year= None,
                 vehicle_width_meters= None,
                 vehicle_length_meters= None, 
                 vehicle_wheels_base= None,
                 vehicle_fron_axle_offset= None, 
                 vehicle_center_of_gravity_offset_from_front_axle = None,
                 steering_ratio= None,):
        
        self.vehicle_name = vehicle_name
        self.vehicle_type = vehicle_type
        self.vehicle_model = vehicle_model
        self.vehicle_year = vehicle_year
        self.vehicle_width_meters = vehicle_width_meters
        self.vehicle_length_meters = vehicle_length_meters
        self.vehicle_wheels_base = vehicle_wheels_base
        self.vehicle_fron_axle_offset = vehicle_fron_axle_offset
        self.vehicle_center_of_gravity_offset_from_front_axle = vehicle_center_of_gravity_offset_from_front_axle
        self.steering_ratio = steering_ratio
        
        
                
niro_ev2 = VehicleConfigBase(vehicle_name = 'niro_ev2', 
# https://www.kiamedia.com/us/en/models/niro-ev/2024/specifications                            
                             vehicle_width_meters=1.825,
                             vehicle_length_meters=  4.420,
                             vehicle_wheels_base= 2.720,
                             vehicle_fron_axle_offset=0.895,
                             steering_ratio = 13.3
                             )

Nissan_Ariya = VehicleConfigBase(vehicle_name = 'Nissan_Ariya',
# file:///home/thamam/Downloads/Specifications%20-%202024%20Nissan%20Ariya%20FWD.pdf
                                 vehicle_width_meters= 1.850,
                                 vehicle_length_meters= 4.595,
                                 vehicle_wheels_base= 2.775,
                                 vehicle_fron_axle_offset= 0.950,
                                 steering_ratio = 13.9)


Passat_V8 = VehicleConfigBase(vehicle_name = 'Passat_V8',
                              vehicle_width_meters= 1.830,
                              vehicle_length_meters= 4.767,
                              vehicle_wheels_base= 2.791,
                              vehicle_fron_axle_offset= 0.950,
                              steering_ratio = 13.6)        

#  See the link below for passat 2021 with different dimensions:
# https://media.vw.com/assets/documents/original/12408-2021PassatTechSpecsFINAL.pdf