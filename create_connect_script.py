#!/bin/python3

# ip link set <interface> up
# wpa_supplicant -B -D nl80211 -c <filename> -i <interface name>
# dhcpcd -A <interface>

import argparse
import sys
import subprocess
import os

# Local file, exports:
#     'interface' = default WLAN interface
#     'connect_dir' = default directory for script and connect data files
import defaults

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
        dest = "connect_dir",
        default = defaults.connect_dir,
        required = False,
        type = str,
        help = "Directory to put files in.")

def create_connect_info_file(filename, ssid, passphrase):
    if not filename.endswith(".conf"):
        filename += ".conf"

    o = open(filename, "w")
    # echo 'ctrl_interface=DIR=/run/wpa_supplicant' > "$FILENAME"
    # wpa_passphrase "$SSID" "$PASSPHRASE" >> "$FILENAME"
    o.write("ctrl_interface=DIR=/run/wpa_supplicant\n")
    o.write(subprocess.Popen(["wpa_passphrase", ssid, passphrase], stdout=subprocess.PIPE).communicate()[0].decode())
    o.close()

    # Chmod 600 <filename>
    os.chmod(filename, 384)

    return filename

def create_connect_script(interface, filename):
    if not filename.endswith(".sh"):
        filename += ".sh"

    o = open(filename, "w")
    o.write("#!/bin/bash\n")
    o.write("ip link set %s up\n" % interface)
    o.write("wpa_supplicant -B -D nl80211 -c %s -i %s\n" % (filename, interface))
    o.write("dhcpcd -A %s\n" % interface)
    o.close()

    # Chmod 700 <filename>
    os.chmod(filename, 448)

    return filename

if __name__ == "__main__":
    args = argparser.parse_args()

    filepath = args.connect_dir + args.outfile

    ci_file = create_connect_info_file(filepath, args.ssid, args.passphrase)
    cs_file = create_connect_script(args.interface, filepath)

    print("Wrote connect data to %s and connect script to %s." % (ci_file, cs_file))
