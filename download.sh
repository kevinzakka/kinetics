#!/bin/bash

echo "Downloading..."
mkdir data
cd data
wget "https://storage.googleapis.com/deepmind-media/Datasets/kinetics700.tar.gz"

echo "Extracting..."
tar -xvzf kinetics700.tar.gz
rm kinetics700.tar.gz
echo "Done."