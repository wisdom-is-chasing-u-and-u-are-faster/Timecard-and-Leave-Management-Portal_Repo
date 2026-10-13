from typing import Dict, List, Tuple


def calculate_daily_hours(raw_hours: float) -> Tuple[float, float, float]:
    """
    Computes regular, overtime (1.5x for >8h), and double-time (2.0x for >12h) hours for a single workday.
    Returns (regular, overtime, double_time).
    """
    if raw_hours <= 0:
        return 0.0, 0.0, 0.0

    if raw_hours <= 8.0:
        return round(raw_hours, 2), 0.0, 0.0
    elif raw_hours <= 12.0:
        reg = 8.0
        ot = round(raw_hours - 8.0, 2)
        return reg, ot, 0.0
    else:
        reg = 8.0
        ot = 4.0
        dt = round(raw_hours - 12.0, 2)
        return reg, ot, dt


def calculate_pay_period_flsa(daily_hours_list: List[float], hourly_rate: float = 25.0) -> Dict[str, float]:
    """
    Computes weekly and pay period FLSA totals including standard weekly overtime (>40h threshold).
    """
    total_hours = round(sum(daily_hours_list), 2)
    total_dt = 0.0
    for h in daily_hours_list:
        if h > 12.0:
            total_dt += round(h - 12.0, 2)

    non_dt_hours = total_hours - total_dt
    if non_dt_hours >= 40.0:
        regular_hours = 40.0
        overtime_hours = round(non_dt_hours - 40.0, 2)
    else:
        # Check daily overtime (>8h)
        daily_ot = sum(max(0.0, round(min(h, 12.0) - 8.0, 2)) for h in daily_hours_list)
        regular_hours = round(total_hours - total_dt - daily_ot, 2)
        overtime_hours = round(daily_ot, 2)

    gross_pay = (regular_hours * hourly_rate) + (overtime_hours * hourly_rate * 1.5) + (total_dt * hourly_rate * 2.0)

    return {
        "total_hours": total_hours,
        "regular_hours": regular_hours,
        "overtime_hours": overtime_hours,
        "double_time_hours": round(total_dt, 2),
        "gross_pay_estimate": round(gross_pay, 2)
    }


class FLSAEngine:
    """FLSA Calculation Engine for Statutory Overtime and Wage Computations."""

    @staticmethod
    def calculate_daily_distribution(raw_hours: float) -> Dict[str, float]:
        reg, ot, dt = calculate_daily_hours(raw_hours)
        return {
            "regular": reg,
            "overtime": ot,
            "double_time": dt
        }

    @staticmethod
    def calculate_pay_period_summary(daily_hours_list: List[float], hourly_rate: float = 25.0) -> Dict[str, float]:
        return calculate_pay_period_flsa(daily_hours_list, hourly_rate)
