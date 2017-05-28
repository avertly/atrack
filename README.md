# ATrack
A simple system status tracking script for use with InfluxDB (and Grafana).

## Screenshots

**ATrack in action:**

![Terminal outputs of ATrack](https://s.ave.zone/feb.png)

**Grafana View:**

![The Grafana Dashboard we use](https://s.ave.zone/407.png)

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