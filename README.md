# Fleet Replacement Electrification Problem (FREP) Modeling

## Overview
This project, part of the USF ISME Department's research, focuses on the Simplified Operations Research Fleet Replacement Electrification Problem (FREP). It aims to address key challenges in fleet electrification and optimization. Please note that this is a basic version as the full paper is currently under development.

### Key Python Packages Used
- **Pandas**: For data manipulation and analysis.
- **NumPy**: For numerical operations.
- **Matplotlib**: For creating static, animated, and interactive visualizations.
- **Gurobipy**: Gurobi's Python API for optimization problems.
- **Seaborn**: For making statistical graphics.

## Data and Information Access
To access the data and information collected or to view the process of creating the FREP Modeling Paper, please visit my [OneDrive link](https://usfedu-my.sharepoint.com/:f:/g/personal/lawolf_usf_edu/Ek66cTeKZ_tOiRcBjoBbrTIBZ1QoQ1jFcITf-ns1XJhewg?e=DGE1fa).

## Visualizations
Below are some of the key visualizations created using Matplotlib and Seaborn. Please note these visualizations are prior to the Gurobipy solver solving the problem.

![Visualization 1](lawolf8/Fleet-Replacement-Electrification-Problem/FREP Visualizations/Transportation Sector Energy Prices, South Atlantic.png)
*Figure 1: Transportation Sector Energy Prices, South Atlantic*

### Visualization Code Example: Transportation Sector Energy Prices, South Atlantic
```python
# Code is what was used to generate the visualization above is created
eprices = np.array([32.204, 34.671, 35.106, 34.915, 33.552, 31.932, 30.705])

ecoeffs = np.polyfit(years, eprices, 3)
efit = np.poly1d(ecoeffs)
eprices_pred = efit(years)
er_squared = 1 - (np.sum((eprices - eprices_pred)**2) / np.sum((eprices - np.mean(eprices))**2))
plt.scatter(years, eprices, label="Price Point")
ex = np.linspace(2021, 2050, 1000)
plt.plot(ex, efit(ex), label="Cubic fit (R^2 = {:.8f})".format(er_squared))
plt.xlabel("Year")
plt.ylabel("Price ($/MMBtu)")
plt.title("Forecasted Transportation Sector Energy Prices (South Atlantic)")
plt.legend(), plt.show()

print("Equation: y = {:.8f}x^3 + {:.8f}x^2 + {:.8f}x + {:.8f}".format(coeffs[0], coeffs[1], coeffs[2], coeffs[3]))
print("R-squared value: {:.6f}".format(er_squared))
