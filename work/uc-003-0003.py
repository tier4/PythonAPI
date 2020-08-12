#!/usr/bin/env python3
import os
import lgsvl
import argparse


def npc_gen(sim,npctype,pos,rotY):
    astate = lgsvl.AgentState()
    astate.transform.position = pos
    astate.transform.rotation = lgsvl.Vector(0,rotY,0)
    agent = sim.add_agent(npctype,lgsvl.AgentType.NPC,astate)
    return agent

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

print("sim : {0}:{1}".format(sim_addr,sim_port))
print("bridge : {0}:{1}".format(br_addr,br_port))

sim = lgsvl.Simulator(sim_addr,sim_port)

# sceneのload
current_scene = sim.current_scene
print("current,load = {0},{1}".format(current_scene,args.environment))
if current_scene == args.environment:
    sim.reset()
else:
    sim.load(args.environment)


# NPC Car設置

npc = npc_gen(sim,"Sedan",lgsvl.Vector(-38.5,0,-5.2),64)

# counter coneの設置

ccone = sim.controllable_add("CounterCone")
controllables = sim.get_controllables()
for c in controllables:
    print("type: " + c.type)
    print("state: " + str(c.transform))

state = lgsvl.ObjectState()
state.transform.position = lgsvl.Vector(-19,0,4)
ccone.object_state = state

# egovehicle追加
spawns = sim.get_spawn()
state = lgsvl.AgentState()
state.transform.position = lgsvl.Vector(-56,0,-15)
state.transform.rotation = lgsvl.Vector(0,64,0)
counter = 0
ego = sim.add_agent(args.ego, lgsvl.AgentType.EGO,state)
# ego.on_collision(lambda a0,a1,contact: ego_on_collision(counter,ccone,a0,a1,contact))
if br_addr != None:
    ego.connect_bridge(br_addr,br_port)

def ego_hitcallback(a0,a1,contact):
    r0 = 0
    if a1 is None:
        print("Success")
    else:
        print("Failure")
        r0 = 1
    exit(r0)


# npc.on_collision()
ego.on_collision(ego_hitcallback)

# 適当にシミュレーション開始
try:
    print("sim start")
    sim.run()
except KeyboardInterrupt as k:
    pass
finally:
    pass

print("exit")









