# ATrack
A simple system status tracking script for use with InfluxDB (and Grafana).

Use `atrack.sh` for Linux systems and `atrack-bsd.py` for BSD/macOS systems.

## Screenshots

**ATrack in action:**

Linux:

```           
    _ _____            _   
   /_\_   _| _ __ _ __| |__
  / _ \| || '_/ _` / _| / /
 /_/ \_\_||_| \__,_\__|_\_\
https://github.com/avertly/atrack

Storage Use: 85%
Memory Use: 5757616 out of 8081556 bytes (71%).
Swap Use: 1243648 out of 10485756 bytes (11%).
CPU Use: 30.67%
Sleeping for 5 seconds
Average Network Speeds: Download: 8KB/s, Upload: 1KB/s
HTTP/1.1 204 No Content
Content-Type: application/json
Request-Id: a117ebbf-51e0-11e7-9bae-000000000000
X-Influxdb-Version: 1.2.4
Date: Thu, 15 Jun 2017 15:38:07 GMT
```

BSD/macOS:

```
    _ _____            _   
   /_\_   _| _ __ _ __| |__
  / _ \| || '_/ _\` / _| / /
 /_/ \_\_||_| \__,_\__|_\_\\

https://github.com/avertly/atrack

Memory Use: 3918360 out of 3942796 bytes (99.38%)
Wired Memory: 1592480 bytes (40.39%)
Swap Use: 1513.25 out of 2048.0 bytes (73.89%)
CPU Load: 4.7
Sleeping for 10 seconds
Download: 0.56083984375KB/s, Upload: 0.2994140625KB/s
Comp: 25030.8/s, Decomp: 13779.2/s
Reads: 85.8/s, Writes: 29.6/s
Pageins: 161.2/s, Pageouts: 5.2/s
Swapins: 3847.2/s, Swapouts: 0.0/s
HTTP/1.1 204 No Content
Content-Type: application/json
Request-Id: db52c42b-51e0-11e7-9bed-000000000000
X-Influxdb-Version: 1.2.4
Date: Thu, 15 Jun 2017 15:39:45 GMT
```

Compression/Decompression refers to how macOS compresses RAM- [you can read more about it here](https://www.lifewire.com/understanding-compressed-memory-os-x-2260327).

Memory use numbers are not particulaly useful- macOS loves to use any unused memory for caching.

**Grafana View:**
Linux:

![The Grafana Dashboard we use](https://i.imgur.com/2IhhDhe.png)
macOS:

![And the other for macOS](https://i.imgur.com/dP1QIvN.png)

## Setting up ATrack

- Create an InfluxDB database and user, give the user write permissions to that DB. Note down the DB's IP, database's name, the user's username and password.
- Learn which network device you use (`ifconfig` might be helpful), note it down
- Learn which storage drive you use (`df -h` might be helpful), note it down
- Change configuration parts after the `Start of configuration part` portion of script with the stuff you just noted down.
- Run `atrack.sh` if you want to run it once, run `run.sh` (preferably in `screen`) if you want it to run repeatedly.

## Using systemd Timers

- Go to `systemd-timer` folder, open up `atrack.service` change path for the script to your script's path.
- Copy both files to `/etc/systemd/system`.
- run `sudo systemctl daemon-reload`
- run `sudo systemctl enable atrack.timer`

It should work.
