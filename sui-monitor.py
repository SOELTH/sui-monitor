#!/usr/bin/env python3
import os
import requests
import yaml
from concurrent.futures import ThreadPoolExecutor
from slack_sdk import WebClient

ONLINE_STATUS = '🟢'
CONFIG_FILE = "config.yaml"

def load_config():
    with open(CONFIG_FILE, "r") as file:
        config = yaml.safe_load(file)
    return config

config = load_config()

def fetch_previous_metrics():
    try:
        with open(config["previous_metrics_file"], "r") as file:
            previous_metrics = yaml.safe_load(file)
    except FileNotFoundError:
        previous_metrics = {}
    return previous_metrics

def store_previous_metrics(previous_metrics):
    with open(config["previous_metrics_file"], "w") as file:
        yaml.dump(previous_metrics, file)

previous_metrics = fetch_previous_metrics()

def fetch_metrics(node_url):
    try:
        response = requests.get(node_url)
        response.raise_for_status()
        raw_metrics = response.text

        metrics = {}
        for line in raw_metrics.splitlines():
            for metric in config["metrics_to_fetch"]:
                if line.startswith(metric):
                    value = float(line.split(' ')[1]) # Use float for comparing numeric metrics
                    metrics[metric] = value

        return (node_url, True, metrics)

    except Exception as e:
        return (node_url, False, str(e))

def format_value(value):
    return f'{int(value)}' if isinstance(value, float) and value.is_integer() else f'{value}'

def report_to_slack(node_name, node_url, status, metrics_or_error):
    slack_client = WebClient(config["slack_token"])
    users_to_tag = ' '.join(config["slack_users_to_tag"])
    if status:
        message = f"Node: {node_name} {ONLINE_STATUS}\n"
        for metric, value in metrics_or_error.items():
            message += f"- {metric}: {format_value(value)}\n"
            
            if metric in config["metrics_to_monitor_for_increase"]:
                prev_value = previous_metrics.get(node_url, {}).get(metric, None)
                if prev_value is not None and value <= prev_value:
                    message += f"⚠️ {metric} has not increased since the last run: {format_value(value)} <= {format_value(prev_value)} {users_to_tag}\n"
    else:
        message = f"⚠️ Error fetching metrics for node {node_url}: {metrics_or_error} {users_to_tag}"

    slack_client.chat_postMessage(channel=config["slack_channel"], text=message)


def main():
    with ThreadPoolExecutor(max_workers=len(config["sui_node_endpoints"])) as executor:
        futures = [executor.submit(fetch_metrics, node["url"]) for node in config["sui_node_endpoints"]]
        results = [f.result() for f in futures]

    for node, (node_url, status, metrics_or_error) in zip(config["sui_node_endpoints"], results):
        report_to_slack(node["name"], node_url, status, metrics_or_error)
        if status:
            if node_url not in previous_metrics:
                previous_metrics[node_url] = {}
            previous_metrics[node_url].update(metrics_or_error)
    store_previous_metrics(previous_metrics)

if __name__ == "__main__":
    main()

