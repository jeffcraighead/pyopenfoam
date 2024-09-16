## Folder Structure
 - `\case_folder`
   - `\0` - Contains files that define the initial and boundary conditions for the primary variables of the simulation (e.g., velocity, pressure, turbulence quantities).
     - `p` - file with initial and boundary conditions for pressure
     - `U` - file with initial and boundary velocity conditions
     - `T` - file with initial conditions for Temperature simulations
   - `\system` - Contains configuration files for controlling the simulation process (solver settings, discretization schemes, etc.).
     - `controlDict` - The main configuration file that controls the overall simulation settings, such as start and end times, time step size, and the frequency of output writing.
     - `fvSchemes` - Defines the numerical schemes used for discretizing the equations (e.g., time derivatives, gradient schemes, interpolation schemes).
     - `fvSolution` - Specifies the linear solvers and tolerances for different fields (like pressure and velocity), as well as relaxation factors for under-relaxation of iterative solvers.
     - `blockMeshDict` - is an essential file for generating a basic mesh in OpenFOAM using the blockMesh utility. This dictionary file defines the geometry, block structure, mesh grading, and boundary conditions for a simple geometry that can be meshed directly using the blockMesh utility.
     - `snappyHexMeshDict` - contains the settings for generating a complex mesh file from an STL file
   - `\constant` - Contains files related to the mesh and physical properties of the simulation.
     - `polyMesh` - This directory contains the mesh files generated by `blockMesh` or `snappyHexMesh`. The required files here are:
       - `boundary`: Defines boundary patches and their types. 
       - `faces`, `neighbour`, `owner`, `points`: Describe the mesh connectivity and geometry.
 

### Sample *snappyHexMeshDict*
```/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  8                                     |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/

castellatedMesh true;   // Generate the base mesh with castellations
snap true;              // Snap the mesh to the surface geometry
addLayers true;         // Add boundary layers

geometry
{
    yourGeometry.stl
    {
        type triSurfaceMesh;      // Specifies that the geometry is a triangulated surface
        name geometry;            // The name used to reference this geometry in other sections
    }
    // Additional geometry definitions if needed
}

// Settings for castellated (initial coarse) mesh generation
castellatedMeshControls
{
    maxLocalCells 1000000;        // Max number of cells per processor
    maxGlobalCells 2000000;       // Max number of cells overall
    minRefinementCells 10;        // Minimum number of cells for any refinement to happen
    nCellsBetweenLevels 3;        // Cells between different refinement levels

    // Refinement based on surface geometry
    refinementSurfaces
    {
        geometry
        {
            level (2 3);          // Min and max refinement levels for the surface
        }
    }
    
    // Region-wise refinement
    refinementRegions
    {
        // No regions defined in this example
    }

    // Resolve feature edges
    resolveFeatureAngle 30;        // Angle above which to keep feature edges
}

// Mesh snapping controls
snapControls
{
    nSmoothPatch 3;               // Number of smoothing iterations
    tolerance 2.0;                // Tolerance for snapping to surfaces
    nSolveIter 30;                // Number of solver iterations
    nRelaxIter 5;                 // Number of relaxation iterations
}

// Controls for layer addition
addLayersControls
{
    relativeSizes true;           // Use relative size specification
    layers
    {
        "geometry.*"
        {
            nSurfaceLayers 3;     // Number of layers to add near the surface
        }
    }

    expansionRatio 1.3;           // Ratio for layer expansion
    finalLayerThickness 0.3;      // Thickness of the final layer
    minThickness 0.1;             // Minimum thickness for layers
    nGrow 0;                      // Maximum number of layer addition iterations
}

// Mesh quality controls
meshQualityControls
{
    maxNonOrtho 65;               // Max allowable non-orthogonality
    maxBoundarySkewness 20;       // Max allowable skewness at boundaries
    maxInternalSkewness 4;        // Max allowable internal cell skewness
    // Additional quality control parameters can be defined here
}

// Advanced options for mesh merging
mergeTolerance 1e-6;              // Tolerance for merging mesh points
```