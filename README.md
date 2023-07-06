# Project Merger
Project Merger is a Python script that allows users to merge multiple programming block files (.v5blocks or .iqblocks) into one. It provides a simple and convenient way to combine block files from different projects.

## File Structure
To use the script, ensure that you have the following folder structure:

- Project Folder
  - ProjectMerger.py
  - Modules
    - BlockFile1.v5blocks
    - BlockFile2.v5blocks
    ...
  - Merge
    - MergedProject.v5blocks
    
The script expects two main folders: ```Modules``` and ```Merge```. The ```Modules``` folder should contain the block files you want to merge, while the ```Merge``` folder will be used to store the merged project file.

Please note that the folder names ```Modules``` and ```Merge``` are crucial for the script to work correctly. If you choose different folder names, you will need to update the script accordingly.

## Usage
Ensure you have Python installed on your system.

Download the ProjectMerger.py script and place it in your project folder.

Double-click the ProjectMerger.py script file in your project folder. The script will be executed, and a command prompt or terminal window will appear, displaying details of how the project files were merged.

The script will merge the block files from the Modules folder and add any blocks from them into the main blocks file in the Merge folder). Additionally, feel free to put code into the main merge file; any blocks created in that file will be preserved during the merge process. 

Note: The script expects the block files to be pre-made and available in the Modules folder. It will not create any new block files, only read and/or modify existing ones.

## Limitations

The script only works with block files in the .v5blocks or .iqblocks format.

This script only merges \<block\> elements from the files. This means that if you have any variables from one file, it will only copy over if it is used in the code itself. If the variable exists but isn't used, it won't transfer. Really, I see this as a feature (;

The script doesn't change the location of any blocks during the transfer, so it is very likely that in the merged file there will be blocks stacked on top of eachother.

## Dependencies

Any dependencies are included in a standard Python installation.

## License

This script is provided under the terms of the MIT License.
