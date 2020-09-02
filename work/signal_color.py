#!/usr/bin/env python3
import os
import lgsvl
import argparse


def ego_on_collision(a0,a1,contact):
    name0 = "static obstacle0" if a0 is None else a0.name
    name1 = "static obstacle1" if a1 is None else a1.name
    print('on_collision : {0}({1}),{2}({3})'.format(name0,str(a0.uid),name1,str(a1.uid)))


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
sim.load(args.environment)
sim.reset()

# ego vehicleのload
spawns = sim.get_spawn()
state = lgsvl.AgentState()
state.transform.position = lgsvl.Vector(12.8,0,-2.48)
state.transform.rotation = lgsvl.Vector(0,153.3,0)

# egovehicle追加
ego = sim.add_agent(args.ego, lgsvl.AgentType.EGO,state)
ego.on_collision(ego_on_collision)
if br_addr != None:
    print("bridge connect : {0}:{1}".format(br_addr,str(br_port)))
    ego.connect_bridge(br_addr,br_port)

# counter coneの設置

ccone = sim.controllable_add("CounterCone")
controllables = sim.get_controllables()
for c in controllables:
    print("type: " + c.type)
    print("state: " + str(c.transform))
    if str(c.type) == "signal":
        signalControl = "green=5;yellow=5;red=5;loop"
        print(signalControl)
        c.control(signalControl)

state = lgsvl.ObjectState()
state.transform.position = lgsvl.Vector(-53.38,0,-13.84)
ccone.object_state = state

# 適当にシミュレーション開始
try:
    print("sim start")
    sim.run()
except KeyboardInterrupt as k:
    pass
finally:
    pass

sim.reset()
print("exit")









