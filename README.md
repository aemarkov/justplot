# justplot - simple data plotter with GUI

Just plot data from CSV and some other files with almost single
button quickly and easy without complicated GUI and lot of actions

![](img/justplot.png)

## Usage

```
usage: justplot [-h] [files [files ...]]

Simple graph plotter. Run without arguments to add files from GUI.

positional arguments:
  files       Files to plot

optional arguments:
  -h, --help  show this help message and exit

```

You can run `justplot` from command line and provide list of files to plot or
choose files via GUI.

### Hotkeys in GUI
| Function       | Hotkey |
|----------------|--------|
| Open file      | CTR+O  |
| Delete plot    | Del    |


## Features
Current status:
 - [X] Just plot the graphs from multiple files
 - [X] Display loaded files and data series in the tree view
 - [x] Hide, show and delete data series and files
 - [x] Command line interface
 - [x] Save the last directory in the Open File dialog (I thought that OS/Qt should do this automatically)
 - [*] Graph export as image (It can be done by pyqtgraph itself by right-clicking graph pane)
 - [x] Hotkeys
 - [x] Multiple files selection in open dialog
 - [ ] Mathematical operations on data
 - [ ] Graph visual settings (?)
 - [ ] Multiple graph panes (?)

Supported file types:
 - [x] CSV with any whitespace separator
 - [ ] Choose separator

## Installation

```sh
pip install justplot-qt
```

### Install from sources
Note: this command will install package in Development Mode, i.e. it will reference local source

```sh
git clone https://github.com/Garrus007/justplot.git
pip3 install -e justplot
```

### Troubleshooting

Make sure all python dependencies are installed
```sh
# Ubuntu distro example
sudo apt install python3 python3-pip python3-setuptools
```

If PyQt5 failed to install try to install from repo
```sh
sudo apt install python3-pyqt5
```
