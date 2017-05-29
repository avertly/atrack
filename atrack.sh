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
influxdb_report_name=$(hostname) # Switch this to a set string if you want, but this ensures that you don't pollute the data.

# End of configuration part

# Network track -- Based on https://github.com/prurigro/darkcloud-tmuxconfig/blob/master/bwrate -- MIT licensed:

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
ram_percentage=$((100*$used_ram_bytes/$total_ram_bytes))
if [ "$used_ram_bytes" -eq 0 ]; then # Check if it is set or not
   ram_percentage=0
fi
printf '%s\n' "Memory Use: ${used_ram_bytes} out of ${total_ram_bytes} bytes (${ram_percentage}%)."

total_swap_bytes=$(free | grep Swap | awk '{print $2}')
used_swap_bytes=$(free | grep Swap | awk '{print $3}')
swap_percentage=$((100*$used_swap_bytes/$total_swap_bytes))
if [ "$used_swap_bytes" -eq 0 ]; then # Check if it is set or not
   swap_percentage=0
fi
printf '%s\n' "Swap Use: ${used_swap_bytes} out of ${total_swap_bytes} bytes (${swap_percentage}%)."

# CPU
# sysstat is needed for this!

cpu_used=$(mpstat 2 1 | grep Average | awk '{print $3}')
printf '%s\n' "CPU Use: ${cpu_used}%"

cpu_load_average=$(uptime  | grep -oP '(?<=average:).*' | awk '{print $1}')

# Back to Network stuff

sleep_time=$((60 - $(date +%S) ))
printf '%s\n' "Sleeping for ${sleep_time} seconds"
sleep $sleep_time &&

# Sleeping so we can get a minute worth of data to calculate average Network use, and so that we can only report back every minute

br2=$(cat /sys/class/net/"$network_device"/statistics/rx_bytes)
bt2=$(cat /sys/class/net/"$network_device"/statistics/tx_bytes)

u_speed=$(( ( ( bt2 - bt1 ) / sleep_time ) / 1024 ))
d_speed=$(( ( ( br2 - br1 ) / sleep_time ) / 1024 ))

printf '%s\n' "Average Network Speeds: Download: ${d_speed}KB/s, Upload: ${u_speed}KB/s"

# CPU Temp

cpu_temp=$(cat /sys/class/thermal/thermal_zone0/temp)
printf '%s\n' "CPU Temperature: ${cpu_used}%"

# Send to InfluxDB:

curl -i -XPOST "$influxdb_ip/write?u=$influxdb_username&p=$influxdb_password&db=$influxdb_database" --data-binary "$influxdb_report_name storage_usage=${used_space//%},cpu_load=${cpu_load_average//,},cpu_percentage=$cpu_used,ram_percentage=$ram_percentage,swap_percentage=$swap_percentage,download=$d_speed,upload=$u_speed,cpu_temp=$cpu_temp"
