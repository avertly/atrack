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

## Using with crontab instead of run script
- Run `crontab -e`
- Add `* * * * * /bin/bash /path/to/script/atrack.sh > /dev/null 2>&1` to latest line.
- Save and exit, it should work fine.