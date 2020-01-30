#!/bin/bash

wget -P data "https://storage.googleapis.com/deepmind-media/Datasets/kinetics700.tar.gz"
cd data
tar -xvzf kinetics700.tar.gz
rm kinetics700.tar.gz
