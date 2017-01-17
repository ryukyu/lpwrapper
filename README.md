# lpwrapper #

Lpwrapper is a cli tool that wraps the lpass cli tool for quick password searches.

# INSTALL #

apt-get -y install lastpass-cli xsel

git clone git@github.com:ryukyu/lpwrapper.git

# USAGE #
$PATH/lpwrapper/lpwrapper

Optionally bind lpwrapper with a terminal profile to get "quick search" functionality.

terminator -x $PATH/lpwrapper/lpwrapper

# NOTES #
Requires the lastpass-cli which does all the heavy lifting. This is just a simple python script to make searches easier. Also requires xsel to copy password to the clipboard.
