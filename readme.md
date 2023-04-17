# SUI Node Monitoring Script

This script helps you monitor SUI nodes by periodically fetching relevant metrics and reporting them to a Slack channel. If any metric doesn't increase since the last run, or if a node is down, the script tags specified users in the Slack message.

## Prerequisites

- Python 3
- `slack_sdk` and `PyYAML` Python packages
- Slack bot with a valid token

## Installation

1. Clone the repository or download the Python script and configuration files.

2. Install the required Python packages by running:

```bash
pip install slack_sdk PyYaml
```


## Configuration

1. Edit the `config.yaml` file to customize the script according to your requirements:

- `sui_node_endpoints`: A list of your SUI node endpoints, with a name and URL for each node.
- `slack_token`: Your Slack bot token.
- `slack_channel`: The Slack channel where the bot will post messages.
- `metrics_to_fetch`: Metrics to fetch from the SUI node.
- `metrics_to_monitor_for_increase`: Metrics to monitor for increments. The script will alert you if these metrics haven't increased since the last run.
- `previous_metrics_file`: File path for storing previous metric values.
- `slack_users_to_mention`: A list of Slack user IDs to mention if there's an issue with a node or a metric.

2. Make sure to replace the placeholders in the `config.yaml` with your actual values.

## Usage

1. Run the Python script:

```shell
python sui-monitor.py
```


2. The script will fetch the specified metrics from the SUI nodes and report them to the configured Slack channel.

## Scheduling

To automatically run the script at regular intervals, you can use a scheduler like `cron` on Linux or macOS, or Task Scheduler on Windows.

For example, to run the script every hour on a Linux or macOS system, you can add the following entry to your `crontab` file:

```
0 * * * * /path/to/python /path/to/sui_node_monitor.py
```

