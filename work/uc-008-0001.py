#!/usr/bin/env python3
import os
import lgsvl
import argparse
import math
import random

EGO_START_POS = lgsvl.Vector(6.5,0,10.0)
EGO_START_ROT_Y = 154

def npc_random_gen(trailerAvailable):
    mindist = 10.0
    maxdist = 40.0
    while True:
        angle = random.uniform(0.0, 2*math.pi)
        dist = random.uniform(mindist, maxdist)
        spawn = random.choice(spawns)
        sx = spawn.position.x
        sy = spawn.position.y
        sz = spawn.position.z
        point = lgsvl.Vector(sx + dist * math.cos(angle), sy, sz + dist * math.sin(angle))
        state = lgsvl.AgentState()
        state.transform = sim.map_point_on_lane(point)

        if (trailerAvailable):
            truck = sim.add_agent("MackAnthemStandupSleeperCab2018", lgsvl.AgentType.NPC, state)
            truck.follow_closest_lane(True, 5.6)
            trailer = sim.add_agent("TrailerTruckTest", lgsvl.AgentType.NPC, state)
            trailer.set_behaviour("NPCTrailerBehaviour")
            sim.remote.command("agent/trailer/attach", {"trailer_uid": trailer.uid, "truck_uid": truck.uid})

        else:
            try:
                agentIndex = int(inp)
                if len(agents) < agentIndex:
                    print("index out of range")
                    continue

                agent = agents[agentIndex]["name"]
                print("Selected {}".format(agent))
                npc = sim.add_agent(agent, lgsvl.AgentType.NPC, state)

                if drunkDriverAvailable:
                    inp = input("make drunk driver? yN")
                if (inp == "y" or inp == "Y"):
                    npc.set_behaviour("NPCDrunkDriverBehaviour")
                    npc.remote.command("agent/drunk/config", { "uid": npc.uid, "correctionMinTime":0.0, "correctionMaxTime":0.6, "steerDriftMin": 0.00, "steerDriftMax":0.09})

                npc.follow_closest_lane(True, 5.6)
                print("spawned agent {}, uid {}".format(agent, npc.uid))

            except ValueError:
                print("expected a number")    


def ego_on_collision(counter,cone,a0,a1,contact):
    name0 = "static obstacle0" if a0 is None else a0.name
    name1 = "static obstacle1" if a1 is None else a1.name
    pc = counter
    if a1 is None:
        counter += 1

    if pc != counter:
        obj = lgsvl.ObjectState()
        if counter == 1:
            obj.transform.position = lgsvl.Vector(63.7,0,46.5)           
        elif counter == 2:
            obj.transform.position = lgsvl.Vector(-53.38,0,-13.84)
        obj.transform.rotation = lgsvl.Vector(0,0,0)
        cone.control("trigger=0")
        counter %= 2
        cone.object_state = obj

    print('on_collision[{0}] : {1} , {2} => {3}'.format(counter,name0,name1,contact))

    return counter


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
sim.load("Reset")
sim.load(args.environment)
sim.reset()

# signalの制御
controllables = sim.get_controllables()
for c in controllables:
    if str(c.type) == "signal":
        c.control("red=60;green=60;yellow=4;red=3;loop")

# counter coneの設置
conePositions = [
    lgsvl.Vector(14.56,0,-32.2),
    lgsvl.Vector(33.5,0,-19.2)
]

for cp in conePositions:
    ccone = sim.controllable_add("CounterCone")
    cs = lgsvl.ObjectState()
    cs.transform.position = cp
    ccone.object_state = cs

state = lgsvl.ObjectState()
state.transform.position = lgsvl.Vector(-53.38,0,-13.84)
ccone.object_state = state

# egovehicle追加
spawns = sim.get_spawn()
state = lgsvl.AgentState()
state.transform.position = EGO_START_POS
state.transform.rotation = lgsvl.Vector(0,EGO_START_ROT_Y,0)
counter = 0
ego = sim.add_agent(args.ego, lgsvl.AgentType.EGO,state)

if br_addr != None:
    ego.connect_bridge(br_addr,br_port)

# signalが夜じゃないとちょっと検知辛い
sim.set_time_of_day(18,fixed=True)

# goalobjectに当ったら終了
def ego_hit_callback(a0,a1,contact):
    e0 = 0
    print(contact)
    if a1 is None:
        print("Success")
        pass # success
    else:
        print("Failure")
        e0 = 1
        pass # failure
    exit(e0)

ego.on_collision(ego_hit_callback)

# シミュレーション開始
try:
    print("sim start")
    sim.run()
except KeyboardInterrupt as k:
    pass
finally:
    pass

print("exit")









