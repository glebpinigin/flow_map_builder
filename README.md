# Flow Map Builder QGIS Plugin
QGIS plugin for automatically creating distributive flow maps
Stable working with QGIS 3.18 or higher or other 3.x versions with NetworkX installed

This plugin is a wrapper around python-based [flow distribution algorithm](https://github.com/glebpinigin/flowmapper). This repo only contains GUI declaration and logic, whereas QGIS API is implemented [here](https://github.com/glebpinigin/flowmapper/blob/273becddea8fca7af010484a0a9bb11fadd21474/flowmapper/io/apiqgis.py).

The plugin's core is an implementation of a greedy algorithm of approximation angle-restricted Steiner arborescence with no presence of obstacles, initially presented [in this artice](https://doi.org/10.48550/arXiv.1109.3316).

Details of underlying maths and results evaluation are availuable in russian [here](https://www.researchgate.net/publication/365775407_Capabilities_of_urban_activity_analysis_based_on_network_models).
<!---
## Distributive flow maps
--->
## Installation guide
1. Download ```.zip``` file with source code
2. Open QGIS
3. Click ```Plugins-Manage and Install Plugins-Install from ZIP```
4. Enter path to ```.zip``` file and click ```Install Plugin``` button.
<!---
## User quide
To be completed
--->
