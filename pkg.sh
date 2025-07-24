#!/bin/bash

cp main.py waaaybar
chmod +x waaaybar
sudo cp ./waaaybar /usr/local/bin/
sudo chmod +x /usr/local/bin/waaaybar
rm ./waaaybar
echo "Installed waaaybar! Have fun :)"
