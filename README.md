# WildLines
Collection of useful scripts for spectral analysis

Python 2.7
Uses calls to os, meaining that many features, for example those using the filesystem, will NOT work on windows. This was developed in Ubuntu, so hopefully the UNIX-ness should make it largely compatible with OS X.

Installation:
1. Clone, download, extract the files.
2. Edit SETUP to have the right path to your bin
3. Run setup! This can be done with the following command:
     $ ./SETUP
   This should create symbolic links to the right files in your bin.
4. Navigate to a folder where you want to run one of the scripts, and run it. This is a list of the new commands:

- read_kurucz
- read_uky
- read_TOSS
- read_VALD
--> These take the outputs from the relevant websites (see comments of each script for details) and converts to .lte format

- quickplot   - Reads a spectrum file, or any file separated into columns, and plots it in a publication-style plot
- reportlines - Reads and summarises a .lte file
- wildlines   - SFIT companion tool
- getMags     - Searches a directory for models, and allows comparision of different aspects of them graphically. Designed to be modified.

- plot_wasp   - Read a WASP .csv file, and plot it
- plot_CRTS   - Read a CRTS .csv file, and plot it
