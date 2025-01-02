# jeksim

pkg update && pkg upgrade
termux-setup-storage
pkg install python
pkg install python pip -y
pip install requests
pkg install git
cd storage && git clone https://github.com/apengjers/jeksim
cd jeksim && python jeksim.py
