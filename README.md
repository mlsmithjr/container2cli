
## container2cli

This utility allows you to generate docker cli commands or a compose file to recreate your containers.
This is helpful when you have existing containers and no existing shell script or compose file, or you want to move to using docker-compose.

Be aware that this tool exports all environment variables assigned to a container.  
This includes some defined in the container itself and not by the user.  
It attempts to filter out some "cruft" but there is no way to know which env settings were created by the user.
If you wish to add your own then edit the _filters_ list at the top of the script.

It is a work in progress and feedback/pull requests are appreciated.

### Install:
Clone this repo, then in a shell or command prompt:
```shell
pip3 install -r requirements.txt
```
**Currently does not run on Synology, but you can connect to one using --host**


### Usage:
container2cli.py [--host <_host ip:port>_] [--compose | --cli] <_container name_> ...

**--host**, optional.  If given, will remote-connect to the specified Docker instance.  If omitted, will default to the host being run on.

**--compose**, generate a docker-compose file

**--cli**, generate shell scripts (default)

**container name**, one or more container names to export

### Examples:
```shell
python3 container2cli.py sonarr nzbget tautulli

python3 container2cli.py --host homeserver:2375 --compose sonarr radarr portainer
```
