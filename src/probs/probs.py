import argparse
import json
import math
import os
import random
import pathlib

import matplotlib.pyplot as plt
import numpy as np

from statistics import mean
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

    prov_info = list(config["providers"].values())
    max_bandwidth = prov_info[0]["megabits"]
    predicted_downtime = (100 - prov_info[0]["uptime"]) / 100
    for provider in prov_info[1:]:
        max_bandwidth += provider["megabits"]
        predicted_downtime *= (100 - provider["uptime"]) / 100
    predicted_downtime = round(config["simulation"]["days"] * predicted_downtime, 2)

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
        fl.write(template.render(
            **config,
            uptime=prov_uptime,
            downtime=downtime,
            predicted_downtime=predicted_downtime,
            round_predicted_downtime=round(predicted_downtime),
            max_bandwidth=max_bandwidth,
            mean_bandwidth=round(mean(prov_bandwidth), 2)
        ))

    plt.xlabel("Días")
    plt.tick_params(axis="y", which="both", left=False, labelleft=False)
    plt.ylim(bottom=0.8)
    plt.yticks()
    plt.ylabel("Fallas")
    plt.legend()
    plt.grid(True)
    plt.title("Fallas de los proveedores")
    plt.savefig(os.path.join(output_dir, "fails.png"))

    bw_options = list(set(prov_bandwidth))
    bw_count = []
    for opt in bw_options:
        bw_count.append(prov_bandwidth.count(opt))

    plt.clf()
    plt.pie(
        bw_count,
        labels=[str(bw) + " mbps" for bw in bw_options],
        autopct=lambda pct: "%d" % np.round(pct / 100 * config["simulation"]["days"], 0),
        explode=[0.5 for _i in range(len(bw_options))]
    )
    plt.title("Ancho de banda (mpbs) y días")
    plt.savefig(os.path.join(output_dir, "bandwidth.png"))


if __name__ == "__main__":
    main()
