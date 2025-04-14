from datetime import datetime
import csv


logs = []


def add_to_log(type: str, prompt: str, content: str):
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "type": type,
        "prompt": prompt,
        "response": content
    })


def write_logs_to_file(filename: str):
    with open(filename, 'w') as f:
        fieldnames = ["timestamp", "type", "prompt", "response"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for entry in logs:
            writer.writerow(entry)
