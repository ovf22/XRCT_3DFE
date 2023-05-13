# Structure Tensor 3D FE Mapping

## Introduction

This method covers the process of aquireing volumetric material orientations in an anisotropic material and ultimately, run simulations in a Finite Element (FE) software with material orientations included, to quantify the constitutive behavior of the material. The method is demonstrated for a unidirectional carbon fiber-reinforced epoxy pultruded profile. The volumetric material orientations are quantified from a X-ray computed micro-tomography scan (X-ray μCT), where the image processing method called structure tensor analysis is used to estimate the dominant material orientations in the volume. The commercial FE software Abaqus<sup>TM</sup> is used for simulation of the material behavior when loaded in tension. 
This work is published together with the work by Ferguson et al. [1].

## Installation guide

This program is based on the Anaconda Distribution, where a virtual environment is used for running the analysis. The file S0_main.sh is the main script from where all analysis steps are controlled. This file also contains a function that installes the virtual environment and necessary Python packages. To enable this function set the parameter Env_installed="no". This should only be done the first time the shell script is executed. After installation of the virtual environment, set Env_installed="yes". 

## Directories and files
- code
	* S0_main.sh
		- Main shell script for running the entire analysis. Datasets for analysis are defined in this script. 
	* S1_STanalysis.py
		- Script for estimating material orientations and define FE model dimensions.
		- Input: X-ray μCT data.
		- Output: Arrays with orientation estimation. (MAP_Var.npz) and FE model dimensions (Tomo_dim.txt).
	* S2_Cube.py
		- Script for generating FE model with mesh.
		- Input: Model dimensions (Tomo_dim.txt).
		- Output: Integration point coordinates (INTCOOR.dat).
	* S3_mapping.py
		- Script for mapping orientations estimated in S1_STanalysis to FE mesh generated in S2_Cube.
		- Input: Material orientation information (MAP_Var.npz) and integration point coordinates (INTCOOR.dat).
		- Output: Fortran files with orientation information for all integration points.
	* S4_Cube_modified.py
		- Script for updating the FE model with the ORIENT function for loading orientation information and rotating local coordinate systems, and running the FE simulation.
		- Input: Abaqus CAE file generated in S2_Cube.py and Fortran files generated in S3_mapping.py
		- Output: Field and history output for post processing. CAE and ODB files for post-processing in Abaqus.
	* S5_PostProcessing.py
		- Script for post processing simulation results from Abaqus.
		- Input: Abaqus result files saved as .out files and integration point coordinates (INTCOOR.dat).
		- Output: Result plots.
		
	* M1_TomoHandling.py
		- Python module with functions for handling tomogram data.
	* M2_Alignment.py
		- Python module with functions for orientation calculations and plotting.
	* M3_AbqFunctions.py
		- Python module with Abaqus functions for part/assembly/mesh generation.
	* M4_IntegrationPoints
		- Python module with a function for plotting integration points with field variables .
		
	* I1_CubeIP.in
		- Input file for Abaqus. Used for exporting .dat file with integration point coordinates.
	* I2_orient.f
		- Fortran file with ORIENT function. 
		
- data
	* A01crop.nii
		- Cropped version of A01.nii file.
	* Other datasets are available in [2].

- results
	* Empty by default. 
	* Is used for saving all relevant data from an analysis of a sample including all result figures.
	* All result files will be saved to a folder of the same name as the sample name. 
		- Note that if an analysis is run for the same sample name, then the previous sample result folder is renamed with an appended counter. 

## Guidelines

- The complete analysis is executed by the shell script S0_main.sh
	* Define the sample names used for the analysis and set the crop_samples parameter for the Nifti file.
- Running the individual python scripts without the shell script. 
	* Change the sample_name from 'shell_sample_name" to the name of the sample, and run the python script. 
		- Make sure that the imported python modules and data files are available in the working directory.

## Example of method
A precompiled version of this work is presented in a CodeOcean Notebook. This version is independent of Abaqus<sup>TM</sup>.
Link to CodeOcean: https://codeocean.com/capsule/9342448/tree/v1

## Authors and acknowledgment
Lead and corresponding auther: Ole Villiam Ferguson (olen@dtu.dk) \
Co-auther: Lars Pilgaard Mikkelsen

## References
[1] O. V. Ferguson, L. P. Mikkelsen, "Three-Dimensional Finite Element Modeling of Anisotropic Materials using X-ray Computed Micro-Tomography Data", *Software Impacts*, Unpublished results \
[2] Mikkelsen, Lars P. (2022). Pultruded carbon fiber profiles - 3D x-ray tomography data-sets for two different pultruded profiles [Data set]. Zenodo. https://doi.org/10.5281/zenodo.5978049 \
