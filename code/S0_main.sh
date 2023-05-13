#!/bin/bash

#Remember, no spaces between variable names and variables i.e., X = 1 will cause an error. 

## Assign shell script control constants. Strings of "yes" and "no" are accepted.
## If "yes" then the step is skipped.
Env_installed="no"

## Define data names for analysis
# declare -a sample_names=("A01" "A01crop" "A02" "A02S")
declare -a sample_names=("A01crop")

# Declare cropping parameters for all datasets in samples_names
# crop_samples=(200 0 200 200)
crop_samples=(0)

## First time runnig the script we need to install a Python environment
if [ "$Env_installed" = "no" ]; then
	source /usr/local/apps/anaconda3/bin/activate
	conda create -n STenv
	conda activate  STenv
	conda install pip
	~/.conda/envs/STenv/bin/pip install numpy matplotlib nibabel structure-tensor jupyter pandas
	echo "<> Python environment installed"
elif [ "$Env_installed" = "yes" ]; then
	echo "<> Python environment already installed"
else
	echo "<> Env_installed should be either yes or no"
fi

## Assign directory for Python environment and active it.
source /usr/local/apps/anaconda3/bin/activate
conda activate  STenv

## Iterate over the data files defined in sample_name
i=0
for sample_name in ${sample_names[@]}; do
	echo index $i
	crop=${crop_samples[i]}
	##### Make results folder
	result_dir=../results
	sample_dir="$result_dir/${sample_name}_files"
	if [ -d "$sample_dir" ]; then
		counter=$(find "${result_dir}/" -name "${sample_name}_files*" -type d | wc -l) 
		mv $sample_dir "${sample_dir}_${counter}"
		mkdir $sample_dir
		mkdir "${sample_dir}/figures"
	else
		echo "No folder available. Result folder is created"
		mkdir $sample_dir
		mkdir "${sample_dir}/figures"
	fi

	##### Analyse the CT images and define model dimensions
	sed -e "s/shell_sample_name/$sample_name/;s/shell_crop/$crop/" S1_STanalysis.py > "${sample_name}_S1_STanalysis.py"
	python3 "${sample_name}_S1_STanalysis.py"
	echo "<> CT image has been analysed and model dimensions are exported"
	
	##### Generate FE-model and export integration points
	module load abaqus/2022a
	sed -e "s/IP1/$sample_name\_IP1/" I1_CubeIP.in > "${sample_name}_IP2.inp"
	sed -e "s/shell_sample_name/$sample_name/" S2_Cube.py > "${sample_name}_S2_Cube.py"
	unset SLURM_GTIDS
	abq2022 cae noGUI="${sample_name}_S2_Cube.py"
	wait
	echo "FE-model has been generated and integration points are exported"
	
	##### Map fiber orientations to integration points
	sed -e "s/shell_sample_name/$sample_name/" S3_mapping.py > "${sample_name}_S3_mapping.py"
	python3 "${sample_name}_S3_mapping.py"
	echo "<> Fiber orientations has been mapped to the integration points"
	
	##### Run simulation in Abaqus with orientation information mapped to integration points
	sed "s/InputOrientFortran1/$sample_name\_PHI/;s/InputOrientFortran2/$sample_name\_THETA/" I2_orient.f > "${sample_name}_orient.f"
	sed "s/InputModelCase/$sample_name/" S4_Cube_modified.py > "${sample_name}_S4_Cube_modified.py"
	abq2022 cae noGUI="${sample_name}_S4_Cube_modified.py"
	
	##### Postprocessing
	mv "${sample_name}_IP2.dat" "Out-${sample_name}_INTCOOR.dat"
	sed -e "s/shell_sample_name/$sample_name/" S5_PostProcessing.py > "${sample_name}_S5_PostProcessing.py"
	python3 "${sample_name}_S5_PostProcessing.py"
	echo "<> Postprocessing of Abaqus data complete."
	
	##### Move files to sample result folder
	rm *.log *.com *.prt *.jnl 
	*IP2* *.inp
	mv "${sample_name}"* "Out-${sample_name}"* ../results/"${sample_name}_files"/
	i=$(( i + 1 ))
	echo index $i
done

echo "<> Script complete"
