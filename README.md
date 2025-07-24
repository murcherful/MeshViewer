# MeshViewer
This web app allows users to view all mesh files in a directory on the service machine.

This app is built with [nicegui](https://nicegui.io/) and [model-viewer](https://github.com/google/model-viewer). Only one lightweight file and one libaray you need to install. You can put it anywhere in your project.

#### Install
```
python -m pip install nicegui
```
#### Usage
Open the web app on your machin:
```
python mesh_viewer.py
```
This will open a app on `0.0.0.0:8081`. Open the url and input the directory you want to visulize. Press "GO!" to show all the meshes. 
