#!/bin/bash
# Convert Docker image to Apptainer SIF format
# Usage: ./docker_to_sif.sh <docker_image> [output_name]

DOCKER_IMAGE=${{1:-ubuntu:20.04}}
OUTPUT_NAME=${{2:-example.sif}}

echo "Converting Docker image $DOCKER_IMAGE to $OUTPUT_NAME"
apptainer build "$OUTPUT_NAME" "docker://$DOCKER_IMAGE"

# TODO: Replace with your actual Docker image
# Examples:
# apptainer build example.sif docker://continuumio/miniconda3
# apptainer build example.sif docker://rocker/r-ver:4.1.0
