#!/usr/bin/env python3
import os
import lgsvl
import argparse
import random
import math
import threading
import time


def ego_on_collision(cone,a0,a1,contact):
    name0 = "static obstacle0" if a0 is None else a0.name
    name1 = "static obstacle1" if a1 is None else a1.name

    print('on_collision : {0} , {1} => {2}'.format(name0,name1,contact))

    r0 = 0
    if a1 is None:
        print("Success")
    else:
        print("Failure")
        r0 = 1
    exit(r0)


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
br_port = 9191
if args.bridge != None:
    br_addr_port = args.bridge.split(':')
    br_addr = br_addr_port[0]
    if 1 < len(br_addr_port):
        br_port = int(br_addr_port[1])

sim = lgsvl.Simulator(sim_addr,sim_port)

# sceneのload
sim.load(args.environment)
sim.reset()

spawns = sim.get_spawn()

# sim.add_random_agents(lgsvl.AgentType.NPC)

# counter coneの設置
ccone = sim.controllable_add("CounterCone")

state = lgsvl.ObjectState()
state.transform.position = lgsvl.Vector(31.2,0,-20)
ccone.object_state = state

# egovehicle追加
state = lgsvl.AgentState()
state.transform.position = lgsvl.Vector(-1.2,0,-23.6)
state.transform.rotation = lgsvl.Vector(0,152,0)

ego = sim.add_agent(args.ego, lgsvl.AgentType.EGO,state)
ego.on_collision(lambda a0,a1,contact: ego_on_collision(ccone,a0,a1,contact))
if br_addr != None:
    ego.connect_bridge(br_addr,br_port)

mindist = 10.0
maxdist = 40.0
random.seed(2)

sx = ego.transform.position.x
sy = ego.transform.position.y
sz = ego.transform.position.z

# NPC
for v in range(5):
    angle = random.uniform(0.0, 2*math.pi)
    dist = random.uniform(mindist, maxdist)
    point = lgsvl.Vector(sx + dist * math.cos(angle), sy, sz + dist * math.sin(angle))
    state = lgsvl.AgentState()
    state.transform = sim.map_point_on_lane(point)
    npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)
    npc.follow_closest_lane(True, 9.72)

# random_agentsはイケてないね..
# sim.add_random_agents(lgsvl.AgentType.NPC)

# 適当にシミュレーション開始
def sim_run(sim):
    t = threading.currentThread()
    while getattr(t,"do_run",True):
        sim.run(time_limit=1,time_scale=1)
        time.sleep(0)
    
    print("exit run_thread")
    

try:
    print("sim start")
    st = threading.Thread(target=sim_run,args=([sim]))
    st.start()
    
    st.join()
except KeyboardInterrupt as k:
    pass
finally:
#    t.do_run = False
    st.do_run = False

print("exit")

