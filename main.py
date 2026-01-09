from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from scheduler import Order, ProductionLine, Scheduler


def load_payload(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_lines(payload: Dict[str, Any]) -> List[ProductionLine]:
    lines_payload = payload.get("lines", [])
    lines: List[ProductionLine] = []
    for line in lines_payload:
        name = line["name"]
        outputs = line["outputs"]
        lines.append(ProductionLine(name=name, rates_per_hour=outputs))
    return lines


def parse_orders(payload: Dict[str, Any]) -> List[Order]:
    orders_payload = payload.get("orders", [])
    orders: List[Order] = []
    for order in orders_payload:
        orders.append(
            Order(
                order_id=order["id"],
                item=order["item"],
                quantity=float(order["quantity"]),
                due_hours=order.get("due_hours"),
            )
        )
    return orders


def schedule_to_dict(schedule):
    return [
        {
            "order_id": entry.order_id,
            "item": entry.item,
            "quantity": entry.quantity,
            "line": entry.line,
            "start_hour": round(entry.start_hour, 2),
            "end_hour": round(entry.end_hour, 2),
            "due_hours": entry.due_hours,
            "lateness_hours": None if entry.lateness_hours is None else round(entry.lateness_hours, 2),
        }
        for entry in schedule
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dynamic production scheduler for multiple lines and outputs."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to JSON file containing lines and orders.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the schedule JSON.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    payload = load_payload(args.input)
    lines = parse_lines(payload)
    orders = parse_orders(payload)

    scheduler = Scheduler(lines)
    schedule = scheduler.schedule(orders)
    schedule_payload = schedule_to_dict(schedule)

    if args.output:
        args.output.write_text(json.dumps(schedule_payload, indent=2), encoding="utf-8")
    else:
        print(json.dumps(schedule_payload, indent=2))


if __name__ == "__main__":
    main()
