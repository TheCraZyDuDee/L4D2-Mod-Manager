# L4D2-Mod-Manager

Manager to enable Mods in Addon disabled Modes (Versus)

![](https://i.imgur.com/x5tZwkf.png)


## Features

- Enable/Disable Mods for use in Mod disabled Gamemodes
- Change Priority of enabled mods in which they get loaded
- Rename/Delete Mods in the list
- Manually add .vpk Mods
- Add installed Workshop Mods

## Usage

- Download the latest Release of the Tool from [here](https://github.com/TheCraZyDuDee/L4D2-Mod-Manager/releases/latest/download/L4D2-Mod-Manager.exe)
- Move the Tool to your Left 4 Dead 2 Game Folder (the same directory where the left4dead2.exe is located)
- Now Manage your mods to your liking and apply changes (mods managed by the tool get moved to a folder called usermods)

## Building

Currently Windows only!

- Download the Repository via git or just as zip
- Install [Python](https://www.python.org/downloads/) and add it to System Path'
- Install PyInstaller using `pip install pyinstaller`
- cd to the directory containing the .png, .py and .spec file and run `pyinstaller l4d2-manager.spec` or just run the build.bat
