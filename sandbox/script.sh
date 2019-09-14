echo "Installing Started ..."
sudo apt-get install python-dev
tar -xzf libsandbox-0.3.5.tar.gz
tar -xzf pysandbox-0.3.5.tar.gz
cd libsandbox-0.3.5
./configure --prefix=/usr --libdir=/usr/lib
sudo make install
cd ..
cd pysandbox-0.3.5
python setup.py build
sudo python setup.py install
cd ..
rm -rf pysandbox-0.3.5
rm -rf libsandbox-0.3.5
sudo apt-get -y install python3-pip && pip3 install django
echo "Installation Complete ..."
