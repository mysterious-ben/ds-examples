# Python Environment Setup From Zero

Setup a python dev environment on Pop!_OS 20.04. It comes with python 3.8.2.


## Switch bash to fish

```console
sudo apt install fish
chsh -s /usr/bin/fish
```

Tuturial: https://fishshell.com/docs/current/tutorial.html


## Install alternative python

...


## Install pip

```console
sudo apt install python3-pip
```


## Install virtualenv & virtual fish

```console
sudo apt install virtualenv
pip install virtualfish
vf install
```

Tutorial: https://virtualfish.readthedocs.io/en/latest/index.html

**Customize the fish prompt (optional)**

1. Run `funced fish_prompt`
2. Add
```
if set -q VIRTUAL_ENV
    echo -n -s (set_color -b blue white) "(" (basename "$VIRTUAL_ENV") ")" (set_color normal) " "
end
```
3. Run `funcsave fish_prompt`

**Change the venv directory (optional)**

```console
set -Ux VIRTUALFISH_HOME <new directory>
```


## Install PyCharm

1. Download an archive from https://www.jetbrains.com/pycharm/download/#section=linux

2. Check it's there

```console
ls ~/Downloads/
``` 

3. Install

```console
mkdir ~/.local/apps/
tar xvzf ~/Downloads/pycharm-community-2020.1.tar.gz -C ~/.local/apps/
~/.local/apps/pycharm-community-2020.1/bin/pycharm.sh
```

(during installation, check *Create a script for opening files and projects from the command line*)

4. Configure a project interpreter: `../<venv>/bin/python3`

