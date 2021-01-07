#!/bin/bash

#SBATCH --job-name=locks
#SBATCH --mail-user=zeph@umich.edu
#SBATCH --mail-type=BEGIN,END
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=1000m
#SBATCH --time=300:00
#SBATCH --account=engin1
#SBATCH --partition=standard
#SBATCH --output=/home/%u/%x-%j.log

./process_locks.sh
