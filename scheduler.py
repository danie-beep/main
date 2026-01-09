from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class ProductionLine:
    name: str
    rates_per_hour: Dict[str, float]

    def can_make(self, item: str) -> bool:
        return item in self.rates_per_hour

    def rate_for(self, item: str) -> float:
        rate = self.rates_per_hour.get(item)
        if rate is None or rate <= 0:
            raise ValueError(f"Line '{self.name}' cannot produce '{item}' or rate is invalid")
        return rate


@dataclass(frozen=True)
class Order:
    order_id: str
    item: str
    quantity: float
    due_hours: Optional[float] = None


@dataclass
class ScheduledOrder:
    order_id: str
    item: str
    quantity: float
    line: str
    start_hour: float
    end_hour: float
    due_hours: Optional[float]

    @property
    def lateness_hours(self) -> Optional[float]:
        if self.due_hours is None:
            return None
        return max(0.0, self.end_hour - self.due_hours)


class Scheduler:
    def __init__(self, lines: Iterable[ProductionLine]) -> None:
        self._lines = list(lines)
        self._line_available_at: Dict[str, float] = {line.name: 0.0 for line in self._lines}

    def schedule(self, orders: Iterable[Order]) -> List[ScheduledOrder]:
        scheduled: List[ScheduledOrder] = []
        orders_sorted = sorted(
            orders,
            key=lambda order: (float("inf") if order.due_hours is None else order.due_hours, order.order_id),
        )

        for order in orders_sorted:
            best_line: Optional[ProductionLine] = None
            best_end: Optional[float] = None
            best_start: Optional[float] = None

            for line in self._lines:
                if not line.can_make(order.item):
                    continue
                start = self._line_available_at[line.name]
                duration = order.quantity / line.rate_for(order.item)
                end = start + duration
                if best_end is None or end < best_end:
                    best_line = line
                    best_end = end
                    best_start = start

            if best_line is None or best_end is None or best_start is None:
                raise ValueError(f"No available line can produce item '{order.item}'")

            self._line_available_at[best_line.name] = best_end
            scheduled.append(
                ScheduledOrder(
                    order_id=order.order_id,
                    item=order.item,
                    quantity=order.quantity,
                    line=best_line.name,
                    start_hour=best_start,
                    end_hour=best_end,
                    due_hours=order.due_hours,
                )
            )

        return scheduled
