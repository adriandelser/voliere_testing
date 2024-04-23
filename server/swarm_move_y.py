import gflow.utils.plot_utils as ut
from gflow.cases import Cases, Case
# from time import time, sleep
from gflow.utils.json_utils import load_from_json
from gflow.utils.simulation_utils import run_simulation, set_new_attribute
from gflow.utils.plot_utils import PlotTrajectories 
from gflow.plotting.main_plot import SimulationVisualizer
from scenebuilder.gui_sim import InteractivePlot
from scenebuilder.observer_utils import Observer
import sys

import time
from djitellopy import TelloSwarm
# sys.path.insert(0,"common_murat")
sys.path.append('.')

from common.voliere import VolierePosition
# from common_murat.voliere import Vehicle as Target
import numpy as np

from common.running_utils import initialize_id_swarm, connect_swarm, xyz_to_enu, run_real_case

# from drone_monitoring_better import ClientVoliere
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
import threading


#should probably pull this from json or something
NEXT_GOAL_LIST:list = [[ [0,0,0.5], [2,2,0.5], [3,2,0.5]],
                [ [-2,-2,1.5], [-2,-3.5,1.5]]]


#---------- OpTr- ACID - -----IP------
#---------- OpTr- ACID - -----IP------
ACS = ['60','61','62','64','65','66','67','68','69', '51', '888']
TELLO_ACS = ['64']


AC_LIST = [[f"{ID}", f"{ID}", f'192.168.1.{ID}'] for ID in ACS if ID in TELLO_ACS]
AC_ID_LIST = [[_[0], _[1]] for _ in AC_LIST] # [['51', '51'], ['65', '65'], ['69', '69']]


CASE_INFO:dict = {
        "filename": 'cases.json',
        "casename": 'DASC23_case_1T',
    }

# Generating an example Source for population
# population = [Source(ID=0, source_strength=0.8, position=np.array([-1., 3., 0.4]))]
POPULATION = None

# Define the distance at which the drone is considered to have arrived at destination
ARRIVAL_DISTANCE = 0.5

USE_PANEL_FLOW = True

def convert_coords(desired):
    tello_input = np.array([-desired[1], desired[0],0])
    return tello_input

class CaseMaker(Observer):
    def __init__(self) -> None:
        self.gui = InteractivePlot()
        self.gui.add_observer(self)
        self.pos = []
        self.swarm:TelloSwarm = None


    def call(self):
        print("Called!")
        #gflow part
        file_name = "scenebuilder.json"
        case_name="scenebuilder"
        case = Cases.get_case(file_name, case_name)
        print(f"{case.vehicle_list=}, {case.buildings =}")
        # if event != "generate_case":
        #     raise NotImplementedError
        if len(case.vehicle_list) != len(AC_LIST):
            print("Number of vehicles does not match!")
            return

        # set_new_attribute(case, "source_strength", new_attribute_value=1)
        set_new_attribute(case, "sink_strength", new_attribute_value=5)
        set_new_attribute(case, "max_speed", new_attribute_value=0.5)
        set_new_attribute(case, "imag_source_strength", new_attribute_value=5)
        set_new_attribute(case, "source_strength", new_attribute_value=1)
        # set_new_attribute(case, "mode", new_attribute_value="radius")
        set_new_attribute(case, "turn_radius", new_attribute_value=0.20)

        case.mode = 'radius'
        case.building_detection_threshold = 10
        case.max_avoidance_distance = 10
        # set_new_attribute(case, "")

        self.fly(case)
    

    def set_position(self, *args):
        print("set position called")
        self.pos = args

    def show(self)->None:
        self.gui.draw_scene()
        # threading.Thread(target=self.gui.draw_scene).start()

        
    def fly(self, case:Case):
        print(case, case.name)
        delta_t = case.vehicle_list[0].delta_t
        update_frequency = 50  # Hz
        update_time_period = max(int(1 / (update_frequency * delta_t)), 1)

        ######################################
        # this variable controls how many time steps occur between every communication of position
        # update_time_period = 10
        ######################################

        # print(f"update every = {update_time_period}")

        id_list, self.swarm = initialize_id_swarm(AC_LIST)
        print(f"ids are {id_list}")
        connect_swarm(self.swarm)

        # id_dict = dict([('65','65')]) # rigidbody_ID, aircraft_ID
        id_dict = {ID:ID for ID in ACS}
        print(f"id_dict = {id_dict}")
        # freq = 10
        # vel_samples = 20

        # vehicles = dict([(ac_id, Vehicle(ac_id)) for ac_id in id_dict.keys()])
        vehicles = {tello.ac_id: tello for tello in self.swarm.tellos}
        # print(id_dict.keys(), vehicles['69'].get_ac_id())
        # vehicles = [Vehicle(ac_id[1]) for ac_id in args.ac]
        voliere = VolierePosition(id_dict, vehicles, freq=20, vel_samples=6)
        
        

        # voliere=initialise_voliere(swarm,AC_ID_LIST)
        print("Starting Natnet3.x interface at %s" % ("1234567"))

        INIT_XYZS = {ACS[idx]: np.append(vehicle.position[:2],0.5) for idx, vehicle in enumerate(case.vehicle_list)}
        print(f"initial positions are {INIT_XYZS}")


        try:
            voliere.run()
            #takeoff everyone
            print(self.swarm.tellos[0].get_position_enu())
            time.sleep(1)
            self.swarm.takeoff()
            starttime = time.time()
            #make them all stop for 2 seconds
            while time.time()-starttime <4:
                for tello in self.swarm.tellos:
                    tello.send_velocity_enu([0,0,0], heading=0)
            

            starttime= time.time()

            # for the first x seconds, move the tellos to their initial positions
            while time.time()-starttime < 5:
                
                desired = [0.2,0,0]
                for idx, tello in enumerate(self.swarm.tellos):
                    # tello.fly_to_enu(INIT_XYZS[tello.ac_id], heading=0)
                    tello.send_velocity_enu(desired, heading=0)
            
            # # self.swarm.tellos[0].send_velocity_enu([0,0,0], heading=0)

            # print('Finished moving !') #Finished 
            # result = run_real_case(case=case,swarm=self.swarm,t = 500,update_every=1,stop_at_collision=True,max_avoidance_distance=20)

            
            # case.to_dict(file_path="realflight_output.json")
            # # # self.swarm.move_down(int(40))
            # self.swarm.land()
            # voliere.stop()
            # self.swarm.end()
            # # time.sleep(1)
            # # create ouput json

            # trajectory_plot = PlotTrajectories(case, update_every=1)
            # # trajectory_plot.BUILDING_EDGE_COLOUR
            # LIMS = (-5,5)
            # # XLIMS = (575600,576000)
            # # YLIMS = (6275100,6275700)
            # trajectory_plot.ax.set_xlim(LIMS)
            # trajectory_plot.ax.set_ylim(LIMS)
            # trajectory_plot.show()

            # # visualisation part
            # visualizer = SimulationVisualizer('realflight_output.json')
            # visualizer.show_plot()


            self.swarm.land()
            voliere.stop()
            self.swarm.end()

        except (KeyboardInterrupt, SystemExit):
            print("Shutting down natnet interfaces...")
            # log.save(flight_type='fast_follow')
            # self.swarm.move_down(int(40))
            self.swarm.land()
            # voliere.stop()
            self.swarm.end()

            time.sleep(1)

        except OSError:
            print("Natnet connection error")
            # self.swarm.move_down(int(40))
            self.swarm.land()
            # voliere.stop()
            self.swarm.end()
            exit(-1)






# def test_func(instance):
#     vvt = ClientVoliere(instance)
#     # vvt.drone_data.connect(print)  # Connect to the appropriate slot
#     vvt.start()  # Start collecting drone data

class Random:
   def __init__(self) -> None:
      self.pos = None

# if __name__ == "__main__":
#     # app = QApplication(sys.argv)  # Ensure only one QApplication instance
#     case_maker = CaseMaker()
#     vvt = ClientVoliere(case_maker)
#     threading.Thread(target=vvt.start, daemon=True).start()
#     for i in range(10):
#         if case_maker.swarm:
#             print(case_maker.swarm.tellos[0].get_position_enu())
#         time.sleep(0.1)
#     case_maker.show()



    # instance = Random()
    # vvt = ClientVoliere(instance)

    # # Start the ClientVoliere in a separate thread
    # threading.Thread(target=vvt.start, daemon=True).start()
    # for i in range(10):
    #     time.sleep(1)
    #     print(instance.pos)
    
    # Additional threads can be started here if needed
    # threading.Thread(target=some_function, daemon=True).start()

    # case_maker.run_drone_data()

    # sys.exit(app.exec_())  # Start the application loop here
    # case_maker = CaseMaker()
    # case_maker.show()
#EOF
    

if __name__ == "__main__":
    # app = QApplication(sys.argv)  # Ensure only one QApplication instance
    case_maker = CaseMaker()
    # vvt = ClientVoliere(case_maker)
    # threading.Thread(target=vvt.start, daemon=True).start()
    for i in range(10):
        if case_maker.swarm:
            print(case_maker.swarm.tellos[0].get_position_enu())
        time.sleep(0.1)
    case_maker.show()
    case_maker.call()
