#!/usr/bin/env python

import argparse
import os
import shutil
from datetime import datetime

"""
**MO2_Exporter made by Shiroe Kuroha**

Feel free to modify, distribute, and improve this script.  
Please give credit to the author.
"""

def setup_argparse():
    parser = argparse.ArgumentParser(description="""MO2_Exporter make a merged Data folder for Skyrim SE from Mod Organizer 2 instance.""")

    parser.add_argument("-i", "--instance",     help="MO2 instance folder path",                 type=str, required=True)
    parser.add_argument("-o", "--output",       help="Output Data & Plugins.txt folder path",    type=str, required=True)
    parser.add_argument("-p", "--profile",      help="Profile of the instance, \"Default\" if not specify", type=str)

    return parser.parse_args()

def copy_folder(src_dir, dst_dir):
    if not os.path.exists(src_dir):
        return

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dst_item = os.path.join(dst_dir, item)

        ignore_default_list = ["docs", "documentation", "readme", "readmes", "tools", "fomod", "meta.ini"]

        if item.lower() in ignore_default_list:
            continue

        if os.path.isdir(src_item):
            copy_folder(src_item, os.path.join(dst_dir, item.lower()))
        else:
            shutil.copy2(src_item, dst_item)

def read_lines_from_file(file_path: str):
    if file_path == None:
        return []

    file_fs = open(file_path, "r")
    file_lines = file_fs.readlines()

    for i in range(0, len(file_lines)):
        file_lines[i] = (file_lines[i][:-1] if file_lines[i][-1] == "\n" else file_lines[i])
    
    return file_lines

def main() -> int:
    args = setup_argparse()
    profile_name = args.profile if args.profile != None else "Default"
    logfile = open("MO2_Exporter_Log.txt", "w", encoding='utf-8')

    def log_write(msg):
        current_time = datetime.now().time()
        full_msg = f"[{str(current_time):^17}]: " + msg

        print(full_msg)
        logfile.write(full_msg + "\n")

    log_write("Verifying instance & Output Path...")

    for dep in ["mods", "overwrite", "profiles"]:
        if not os.path.exists(os.path.join(args.instance, dep)):
            log_write("ERROR // ERROR: \t" + f"{dep:>12}" + " is Missing!")
            return -1
    
    log_write("Verifying modlist.txt and plugins.txt...")
    rel_path_modlist = os.path.join("profiles", profile_name, "modlist.txt")
    abs_path_modlist = os.path.join(args.instance, rel_path_modlist)

    if os.path.exists(abs_path_modlist):
        log_write(f"\t{abs_path_modlist} is good")

    else:
        log_write("ERROR // ERROR: \tMissing modlist.txt")
        return -2

    rel_path_plugins = os.path.join("profiles", profile_name, "plugins.txt")
    abs_path_plugins = os.path.join(args.instance, rel_path_plugins)

    if os.path.exists(abs_path_plugins):
        log_write(f"ERROR // ERROR: \t{abs_path_plugins} is good")

    else:
        log_write("ERROR // ERROR: \tMissing plugins.txt")
        return -3

    modlist_fs = open(abs_path_modlist, "r")
    modlist_lines = read_lines_from_file(abs_path_modlist)
    modlist_final = []

    for index in range(0, len(modlist_lines)):
        if "_separator" in modlist_lines[index] or modlist_lines[index][0] == "#":
            log_write(f"\t\"{modlist_lines[index][1:]}\" is seperator or comment, ignoring...")
        
        elif modlist_lines[index][0] == "*":
            log_write(f"\t\"{modlist_lines[index][1:]}\" is Creation Club mod, ignoring...")

        else:
            if modlist_lines[index][0] == "-":
                log_write(f"\t\"{modlist_lines[index][1:]}\" is mod, but disabled, ignoring...")

            else:
                log_write(f"\t\"{modlist_lines[index][1:]}\" is mod, appending...")
                modlist_final.append(modlist_lines[index][1:])

    modlist_final = modlist_final[::-1]
            
    final_package_path = args.output
    final_package_data_path = os.path.join(final_package_path, "Data")

    if not os.path.exists(final_package_path):
        os.makedirs(final_package_path)

    if not os.path.exists(final_package_data_path):
            os.makedirs(final_package_data_path)

    log_write("Preparing Final Package:")
    start_time = datetime.now()
    end_time = datetime.now()

    for mod in modlist_final:
        mod_path = os.path.join(args.instance, "mods", mod)

        if os.path.exists(mod_path):
            log_write(f"Copying {mod}...")
            copy_folder(mod_path, final_package_data_path)
                
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
    log_write("If you forget to create a separate mod for tools output like(FNIS, Nemesis, Bodyslide), you might want to copy overwrite folder contents to Data folder too!")
    log_write("Thank you for using MO2 Exporter!")

    return 0

if __name__ == "__main__":
    match(main()):
        case 0:
            print("Success! Everything is OK!")

        case _:
            print("Failed, please check log file.")