from __future__ import annotations
from gflow.vehicle import Vehicle
from gflow.cases import Case, Cases
from typing import List
import time

from time import sleep
import time
from djitellopy import TelloSwarm
# from voliere import VolierePosition
# from voliere import Vehicle as Target
import numpy as np
from numpy.typing import ArrayLike
import requests


#write a function which converts xyz coordinates to ENU coordinates
def xyz_to_enu(x,y,z,lat,lon):
    '''Converts xyz coordinates to ENU coordinates'''
    R = 6378137 # Earth radius in meters
    phi = lat*np.pi/180
    lambda_ = lon*np.pi/180
    x_e = R*np.cos(phi)*np.cos(lambda_) + x
    y_e = R*np.cos(phi)*np.sin(lambda_) + y
    z_e = R*np.sin(phi) + z
    return x_e, y_e, z_e


def initialize_id_swarm(ac_list:list)->tuple[list,TelloSwarm]:
    '''Initialise the parameters'''
    ip_list = [_[2] for _ in ac_list]
    swarm = TelloSwarm.fromIps(ip_list)

    id_list = [_[1] for _ in ac_list]
    for i, id in enumerate(id_list):
        swarm.tellos[i].set_ac_id(id)
    
    return id_list, swarm




def connect_swarm(swarm)->None:
    print('Connecting to Tello Swarm...')
    swarm.connect()
    print('Connected to Tello Swarm...')
    return None

# def initialise_voliere(swarm,AC_ID_LIST):
#     voliere = VolierePosition(AC_ID_LIST, swarm.tellos, freq=40)
#     voliere.run()
#     sleep(4)

    # return voliere

# def convert_coords(desired):
#     tello_input = np.array([-desired[1], desired[0],0])
#     return tello_input

def step_simulation(swarm:TelloSwarm, case:Case):
    # case.from

    case_vehicle_list = case.vehicle_list
    max_avoidance_distance = case.max_avoidance_distance
    # for idx,vehicle in enumerate(case_vehicle_list):
    #     #update the simulated vehicle with its real position
    #     real_position = swarm.tellos[idx].get_position_enu()
    #     vehicle.position = real_position
    """'Step the simulation by one timstep, list_of_vehicles is case.vehicle_list"""
    for idx, vehicle in enumerate(case_vehicle_list):
        # if the current vehicle has arrived, do nothing, continue looking at the other vehicles
        # print("close to goal?",np.linalg.norm(vehicle.position-case.vehicle_list[0].goal)<0.5, f"state = {vehicle.state}")
        if vehicle.state == 1 or np.linalg.norm(vehicle.position-case.vehicle_list[idx].goal)<0.25:
            if not vehicle.has_landed:
                vehicle.state=1
                # swarm.tellos[idx].send_velocity_enu(convert_coords([0,0,0]), heading=0)
                # Perform the landing sequence once
                # time.sleep(0.5)
                print("landing")
                swarm.tellos[idx].send_velocity_enu([0,0,0], heading=0)
                # swarm.tellos[idx].move_down(40)
                # swarm.tellos[idx].land()
                vehicle.has_landed = True
                pass
            else:
                swarm.tellos[idx].send_velocity_enu([0,0,0], heading=0)

            # Skip the rest of the loop and continue with the next vehicle
            continue

        #update the simulated vehicle with its real position again
        real_position = swarm.tellos[idx].get_position_enu()
        vehicle.position = real_position
        # update the vehicle's personal knowledge of other drones by only keeping those that meet specific conditions:
        # not too far, have not arrived yet, and are transmitting.
       
        vehicle.update_personal_vehicle_dict(case_vehicle_list,max_avoidance_distance)
        vehicle.update_nearby_buildings(threshold = case.building_detection_threshold) #meters


        vehicle.run_simple_sim(mode='radius')


        velocity = vehicle.velocity
        velocity[2] = 0 #ensure z velocity is 0

        # send_to_server(id = swarm.tellos[idx].ac_id, vec = velocity)
        # print(f"In file running_utils.py, velocity is {velocity}")
        # velocity = velocity * 1
        swarm.tellos[idx].send_velocity_enu(velocity, heading=0)

    return None

def send_to_server(id, vec:ArrayLike):
    '''Method to send a vehicles latest instruction to the server'''
    url = 'http://127.0.0.1:8000/desired'
    data = {str(id):[vec[0], vec[1], vec[2]]}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=data, headers=headers)
    except Exception:
        pass

def run_real_case(
    case: Case,
    swarm,
    t=500,
    update_every: int = 1,
    stop_at_collision=False,
    max_avoidance_distance=20,
):
    """function which runs the simulation for t seconds while updating the drone positions wrt each other every update_time seconds
    Returns true if simulation run to the end without collistions, False if there is a collision. Note the collision threshold
    is an attribute of the Case class and can be set with case.collision_threshold = 5 for updates every 5 seconds"""
    collisions = False
    # arrived = set()
    # case_vehicle_list = case.vehicle_list
    start_time = time.time()
    
    # file_name = "examples/case3.json"
    # case_name="essai"
    # # case = Cases.get_case(filename="bug_fixing/cases.json", case_name="ignore_arrived")
    # case = Cases.get_case(file_name=file_name, case_name=case_name)

    while time.time()-start_time < t:
        # Step the simulation

        step_simulation(swarm, case)

        if case.colliding():
            # a collision has been detected, do whatever you want
            collisions = True
            if stop_at_collision:
                return False
        
        #stop as soon as any vehicle reaches its destination
        # for vehicle in case.vehicle_list:
        #     if vehicle.state == 1:
        #         return True
        # introduce logic that checks if all drones in case.vehicle_list have state 1, is so, return True
        if all(vehicle.state == 1 for vehicle in case.vehicle_list):
            return True
        
        time.sleep(0.05)
        # Communication Block
        # for vehicle in case.vehicle_list:
        #     if i % update_every == 0:
        #         vehicle.transmitting = True
        #     else:
        #         vehicle.transmitting = False

    end_time = time.time()
    print(f"Simulation took {end_time - start_time} seconds")
    if collisions:
        return False
    return True