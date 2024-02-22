import sys
sys.path.insert(0,"./common")
from common.NatNetClient import NatNetClient
# from PyQt5.QtCore import pyqtSignal, QObject, QTimer, pyqtSlot
# from PyQt5.QtWidgets import QApplication
from collections import deque
import numpy as np
import socket
import threading
import json
from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#   from simple_sim import CaseMaker

id_dict = dict([('51','51'),('65','65'),('69','69'),('68','68')]) # rigidbody_ID, aircraft_ID
freq = 10
vel_samples = 20

#------------------------------------------------------------------------------
timestamp = dict([(ac_id, None) for ac_id in id_dict.keys()])
track = dict([(ac_id, deque()) for ac_id in id_dict.keys()])
period = 1. / freq

#------------------------------------------------------------------------------

class Rigidbody():
  def __init__(self,ac_id):
    self.ac_id = ac_id
    self.valid = False
    self.position = np.zeros(3)
    self.velocity = np.zeros(3)
    self.heading = 0.
    self.quat = np.zeros(4)

def store_track(ac_id, pos, t):
  if ac_id in id_dict.keys():
    track[ac_id].append((pos, t))
    if len(track[ac_id]) > vel_samples:
      track[ac_id].popleft()

def compute_velocity(ac_id):
  vel = [ 0., 0., 0. ]
  if len(track[ac_id]) >= vel_samples:
    nb = -1
    for (p2, t2) in track[ac_id]:
      nb = nb + 1
      if nb == 0:
        p1 = p2
        t1 = t2
      else:
        dt = t2 - t1
        if dt < 1e-5:
          continue
        vel[0] += (p2[0] - p1[0]) / dt
        vel[1] += (p2[1] - p1[1]) / dt
        vel[2] += (p2[2] - p1[2]) / dt
        p1 = p2
        t1 = t2
    if nb > 0:
      vel[0] /= nb
      vel[1] /= nb
      vel[2] /= nb
  return vel


class ClientVoliere:
    # signal for voliere data (AC_ID, pos_x, pos_y,pos_z, quat_a, quat_b, quat_c, quat_d)
    # drone_data = pyqtSignal(int, float, float, float, float, float, float, float)
    pos = []
    def __init__(self, class_instance):
        super().__init__()
        self.class_instance = class_instance
        # create NatNetClient to retrieve data from Motion Tracking
        self.natnet = NatNetClient()

    def start(self):
        # Start the server and other processing here
        self.natnet.set_server_address("192.168.1.240")
        self.natnet.set_client_address('0.0.0.0')
        self.natnet.set_print_level(0)
        self.natnet.rigid_body_list_listener = self.receiveRigidBodyList
        self.natnet.run()

    def stop(self):
        self.natnet.stop()

    def receiveRigidBodyList(self, rigid_body_data, stamp ):
        for idx, rigid_body in enumerate(rigid_body_data.rigid_body_list):
            # print(f"idx = {idx}")
            if not rigid_body.tracking_valid:
                # skip if rigid body is not valid
                continue
           
            i = str(rigid_body.id_num)

            if i not in id_dict.keys():
                continue
                
            pos = rigid_body.pos
            quat = rigid_body.rot
            
            store_track(i, pos, stamp)

            rgbs = dict([(ac_id, Rigidbody(ac_id)) for ac_id in id_dict.keys()])

            if timestamp[i] is None or abs(stamp - timestamp[i]) < period:
                if timestamp[i] is None:
                 timestamp[i] = stamp
                continue # too early for next message
            timestamp[i] = stamp
            # self.drone_data.emit(int(i), pos[0], pos[1], pos[2], quat[0], quat[1], quat[2], quat[3])
            # print(self.class_instance.swarm)
            # if self.class_instance.swarm is not None:
            #    self.class_instance.swarm.tellos[0].set_position_enu(np.array([pos[0], pos[1], pos[2]]))
            # self.class_instance.pos[idx] = [int(i), pos[0], pos[1], pos[2]]
            self.class_instance.drones[idx] = [pos[0], pos[1], pos[2]+4]

            # print(f" position is {self.pos}")


# if __name__ == "__main__":
#     import sys
#     import threading
#     app = QApplication([])
#     vvt = ClientVoliere()
#     vvt.drone_data.connect(print)
#     # app.aboutToQuit.connect(vvt.stop)
#     sys.exit(app.exec_())


# if __name__ == "__main__":
#     app = QApplication([])

#     def update_position(ac_id, x, y, z, qa, qb, qc, qd):
#         # Update GUI or process data here
#         print(f"Drone {ac_id} position: {x}, {y}, {z}")

#     vvt = ClientVoliere()
#     vvt.drone_data.connect(update_position)

#     # Run the ClientVoliere in a separate thread
#     threading.Thread(target=vvt.run, daemon=True).start()

#     sys.exit(app.exec_())


# if __name__ == "__main__":
#   app = QApplication([])

#   vvt = ClientVoliere()
#   vvt.drone_data.connect(print)

#   # Start the ClientVoliere in a separate thread
#   threading.Thread(target=vvt.start, daemon=True).start()
#   sys.exit(app.exec_())
#   print("hi")
            
class Random:
   def __init__(self,N) -> None:
      self.drones = np.zeros((N,3))
      self.swarm = None


if __name__ == "__main__":
      import time
      N=3
      instance = Random(N)
      vvt = ClientVoliere(instance)

      # Start the ClientVoliere in a separate thread
      threading.Thread(target=vvt.start, daemon=True).start()
      for i in range(10):
         time.sleep(1)
         print(instance.drones)