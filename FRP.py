'''
Luke Wolf
FRP V1

Does not include distnace or range due to limited ifnromation, therefore some constraints are remvoed
'''
import gurobipy as gp
from gurobipy import GRB

G = ['a', 'b']
B = ['ev', 'nev']
T = [0,1]
nodes = ['node1', 'node2', 'node3', 'node4', 'node5', 'node6', 'node7', 'node8', 'node9']
arcs = {}
arcs['a'] = [('node1', 'node2'), ('node2', 'node3'), ('node3', 'node4'), ('node4', 'node5')]
arcs['b'] = [('node6', 'node7'), ('node7', 'node3'), ('node3', 'node8'), ('node8', 'node9')]
inflow = {(b, node): 1 for b in B for node in nodes}
L = ['hub1', 'hub2', 'hub3', 'hub 4'] #3a: Third Party Hubs, They are assumed at every 2nd arc in the network therefore 4 hubs will suffice for this model
#d = {(i, j): 1 for g in G for i, j in arcs[g]} #3b: Distance Between Nodes
#R = 0.75 #3b: Maximum Distance Between Hubs and Nodes
K = list(range(20))

m = gp.Model("frlm")


demand = m.addVars(((g, b, i, j, t) for g in G for b in B for t in T for (i,j) in arcs [g]), name="demand")

Y = {(g, i, j, t): m.addVar(name=f"Y_{g}_{i}_{j}_{t}") for g in G for (i,j) in arcs[g] for t in T}
Z = {(g, i, l, t): m.addVar(name=f"Z_{g}_{i}_{l}_{t}") for g in G for (i,j) in arcs[g][::2] for l in L for t in T}
X = {(g, b, i, j, t): m.addVar(name=f"X_{g}_{b}_{i}_{j}_{t}") for g in G for b in B for (i,j) in arcs[g] for t in T}
theta = {(g, b, i, j, t): m.addVar(name=f"theta_{g}_{b}_{i}_{j}_{t}") for g in G for b in B for (i,j) in arcs[g] for t in T}
ncs = {(node, t): m.addVar(name=f"ncs_{node}_{t}") for node in nodes for t in T}
M = {(node, t): m.addVar(name=f"M_{node}_{t}") for node in nodes for t in T}
omega = {(node,t): m.addVar(vtype=GRB.BINARY, name=f"omega_{node}_{t}") for node in nodes for t in T}
alpha = {(t): m.addVar(name=f"alpha_{t}") for t in T}
V = {(b, k, t): m.addVar(name=f"V_{b}_{k}_{t}") for b in B for k in K for t in T}

#1: Number of Vehicles (Types) that fulling demand between nodes
m.addConstrs(
    (X[g,b,i,j,t] == demand[g, b, i, j, t] for g in G for b in B for (i,j) in arcs[g] for t in T),
    name="X"
)

#2: Conservation of Flow
m.addConstrs(
    (gp.quicksum(X[g,b,i, j, t] for t in T for b in B for (i,j) in arcs[g]) == inflow[b, node]
    for g in G for b in B for node in nodes if node in [i for i,j in arcs[g]] if node != "node1"),
    name="flow_conservation"
)

#3: In-house Hubs or Third Party Hubs Between Arcs
#DISTNACE UNKONWN NO SOLVE
'''m.addConstrs( 
    (X[g, 'ev', i, j, t] == Y[g, i, j, t] + Z[g, i, l, t] for g in G for (i, j) in arcs[g][::2] for t in T for l in L if d[i, j] > R), 
    name="charging_hubs"
)
'''
#4: Refuel Depleted Batteries at Hubs
m.addConstrs(
    (X[g, 'ev', i, j, t] == Y[g, i, j, t] + gp.quicksum(Z[g, i, l, t] for l in L if (g, i, l, t) in Z) for g in G for (i, j) in arcs[g] for t in T),
    name="refuel_batteries"
)

#5:Number of EVs supported by a Chargining Station
m.addConstrs(
    (Y[g, i, j, t] <= theta[g, b, i, j, t] * ncs[j, t]
    for g in G for b in B for (i, j) in arcs[g] for t in T),
    name="charging_station_support"
)

#6:Number of Charging Stations Supported By Existing Power Network
m.addConstrs(
    (ncs[j,t] <= M[j, t] * omega[j, t] for j in nodes for t in T),
    name="power_network_support"
)

#7: Number of Charging Station Per Year
m.addConstrs(
    (ncs[j, t] >= ncs[j, t-1] for j in nodes for t in range(1, len(T))),
    name="charging_station_per_year"
)

#8: Intermediate Electrification Goal (% of total VMT traveled by EVs)
#DISTNACE UNKONWN NO SOLVE
'''
m.addConstrs(
    (gp.quicksum(X[g, "ev", i, j, t] * d[i,j] for g in G for (i,j) in arcs[g] for t in T) >= alpha[t] * gp.quicksum(X[g, b, i, j, t] * d[i,j] for g in G for b in B for (i,j) in arcs[g] for t in T) for t in T),
    name="intermediate_electrification_goal"
)
'''

#9: Number of EVs in Year T
m.addConstr(
    (gp.quicksum(X[g, "ev", i, j, t] for g in G for (i,j) in arcs[g] for t in T) >= gp.quicksum(X[g, "ev", i, j, t-1] for g in G for (i,j) in arcs[g] for t in range(1, len(T)))),
    name="number_of_evs"
)

#10: The number of B Vehicles of Age K in Year T:  
m.addConstr(
    (gp.quicksum(V[b, k, t] for b in B for k in K for t in T) == gp.quicksum(X[g, b, i, j, t] for g in G for b in B for (i,j) in arcs[g] for t in T)),
    name="age_of_vehicles"
)
#Objective Functions
#Total Cost: The Unit Price of Purchasing Vehicle Type k in year T, Represented by Cveh


m.setObjective(0, GRB.MINIMIZE)
m.params.NonConvex = 2
m.update()
m.optimize()
m.write("frlm.lp")

"""for v in m.getVars():
    if v.VarName.startswith('flow'):
        print(f'Flow Variable: {v.VarName}, Value: {v.X}')
    elif v.VarName.startswith('demand'):
        print(f'Demand Variable: {v.VarName}, Value: {v.X}')
"""

# Solution Status Printed 
status = m.status
if status == GRB.Status.OPTIMAL :
  print("Model is optimal")
elif status != GRB.Status.OPTIMAL:
    if status == GRB.Status.UNBOUNDED:
        print("Model is unbounded")
    elif status == GRB.Status.INFEASIBLE:
        print("Model is infeasible") 
    elif status != GRB.Status.INF_OR_UNBD:
        print("Model was stopped with status %d" % status)
    exit(0)

X

demand