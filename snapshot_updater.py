import json
import re
import argparse
from datetime import datetime, timedelta
from os import listdir


class SnapshotUpdater:
    def __init__(self, exp_time):
        self.expiration_time = timedelta(days=int(exp_time))

    def add_timedelta(self, m):
        parsed_time = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S.%f") \
                      + self.expiration_time
        return parsed_time.isoformat(timespec="milliseconds")

    def update_time(self, actions, time_prefix):
        return re.sub(
            f"{time_prefix}_time\":\"(.*?)Z",
            lambda m: f"{time_prefix}_time\":\"{self.add_timedelta(m)}Z",
            actions
        )

    @staticmethod
    def read_snapshot(snapshot_file):
        with open(snapshot_file) as file:
            snapshot_data = json.load(file)
            return snapshot_data

    @staticmethod
    def write_snapshot(snapshot_file, snapshot_data):
        with open(snapshot_file, mode="w") as file:
            json.dump(snapshot_data, file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--integration", required=True)
    parser.add_argument("--expiration_time", required=True)
    args = parser.parse_args()

    snapshots_dir = [
        elem for elem in listdir() if
        elem == args.integration
    ]

    snapshot_updater = SnapshotUpdater(args.expiration_time)
    for snapshot in listdir(snapshots_dir[0]):
        path_to_snapshot = f"{snapshots_dir[0]}/{snapshot}"

        try:
            data = snapshot_updater.read_snapshot(path_to_snapshot)
        except json.JSONDecodeError:
            print(f"Error: File '{snapshot}' is malformed.")
            continue

        actions = data["actions"]
        actions = snapshot_updater.update_time(actions, "start")
        actions = snapshot_updater.update_time(actions, "end")
        data["actions"] = actions

        snapshot_updater.write_snapshot(path_to_snapshot, data)


if __name__ == '__main__':
    main()
