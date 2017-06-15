#!/usr/local/bin/python3
from __future__ import division

header = r"""
    _ _____            _   
   /_\_   _| _ __ _ __| |__
  / _ \| || '_/ _\` / _| / /
 /_/ \_\_||_| \__,_\__|_\_\\

https://github.com/avertly/atrack
"""

print(header)
import subprocess
import time
import requests
import os

network_device = "en0"
tracked_storage_device = '/dev/sda1'
influxdb_ip = 'http://52.233.135.76:8086'
influxdb_username = 'ave'
influxdb_password = 'Cmup7XU4696mWYwT'
influxdb_database = 'avertlystatus'
influxdb_report_name = command(
    "hostname")  # Switch this to a set string if you want, but this ensures that you don't pollute the data.


# Start of configuration part

def command(cmd):
    return subprocess.run(cmd.split(' '), stdout=subprocess.PIPE).stdout.decode('utf-8').strip()


import re
import sys

# Get process info
ps = subprocess.Popen(['ps', '-caxm', '-orss,comm'], stdout=subprocess.PIPE).communicate()[0].decode()
vm = subprocess.Popen(['vm_stat'], stdout=subprocess.PIPE).communicate()[0].decode()

# Iterate processes
processLines = ps.split('\n')
sep = re.compile('[\s]+')
rssTotal = 0  # kB
for row in range(1, len(processLines)):
    rowText = processLines[row].strip()
    rowElements = sep.split(rowText)
    try:
        rss = float(rowElements[0]) * 1024
    except:
        rss = 0  # ignore...
    rssTotal += rss

# Process vm_stat
vmLines = vm.split('\n')
sep = re.compile(':[\s]+')
vmStats = {}
for row in range(1, len(vmLines)-1):
    rowText = vmLines[row].strip()
    rowElements = sep.split(rowText)
    vmStats[(rowElements[0])] = int(rowElements[1].strip('\.')) * 4096

wired = int(vmStats["Pages wired down"] / 1024)
free = int(vmStats["Pages free"] / 1024)
pagein1 = int(vmStats["Pageins"] / 1024)
pageout1 = int(vmStats["Pageouts"] / 1024)
swapin1 = int(vmStats["Swapins"] / 1024)
swapout1 = int(vmStats["Swapouts"] / 1024)
inactive = int(vmStats["Pages inactive"] / 1024)
compressions = int(vmStats["Compressions"] / 1024)
decompressions = int(vmStats["Decompressions"] / 1024)
total = int(rssTotal / 1024)
used = int(total - free)

result = subprocess.run("top -l 1 -s 0".split(' '), stdout=subprocess.PIPE)

for line in result.stdout.split(b'\n'):
    if line.startswith(b"Networks"):
        network_line = line
    elif line.startswith(b"Disks"):
        disk_line = line

match = re.match(br'^Networks: packets: (\d+)\/\d+M in, (\d+)\/\d+M out\.$', network_line)
inbytes = match.groups(1)[0].decode('utf-8')
outbytes = match.groups(1)[1].decode('utf-8')

match = re.match(br'^Disks: (\d+)\/\d+G read, (\d+)\/\d+G written\.$', disk_line)
read1 = float(match.groups(1)[0].decode('utf-8'))
write1 = float(match.groups(1)[1].decode('utf-8'))

result = subprocess.run("uptime".split(' '), stdout=subprocess.PIPE)

match = re.match(br'^.+, load averages: ([\d\.]+) [\d\.]+ [\d\.]+', result.stdout)
load = float(match.groups(0)[0].decode('utf-8'))

result = subprocess.run("sysctl vm.swapusage".split(' '), stdout=subprocess.PIPE)
match = re.match(br'vm\.swapusage:\stotal\s=\s([\d.]+)M\s+used\s=\s([\d.]+)M\s+free\s=\s([\d.]+)M.+', result.stdout)
swap_total = float(match.groups(1)[0].decode('utf-8'))
swap = float(match.groups(1)[1].decode('utf-8'))


br1 = float(inbytes)
bt1 = float(outbytes)

comp1 = float(compressions)
decomp1 = float(decompressions)

# Continued at the ending of the script.

# Storage space

# used_space=$(df | grep $tracked_storage_device | grep -o '[0-9]\{1,2\}%')

# printf '%s\n' "Storage Use: ${used_space}"

# Memory

total_ram_bytes = total
used_ram_bytes = used
ram_percentage = (used / total) * 100
print("Memory Use: {} out of {} bytes ({:.2f}%)".format(used_ram_bytes, total_ram_bytes, float(ram_percentage)))
print("Wired Memory: {} bytes ({:.2f}%)".format(wired, (wired / total) * 100))

total_swap_bytes = swap_total
used_swap_bytes = swap
swap_percentage = (swap / swap_total) * 100

print("Swap Use: {} out of {} bytes ({:.2f}%)".format(used_swap_bytes, total_swap_bytes, float(swap_percentage)))

# CPU
# sysstat is needed for this!

# cpu_used=$(mpstat 2 1 | grep Average | awk '{print $3}')
# printf '%s\n' "CPU Use: ${cpu_used}%"

cpu_load_average = load

print("CPU Load: {}".format(cpu_load_average))

# Back to Network stuff

sleep_time = 10
print("Sleeping for {} seconds".format(sleep_time))
time.sleep(sleep_time)
# Sleeping so we can get a minute worth of data to calculate average Network use, and so that we can only report back every minute

# Get process info
ps = subprocess.Popen(['ps', '-caxm', '-orss,comm'], stdout=subprocess.PIPE).communicate()[0].decode()
vm = subprocess.Popen(['vm_stat'], stdout=subprocess.PIPE).communicate()[0].decode()

# Iterate processes
processLines = ps.split('\n')
sep = re.compile('[\s]+')
rssTotal = 0  # kB
for row in range(1, len(processLines) - 1):
    rowText = processLines[row].strip()
    rowElements = sep.split(rowText)
    try:
        rss = float(rowElements[0]) * 1024
    except:
        rss = 0  # ignore...
    if row != len(processLines) - 1:
        rssTotal += rss

# Process vm_stat

vmLines = vm.split('\n')
sep = re.compile(':[\s]+')
vmStats = {}
for row in range(1, len(vmLines) - 1):
    rowText = vmLines[row].strip()
    rowElements = sep.split(rowText)
    vmStats[(rowElements[0])] = int(rowElements[1].strip('\.')) * 4096

compressions = int(vmStats["Compressions"] / 1024)
decompressions = int(vmStats["Decompressions"] / 1024)
pagein2 = int(vmStats["Pageins"] / 1024)
pageout2 = int(vmStats["Pageouts"] / 1024)
swapin2 = int(vmStats["Swapins"] / 1024)
swapout2 = int(vmStats["Swapouts"] / 1024)

result = subprocess.run("top -l 1 -s 0".split(' '), stdout=subprocess.PIPE)

for line in result.stdout.split(b'\n'):
    if line.startswith(b"Networks"):
        network_line = line
    elif line.startswith(b"Disks"):
        disk_line = line
match = re.match(br'^Networks: packets: (\d+)\/\d+M in, (\d+)\/\d+M out\.$', network_line)
inbytes = match.groups(1)[0].decode('utf-8')
outbytes = match.groups(1)[1].decode('utf-8')

match = re.match(br'^Disks: (\d+)\/\d+G read, (\d+)\/\d+G written\.$', disk_line)
read2 = float(match.groups(1)[0].decode('utf-8'))
write2 = float(match.groups(1)[1].decode('utf-8'))

result = subprocess.run("sysctl vm.swapusage".split(' '), stdout=subprocess.PIPE)
match = re.match(br'vm\.swapusage:\stotal\s=\s([\d.]+)M\s+used\s=\s([\d.]+)M\s+free\s=\s([\d.]+)M.+', result.stdout)
swap_total = float(match.groups(1)[0].decode('utf-8'))
swap = float(match.groups(1)[1].decode('utf-8'))

br2 = float(inbytes)
bt2 = float(outbytes)

comp2 = float(compressions)
decomp2 = float(decompressions)

u_speed = ((bt2 - bt1) / sleep_time) / 1024
d_speed = ((br2 - br1) / sleep_time) / 1024

comp_speed = (comp2 - comp1) / sleep_time
decomp_speed = (decomp2 - decomp1) / sleep_time

read_speed = (read2 - read1) / sleep_time
write_speed = (write2 - write1) / sleep_time

pagein_speed = (pagein2 - pagein1) / sleep_time
pageout_speed = (pageout2 - pageout1) / sleep_time

swapin_speed = (swapin2 - swapin1) / sleep_time
swapout_speed = (swapout2 - swapout1) / sleep_time

print("Download: {}KB/s, Upload: {}KB/s".format(d_speed, u_speed))
print("Comp: {}/s, Decomp: {}/s".format(comp_speed, decomp_speed))
print("Reads: {}/s, Writes: {}/s".format(read_speed, write_speed))
print("Pageins: {}/s, Pageouts: {}/s".format(pagein_speed, pageout_speed))
print("Swapins: {}/s, Swapouts: {}/s".format(swapin_speed, swapout_speed))


# Send to InfluxDB:

# curl -i -XPOST "$influxdb_ip/write?u=$influxdb_username&p=$influxdb_password&db=$influxdb_database" --data-binary "$influxdb_report_name storage_usage=${used_space//%},cpu_load=${cpu_load_average//,},cpu_percentage=$cpu_used,ram_percentage=$ram_percentage,swap_percentage=$swap_percentage,download=$d_speed,upload=$u_speed"

cmd = ['curl', '-i', '-XPOST',
       '"{}/write?u={}&p={}&db={}"'.format(influxdb_ip, influxdb_username, influxdb_password, influxdb_database),
       '--data-binary',
       '"{}'.format(influxdb_report_name),
       'ram_percentage={},cpu_load={},download={},upload={},comp_speed={},decomp_speed={},swap_percentage={},disk_read={},disk_write={}",swapins={},swapouts={},pageins={},pageouts={},wired={}'.format(
           ram_percentage,
           cpu_load_average, d_speed, u_speed, comp_speed, decomp_speed, swap_percentage, read_speed, write_speed,
       swapin_speed, swapout_speed, pagein_speed, pageout_speed, wired / total_ram_bytes)
       ]

os.system(' '.join(cmd))
