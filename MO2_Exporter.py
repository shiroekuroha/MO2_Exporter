#!/usr/bin/env python

import argparse
import os
import shutil
from datetime import datetime

"""
**MO2_Exporter made by Shiroe Kuroha**

Feel free to modify, distribute, and improve this script.  
Please give credit to the author.

**Requirements**:
- SteamOS/Linux or Windows (No macOS, because... Apple)
- 6 GB+ of RAM (Or don't, but I don't think you'll survive once the script finishes)
- 60 GB+ of SSD (Or don't, if you're on a budget or have a potato machine and plenty of patience)
- Proton-GE-20+ (Experimental should works, but Glorious Eggroll works best)
- Steam (Linux/SOSD: Flatpak or Native should work, but Flatpak is the better version that doesn't mess with your package manager)
- Steam Tinker Launch 12.12+ (Linux/SOSD: If you're using Linux or SteamOS devices)
- Python 3.10+ (Make sure Python is in your PATH)
- Skyrim Special Edition (Can't test on LE or Oldrim, because I'm not old)
- SKSE and Address Library (If your mods require it, read the mod description)
- ReShade (If you plan to use it)
- Terminal Emulator or CMD
- 2+ Brain cells

**Execution**:
```bash
python MO2_Exporter.py -i [MO2 Instance path] -o [Skyrim SE path] [-n [Ignore list path]]
```

**Execution (Special Edition)**:
```bash
chmod +x MO2_Exporter.py
MO2_Exporter.py -i [MO2 Instance path] -o [Skyrim SE path] [-n [Ignore list path]]
```

**Notes**:
- If you plan on using MO2 on SteamDeck, I encountered a weird audio delay once I added too many mods.
- Do not use CryoUtils if you're on SteamDeck, as it will break compatibility with Steam Tinker Launch!

Thank you for using my script! Enjoy the game :))
"""

def setup_argparse():
    parser = argparse.ArgumentParser(description="""MO2_Exporter make a merged Data folder for Skyrim mods(and Fallout4 <Not Tested Yet>) to skip the use of Mod Organizer. \n
                                     Supposedly increasing platform support for Linux and SteamDeck(or other SteamOS devices)""")

    parser.add_argument("-i", "--inst", help="MO2 instance folder path, there should be \"downloads\", \"mods\", \"overwrite\", \"profiles\" folders", type=str, required=True)
    parser.add_argument("-o", "--output", help="Data folder path, could be directly in your Skyrim install(not recommend but it's your choice)", type=str, required=True)
    parser.add_argument("-n", "--ignore", help="Ignore file path, mod names in this file will always be ignore(not required, but could be useful if you don't want to install tool mods)", type=str)
    
    return parser.parse_args()

def main():
    logfile = open("MO2_Exporter_Log.txt", "w", encoding='utf-8')

    def log_write(msg):
        current_time = datetime.now().time()
        full_msg = f"[{str(current_time):^17}]: " + msg

        print(full_msg)
        try:
            logfile.write(full_msg + "\n")
        
        except:
            log_write("*THIS MSG IS NOT AVAILABLE, and I dont't know why!")

    def verify_inst_structure(inst_path: str):
        folder_structure = ["downloads", "mods", "overwrite", "profiles"]

        for dep in folder_structure:
            if not os.path.exists(os.path.join(inst_path, dep)):
                log_write("\t" + f"{dep:>12}" + " is Missing!")
                return False
            
            else:
                log_write("\t" + f"{dep:>12}" + " is Good!")

        return True

    def copy_folder(src_dir, dst_dir, ignore):
        if not os.path.exists(src_dir):
            return

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        for item in os.listdir(src_dir):
            log_write("Copying: " + os.path.join(src_dir, item))
            src_item = os.path.join(src_dir, item)
            dst_item = os.path.join(dst_dir, item)

            if item in ignore:
                continue

            if os.path.isdir(src_item):
                copy_folder(src_item, dst_item, ignore)
            else:
                shutil.copy2(src_item, dst_item)

    args = setup_argparse()

    log_write("\nVerifying inst & Output Path...")
    if os.path.exists(args.inst) and os.path.exists(args.output):
        log_write("\t" + f"{"inst Path: ":>18}" + args.inst)
        log_write("\t" + f"{"Output Path: ":>18}" + args.output)

        log_write("\nVerifying inst Structure...")
        if verify_inst_structure(args.inst):

            log_write("\nVerifying modlist.txt and plugins.txt...")
            rel_path_modlist = os.path.join("profiles", "Default", "modlist.txt")
            abs_path_modlist = os.path.join(args.inst, rel_path_modlist)
            if os.path.exists(abs_path_modlist):
                log_write(f"\t{abs_path_modlist} is good")

            else:
                log_write("\tMissing modlist.txt")

            rel_path_plugins = os.path.join("profiles", "Default", "plugins.txt")
            abs_path_plugins = os.path.join(args.inst, rel_path_plugins)

            if os.path.exists(abs_path_plugins):
                log_write(f"\t{abs_path_plugins} is good")

            else:
                log_write("\tMissing plugins.txt")
                return -1
            
            modlist_fs = open(abs_path_modlist, "r")
            modlist_lines = modlist_fs.readlines()
            modlist_complete = []

            modlist_ignore_fs = None
            modlist_ignore = []
            if args.ignore != None:
                modlist_ignore_fs = open(args.ignore, "r")
                log_write("Mod List Ignore detected!")
                modlist_ignore = modlist_ignore_fs.readlines()

                for i in range(0, len(modlist_ignore)):
                    modlist_ignore[i] = modlist_ignore[i][:-1] if modlist_ignore[i][-1] == "\n" else modlist_ignore[i]
                    log_write("Mod List Ignore: " + modlist_ignore[i])

            log_write("Mod List:")

            for index in range(0, len(modlist_lines)):
                if modlist_lines[index][-1] == "\n":
                    modlist_lines[index] = modlist_lines[index][:-1]
                
                else:
                    modlist_lines[index] = modlist_lines[index]

                if "_separator" in modlist_lines[index] or modlist_lines[index][0] == "#":
                    log_write(f"\t\"{modlist_lines[index][1:]}\" is seperator or comment, ignoring...")
                
                elif modlist_lines[index][0] == "*":
                    log_write(f"\t\"{modlist_lines[index][1:]}\" is Creation Club mod, ignoring...")

                else:
                    if modlist_lines[index][0] == "-":
                        log_write(f"\t\"{modlist_lines[index][1:]}\" is mod, but disabled, ignoring...")

                    else:
                        if modlist_lines[index][1:] in modlist_ignore:
                            log_write(f"\t\"{modlist_lines[index][1:]}\" is mod, but in ignore list, ignoring...")
                        
                        else:
                            log_write(f"\t\"{modlist_lines[index][1:]}\" is mod, appending...")
                            modlist_complete.append(modlist_lines[index][1:])

            modlist_complete = modlist_complete[::-1]
            
            final_package_path = args.output
            final_package_data_path = os.path.join(final_package_path, "Data")

            if not os.path.exists(final_package_path):
                os.makedirs(final_package_path)
            
            if not os.path.exists(final_package_data_path):
                os.makedirs(final_package_data_path)

            log_write("Preparing Final Package:")
            start_time = datetime.now()
            end_time = datetime.now()

            for mod in modlist_complete:
                mod_path = os.path.join(args.inst, "mods", mod)

                if os.path.exists(mod_path):
                    log_write(f"Copying {mod}...")
                    copy_folder(mod_path, final_package_data_path, ["meta.ini"])
                
                else:
                    log_write(f"ERROR // ERROR: Mod Folder does not exist or corrupted")
                    return - 1
            
            log_write("Copying plugins.txt to Final Package...")
            shutil.copy2(abs_path_plugins, os.path.join(final_package_path, "Plugins.txt"))

            end_time = datetime.now()
            log_write(f"Start Time: {start_time.time()}")
            log_write(f"End Time: {end_time.time()}")
            log_write(f"Copy Execution Time: {(end_time - start_time).total_seconds()} s")

            log_write("Done! Please make a backup of Skyrim Data folder, overwrite Skyrim Data folder and Plugins.txt file in %APPDATA%\\..\\Local\\Skyrim Special Edition")
            log_write("Thank you for using MO2 Exporter!")

    else:
        log_write("Bad inst or Output Path, please fix!")
    
    return 0

if __name__ == "__main__":
    main()