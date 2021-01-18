#! /bin/sh

echo "=================================================="
echo "      pike.esi.uclm.es ----> sources.list"
echo "=================================================="
sudo wget -P /etc/apt/trusted.gpg.d https://uclm-arco.github.io/debian/uclm-arco.asc
echo "deb https://uclm-arco.github.io/debian/ sid main" | sudo tee /etc/apt/sources.list.d/arco.list
sudo apt update

echo "=================================================="
echo "            Installing Python3"
echo "=================================================="
sudo apt install -y python3

echo "=================================================="
echo "         Installing Python3 Commodity"
echo "=================================================="
sudo apt install python3-commodity

echo "=================================================="
echo "             Installing ZeroC Ice"
echo "=================================================="
sudo apt install python-zeroc-ice36 zeroc-ice36

echo "=================================================="
echo "            Installing Scone-Wrapper"
echo "=================================================="
sudo apt install scone-wrapper

echo "=================================================="
echo "                Installing PIP"
echo "=================================================="
sudo apt install python3-pip

echo "=================================================="
echo "        Installing networkx Python lib"
echo "=================================================="
sudo pip3 install networkx

echo "=================================================="
echo "                Installing numpy"
echo "=================================================="
sudo pip3 install numpy

echo "=================================================="
echo "          Installing scipy Python lib"
echo "=================================================="
sudo pip3 install scipy

echo "=================================================="
echo "        Installing matplotlib Python lib"
echo "=================================================="
sudo pip3 install matplotlib

echo "=================================================="
echo "            Installing lxml Python lib"
echo "=================================================="
sudo pip3 install lxml

echo "=================================================="
echo "          Installing shapely Python lib"
echo "=================================================="
sudo pip3 install shapely

echo "=================================================="
echo "            Installing nose Python lib"
echo "=================================================="
sudo pip3 install nose

echo "=================================================="
echo "           Installing tkinter python lib"
echo "=================================================="
sudo apt install python3-tk