import sys
sys.path.append('.')
from common.voliere import VolierePosition
from common.running_utils import initialize_id_swarm

#---------- OpTr- ACID - -----IP------
ACS = ['60','61','62','63','64','65','66','67','68','69', '51', '888','881','882','883','887','889']
TELLO_ACS = ['60','61','62','63','64','65','66','67','68','69']


AC_LIST = [[f"{ID}", f"{ID}", f'192.168.1.{ID}'] for ID in ACS if ID in TELLO_ACS]
# AC_ID_LIST = [[_[0], _[1]] for _ in AC_LIST] # [['51', '51'], ['65', '65'], ['69', '69']]


# CASE_INFO:dict = {
#         "filename": 'cases.json',
#         "casename": 'DASC23_case_1T',
#     }

# id_list, swarm = initialize_id_swarm(AC_LIST)   

def start_voliere(swarm):
    
    # connect_swarm(swarm)
    id_dict = {ID:ID for ID in ACS}
    vehicles = {tello.ac_id: tello for tello in swarm.tellos}
    voliere = VolierePosition(id_dict, vehicles, freq=20, vel_samples=6)
    print("Starting Natnet3.x interface at %s" % ("1234567"))
    voliere.run()
    
    # voliere.stop()
    # swarm.end()
    # time.sleep(1)

if __name__ == '__main__':
    id_list, swarm = initialize_id_swarm(AC_LIST)   
    start_voliere(swarm)
