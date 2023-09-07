#!/bin/bash

# Check if sudo is installed
if command -v sudo &>/dev/null; then
    echo "sudo is already installed."
else
    echo "sudo is not installed. Installing it..."
    apt update
    apt install sudo
    
    echo "sudo has been installed."
fi


sudo apt update
sudo apt install software-properties-common -y

# Install Python versions

sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.7-dev python3.7-distutils -y
sudo apt install python3.9-dev python3.9-distutils -y
sudo apt install python3.10-dev python3.10-distutils -y
sudo apt install python3.11-dev python3.11-distutils -y
sudo apt install libcurl4-openssl-dev libssl-dev -y

# Install virtual environments
sudo pip install virtualenv pipenv
sudo apt install python-is-python3

# Install pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install poetry==1.2.0
