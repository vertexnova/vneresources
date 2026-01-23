# vertexnova-resources

A separate repository for storing large resource files and test data for the VertexNova project. This repository is kept separate from the main source code to avoid bloating the main repository with large binary assets.

## Structure

```
resources/
├── models/          # Complete 3D models with associated textures and materials
├── meshes/          # Standalone mesh files (.ply, .stl, .obj)
├── materials/       # PBR (Physically Based Rendering) material texture sets
└── textures/        # Standalone texture images
```

## Usage

This repository can be cloned as a submodule or referenced directly by the VertexNova project to access test assets and resources during development and testing.