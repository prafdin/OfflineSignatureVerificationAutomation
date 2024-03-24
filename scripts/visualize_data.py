import copy
import datetime
import json
import os
from itertools import groupby

import yaml
from jsonpath_ng.ext import parse
from matplotlib import pyplot as plt
from pathlib import Path

DATA_PATH = "./exps.json"
OUTPUT_DIR = "./output"
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
WORKDIR = os.path.join(OUTPUT_DIR, TIMESTAMP)


def do_filter(exps, path, value):
    filter_exp = parse(path)
    exps = [filter_exp.filter(lambda d: d != value, exp) for exp in copy.deepcopy(exps)]
    return [exp for exp in exps if filter_exp.find(exp)]

def main():
    with open("visualize_config.yaml") as f:
        config = yaml.safe_load(f)

    x_axis_exp = parse(config["x_axis"])
    y_axis_exp = parse(config["y_axis"])

    with open(DATA_PATH) as f:
        exps = json.load(f)

    for filter in config["filters"]:
        exps = do_filter(exps, filter['key'], filter['value'])

    legend = []
    fig_data = []
    for i, key_group in enumerate(groupby(exps, lambda exp: x_axis_exp.filter(lambda d: True, copy.deepcopy(exp))["params"])):
        k, g = key_group
        values_in_group = list(g)
        x = list(x_axis_exp.find(v)[0].value for v in values_in_group)
        y = list(y_axis_exp.find(v)[0].value for v in values_in_group)

        legend.append({
            "label": f"{i}",
            "params": k
        })
        fig_data.append({
            "label": f"{i}",
            "x": x,
            "y": y
        })
        plt.plot(x, y, label=f"{i}")


    Path(WORKDIR).mkdir(parents=True)
    plt.legend()
    plt.savefig(os.path.join(WORKDIR, "figure.png"))
    yaml.dump(legend, open(os.path.join(WORKDIR, "legend.yaml"), "w"))
    yaml.dump(fig_data, open(os.path.join(WORKDIR, "fig_data.yaml"), "w"))
    yaml.dump(config, open(os.path.join(WORKDIR, "config.yaml"), "w"))

if __name__ == '__main__':
    main()
