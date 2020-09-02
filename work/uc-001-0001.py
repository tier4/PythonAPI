#!/usr/bin/env python3
import os
import lgsvl
import argparse
import threading
import time


MAX_EGO_SPEED = 11.18 # (40 km/h, 25 mph)
SPEED_VARIANCE = 10 # Simple Physics does not return an accurate value
MAX_POV_SPEED = 8.94 # (32 km/h, 20 mph)
MAX_POV_ROTATION = 5 #deg/s
TIME_LIMIT = 30 # seconds
TIME_DELAY = 3
MAX_FOLLOWING_DISTANCE = 50 # Apollo 3.5 is very cautious


def ms2kmh(ms):
    r0 = ms * 60 * 60 / 1000
    return r0

def kmh2ms(kmh):
    r0 = kmh / 60 / 60 * 1000
    return r0


def ego_on_collision(cone,npc,ego,a0,a1,contact):
    name0 = "static obstacle0" if a0 is None else a0.name
    name1 = "static obstacle1" if a1 is None else a1.name

    pc = counter

    if a1 is not None:
        return

    obj = lgsvl.ObjectState()
    obj.transform.position = lgsvl.Vector(63.7,0,46.5)
    npc.follow_closest_lane(True, 11.1)       
    threading.Thread(target=ego_speed_check,args=([ego])).start()

    cone.control("trigger=0")
    cone.object_state = obj


def ego_speed_check(ego):
    print("ego_speed_check: " + str(ego))
    while True:
        state = ego.state
        print("ego speed: " + str(ego))
        time.sleep(1)
        

parser = argparse.ArgumentParser()
parser.add_argument('ego',help='ego car name')
parser.add_argument('environment',help='map name')
parser.add_argument('--bridge',help='bridge ip address addr:port port default is 9090')
parser.add_argument('--sim_addr',help="simulator ip address addr:port port default is 8181")

args = parser.parse_args()

# 各ip/portの設定
sim_addr = "127.0.0.1"
sim_port = 8181

if args.sim_addr != None:
    sim_addr_port = args.sim_addr.split(':')
    sim_addr = sim_addr_port[0]
    if 1 < len(sim_addr_port):
        sim_port = int(sim_addr_port[1])

br_addr = None
br_port = 9090
if args.bridge != None:
    br_addr_port = args.bridge.split(':')
    br_addr = br_addr_port[0]
    if 1 < len(br_addr_port):
        br_port = int(br_addr_port[1])

sim = lgsvl.Simulator(sim_addr,sim_port)

# sceneのload
sim.load(args.environment,2)
sim.reset()

spawns = sim.get_spawn()

# counter coneの設置

ccone = sim.controllable_add("CounterCone")
print("ccone: {0} : {1}".format(str(ccone.uid),ccone.valid_actions))
controllables = sim.get_controllables()
for c in controllables:
    print("type: " + c.type)
    print("state: " + str(c.transform))

state = lgsvl.ObjectState()
state.transform.position = lgsvl.Vector(-50,0,-12)
ccone.object_state = state

# egovehicle追加
spawns = sim.get_spawn()
state = lgsvl.AgentState()
state.transform = spawns[0] # position弄る時はここを
counter = 0
ego = sim.add_agent(args.ego, lgsvl.AgentType.EGO,state)
if br_addr != None:
    ego.connect_bridge(br_addr,br_port)

# NPC
state = lgsvl.AgentState()

forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])


# state.transform = sim.map_point_on_lane(lgsvl.Vector(spawns[0].position.x, spawns[0].position.y, spawns[0].position.z + 30))
state.transform = sim.map_point_on_lane(lgsvl.Vector(spawns[0].position.x, spawns[0].position.y, spawns[0].position.z + 40))

npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)

# If the passed bool is False, then the NPC will not moved
# The float passed is the maximum speed the NPC will drive
# 11.1 m/s is ~40 km/h

ego.on_collision(lambda a0,a1,contact: ego_on_collision(ccone,npc,ego,a0,a1,contact))

# 適当にシミュレーション開始
r0 = 0
try:
    t0 = time.time()    

    while True:
        sim.run(1)

        egoCurrentState = ego.state
        if MAX_EGO_SPEED + SPEED_VARIANCE < egoCurrentState.speed:
            r0 = 1
            break

        POVCurrentState = npc.state
        if MAX_POV_SPEED + SPEED_VARIANCE < POVCurrentState.speed:
            r0 = 1
            break
    
        if MAX_POV_ROTATION < POVCurrentState.angular_velocity.y:
            r0 = 1
            break

        if TIME_LIMIT < time.time() - t0:
            break
   

except KeyboardInterrupt as k:
    pass
finally:
    pass

if r0 == 0:
    print("Sucess")
else:
    print("Failure")

print("exit")









