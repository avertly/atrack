#!/usr/bin/env bash
echo """
    _ _____            _   
   /_\_   _| _ __ _ __| |__
  / _ \| || '_/ _\` / _| / /
 /_/ \_\_||_| \__,_\__|_\_\\

https://github.com/avertly/atrack
"""

# Start of configuration part

network_device="eth0"
tracked_storage_device='/dev/sda1'
influxdb_ip='http://something:8086'
influxdb_username='username'
influxdb_password='password'
influxdb_database='database'
influxdb_report_name='report'

# End of configuration part

# Based on https://github.com/prurigro/darkcloud-tmuxconfig/blob/master/bwrate -- MIT licensed:

[[ ! -d "/sys/class/net/$network_device" ]] && {
    printf '%s\n' "No such device: $network_device"
    exit 1
}

br1=$(</sys/class/net/"$network_device"/statistics/rx_bytes)
bt1=$(</sys/class/net/"$network_device"/statistics/tx_bytes)

# Continued at the ending of the script.

# Storage space

used_space=$(df | grep $tracked_storage_device | grep -o '[0-9]\{1,2\}%')

printf '%s\n' "Storage Use: ${used_space}"

# Memory

total_ram_bytes=$(free | grep Mem | awk '{print $2}')
used_ram_bytes=$(free | grep Mem | awk '{print $3}')
printf '%s\n' "Memory Use: ${used_ram_bytes} out of ${total_ram_bytes} bytes."

total_swap_bytes=$(free | grep Swap | awk '{print $2}')
used_swap_bytes=$(free | grep Swap | awk '{print $3}')
printf '%s\n' "Swap Use: ${used_swap_bytes} out of ${total_swap_bytes} bytes."

ram_percentage=$((100*$used_ram_bytes/$total_ram_bytes))
swap_percentage=$((100*$used_swap_bytes/$total_swap_bytes))

if [ "$used_ram_bytes" -eq 0 ]; then
   ram_percentage=0
fi

if [ "$used_swap_bytes" -eq 0 ]; then
   swap_percentage=0
fi

printf '%s\n' "RAM: ${ram_percentage}%, Swap: ${swap_percentage}%."

# CPU
# sysstat is needed for this!

cpu_used=$(mpstat 2 1 | grep Average | awk '{print $3}')
printf '%s\n' "CPU Use: ${cpu_used}%"

cpu_load_average=$(uptime  | grep -oP '(?<=average:).*' | awk '{print $1}')

# Uptime

system_uptime=$(uptime | awk '{print $1}')
printf '%s\n' "Uptime: ${system_uptime}"

sleep_time=$((60 - $(date +%S) ))
printf '%s\n' "Sleeping for ${sleep_time} seconds"
sleep $sleep_time &&


br2=$(cat /sys/class/net/"$network_device"/statistics/rx_bytes)
bt2=$(cat /sys/class/net/"$network_device"/statistics/tx_bytes)

u_speed=$(( ( ( bt2 - bt1 ) / sleep_time ) / 1024 ))
d_speed=$(( ( ( br2 - br1 ) / sleep_time ) / 1024 ))

printf '%s\n' "Average Network Speeds: Download: ${d_speed}KB/s, Upload: ${u_speed}KB/s"

curl -i -XPOST "$influxdb_ip/write?u=$influxdb_username&p=$influxdb_password&db=$influxdb_database" --data-binary "$influxdb_report_name storage_usage=${used_space//%},cpu_load=${cpu_load_average//,},cpu_percentage=$cpu_used,ram_percentage=$ram_percentage,swap_percentage=$swap_percentage,download=$d_speed,upload=$u_speed"