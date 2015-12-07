#!/bin/python3

# ip link set <interface> up
# wpa_supplicant -B -D nl80211 -c <filename> -i <interface name>
# dhcpcd -A <interface>

import argparse
import sys
import subprocess
import os
import pystache

if os.path.isfile("./defaults.py"):
    # Local file, exports:
    #     'interface' = default WLAN interface
    #     'data_dir' = default directory for script and connect data files
    #     'script_dir' = default directory for script and connect data files
    import defaults

pystache_renderer = pystache.Renderer()
argparser = argparse.ArgumentParser(description = "Creates a new connect script")

argparser.add_argument(
    "-s", "--ssid",
    dest = "ssid",
    default = "",
    required = True,
    type = str,
    help = "SSID for the network to connect to.")

argparser.add_argument(
    "-p", "--passphrase",
    dest = "passphrase",
    default = "",
    required = False,
    type = str,
    help = "Passphrase, if any, for the network.")

argparser.add_argument(
    "-o", "--outfile",
    dest = "outfile",
    default = sys.stdout,
    required = False,
    type = str,
    help = "Filename base for connect data and connect script.")

argparser.add_argument(
    "-i", "--interface",
    dest = "interface",
    default = defaults.interface,
    required = False,
    type = str,
    help = "Interface to use for connect script.")

argparser.add_argument(
    "-c", "--connectscript_dir",
    dest = "script_dir",
    default = defaults.script_dir,
    required = False,
    type = str,
    help = "Directory to put script files in.")

argparser.add_argument(
    "-d", "--datafile_dir",
    dest = "data_dir",
    default = defaults.data_dir,
    required = False,
    type = str,
    help = "Directory to put data files in.")

def create_connect_info_file(data_filename, ssid, passphrase):
    if not data_filename.endswith(".conf"):
        data_filename += ".conf"

    with open(data_filename, "w") as o:
        wpa_supplicant_output = subprocess.Popen(
            ["wpa_passphrase", ssid, passphrase],
            stdout=subprocess.PIPE).communicate()[0].decode()
        o.write(pystache_renderer.render_path(
            'templates/data.mustache',
            {'wpa_supplicant_output':wpa_supplicant_output}))

    # Chmod 600 <filename>
    os.chmod(data_filename, 384)

    return data_filename

def create_connect_script(interface, script_filename, data_filename):
    if not data_filename.endswith(".conf"):
        data_filename += ".conf"

    if not script_filename.endswith(".sh"):
        script_filename += ".sh"

    with open(script_filename, "w") as o:
        o.write(pystache_renderer.render_path(
            'templates/script.mustache',
            {'interface':interface, 'data_filename':data_filename}))

    # Chmod 700 <filename>
    os.chmod(script_filename, 448)

    return script_filename

if __name__ == "__main__":
    args = argparser.parse_args()

    if not args.script_dir.endswith("/"):
        script_filepath = args.script_dir + "/" + args.outfile
    else:
        script_filepath = args.script_dir + args.outfile
    if not args.data_dir.endswith("/"):
        data_filepath = args.data_dir + "/"  + args.outfile
    else:
        data_filepath = args.data_dir + args.outfile

    ci_file = create_connect_info_file(data_filepath, args.ssid, args.passphrase)
    cs_file = create_connect_script(args.interface, script_filepath, data_filepath)

    print("Wrote connect data to %s and connect script to %s." % (ci_file, cs_file))
