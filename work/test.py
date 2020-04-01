#!/usr/bin/env python3

import os
import lgsvl

# TODO:引数チェック
sceneName = "kashiwanoha"
sim_host = {"address":os.environ.get("SIMULATOR_HOST","127.0.0.1"), "port":8181}
bridge_host = {"address":os.environ.get("BRIDGE_HOST"),"port":9090}

sim = lgsvl.Simulator(sim_host['address'],sim_host['port'])

# currentScene設定
if sim.current_scene == sceneName:
  sim.reset()
else:
  sim.load(sceneName)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]

# egovehicle追加
ego = sim.add_agent("Tier4Lexus", lgsvl.AgentType.EGO,state)

if bridge_host['address'] is not None:
  print("connect bridge:",bridge_host)
  ego.connect_bridge(bridge_host['address'], bridge_host['port'])

# signal置く
controllables = sim.get_controllables()
print("controllables objects :", len(controllables))
for s in controllables:
  s.control("trigger=30;red=60;green=60;yellow=4;loop")

sim.set_time_of_day(18,fixed=True)

# 実行?
sim.run(0,1)

print("finish...")
