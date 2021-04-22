import docker
import sys

env_filters = ["PATH=", "LANGUAGE=", "LANG=", "TERM=", "HOME=", "XDG_", "PS1=", "S6"]


if __name__ == "__main__":
    mode = "cli"
    names = list()
    i = 1
    host = None
    while True:
        if i >= len(sys.argv):
            break
        arg = sys.argv[i]
        if arg == "--cli":
            mode = "cli"
        elif arg == "--compose":
            mode = "compose"
        elif arg == "--host":
            i += 1
            host = sys.argv[i]
        else:
            names.append(arg)
        i += 1

    client = None
    if host:
        client = docker.DockerClient(base_url=f"tcp://{host}")
    else:
        client = docker.from_env()

    if mode == "cli":

        for name in names:
            x = client.containers.get(name)
            config = x.attrs["HostConfig"]

            cli = list()
            cli.append(f"docker create --name {name}")
            for b in config["Binds"]:
                cli.append(f"  -v {b}")

            if config.get("PortBindings", None):
                for cport, hipport in config["PortBindings"].items():
                    for hostd in hipport:
                        hport = hostd["HostPort"]
                        cli.append(f"  -p {hport}:{cport}")

            if config.get("Env", None):
                for env in config["Env"]:
                    for f in env_filters:
                        if env.startswith(f):
                            break
                    else:
                        cli.append(f"  -e {env}")

            restart = config["RestartPolicy"]["Name"]
            if len(restart):
                cli.append(f'  --restart="{restart}"')

            if "Privileged" in config:
                if config["Privileged"]:
                    cli.append(f"  --privileged")

            image = x.image.tags[0]
            cli.append(f"  {image}")

            print(" \\\n".join(cli))
            print()

    elif mode == "compose":
        yml = list()
        networks = dict()

        for name in names:
            x = client.containers.get(name)
            yml.append(f"  {name}:")
            yml.append(f"    container_name: {name}")
            image = x.image.tags[0]
            yml.append(f"    image: {image}")

            config = x.attrs["HostConfig"]
            if "Privileged" in config:
                if config["Privileged"]:
                    yml.append(f"    privileged: true")

            if len(config["Binds"]):
                yml.append("    volumes:")
                for b in filter(lambda bind: bind.startswith("/"), config["Binds"]):
                    yml.append(f"      - {b}")

            dns = config.get("Dns", None)
            if dns:
                yml.append("    dns:")
                for d in dns:
                    yml.append(f"      - {d}")

            networkmode = config.get("NetworkMode", "host")
            if networkmode != "default":
                if networkmode == "host":
                    yml.append("    network_mode: host")
                if networkmode != "host":
                    if networkmode not in networks:
                        n = client.networks.get(networkmode)
                        networks[networkmode] = n.attrs["Driver"]
                    yml.append(f"    networks:")
                    yml.append(f"      - {networkmode}")

            if config.get("PortBindings", None):
                yml.append("    ports:")
                for cport, hipport in config["PortBindings"].items():
                    for hostd in hipport:
                        hport = hostd["HostPort"]
                        yml.append(f"      - {hport}:{cport}")

            if config.get("Env", None):
                yml.append(f"    environment:")
                for env in config["Env"]:
                    for f in env_filters:
                        if env.startswith(f):
                            break
                    else:
                        yml.append(f"      - {env}")
            restart = config["RestartPolicy"]["Name"]
            if len(restart):
                yml.append(f"    restart: {restart}")
            yml.append("")

        print("version: '2'")
        print("services:")
        print("\n".join(yml))
        print("")
        print("networks:")
        for n, v in networks.items():
            print(f"  {n}:\n    driver: {v}")
