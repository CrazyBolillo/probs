import argparse
import json
import math
import os
import random
import pathlib

import matplotlib.pyplot as plt
import numpy as np

from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("file", help="File containing ISPs' information")
    parser.add_argument("--output", help="Path where output files will be written to", default="out")
    args = parser.parse_args()

    with open(os.path.abspath(args.file), 'r') as fl:
        config = json.load(fl)

    days = config["simulation"]["days"]
    days_array = np.array([i for i in range(1, days + 1)])

    for provider, values in config["providers"].items():
        config["providers"][provider]["predicted_downs"] = math.ceil(days - (days * (values["uptime"] / 100)))

    prov_color = 1
    prov_uptime = {}
    for provider, values in config["providers"].items():
        prov_uptime[provider] = [
            0 if random.randint(0, 100) <= values["uptime"] else prov_color + random.random() * 0.8
            for _x in range(days)
        ]
        plt.scatter(days_array, np.array(prov_uptime[provider]), label=provider)
        prov_color += 1

    predicted_downtime = 0
    prov_info = config["providers"].items()



    downtime = 0
    prov_bandwidth = []
    for i in range(days):
        failed = True
        bandwidth = 0
        for provider, values in prov_uptime.items():
            if values[i] == 0:
                bandwidth += config["providers"][provider]["megabits"]

            failed &= bool(int(values[i]))

        prov_bandwidth.append(bandwidth)
        if failed:
            downtime += 1

    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "../templates")),
        autoescape=select_autoescape()
    )
    template = env.get_template("report.html")

    output_dir = os.path.abspath(args.output)
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    with open((os.path.join(output_dir, 'probs.html')), 'w') as fl:
        fl.write(template.render(**config, uptime=prov_uptime, downtime=downtime))

    plt.xlabel("Días")
    plt.tick_params(axis="y", which="both", left=False, labelleft=False)
    plt.ylim(bottom=0.8)
    plt.yticks()
    plt.ylabel("Fallas")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "fails.png"))

    bw_options = np.array(list(set(prov_bandwidth)))
    bw_count = []
    for opt in bw_options:
        bw_count.append(prov_bandwidth.count(opt))
    bw_count = np.array(bw_count)

    plt.clf()
    k = plt.bar(bw_options, bw_count, align="center", width=5)
    plt.xticks(bw_options)
    plt.xlabel("Ancho de banda (mpbs)")
    plt.ylabel("Días")
    plt.bar_label(k)
    plt.savefig(os.path.join(output_dir, "bandwidth.png"))


if __name__ == "__main__":
    main()
