# Dynamic Production Scheduler

This repository contains a small Python program that builds a dynamic production
schedule across multiple lines with varying output rates.

## Input format

Provide a JSON file describing production lines and orders:

```json
{
  "lines": [
    {"name": "Line A", "outputs": {"Widget": 25, "Gadget": 18}},
    {"name": "Line B", "outputs": {"Widget": 30}}
  ],
  "orders": [
    {"id": "SO-100", "item": "Widget", "quantity": 120, "due_hours": 6},
    {"id": "SO-101", "item": "Gadget", "quantity": 60, "due_hours": 5}
  ]
}
```

## Running the scheduler

```bash
python main.py path/to/input.json --output schedule.json
```

If you omit `--output`, the schedule prints to stdout.

## Output format

The scheduler returns a JSON array with the selected line, start/end hours, and
lateness per order.
