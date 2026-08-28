from datetime import datetime


# Simulated booking calendar. Any (date, time) pair listed here is already
# reserved by another customer, so a new booking attempt for that slot fails.
ALREADY_BOOKED_SLOTS = {
    ("2026-08-30", "11:00 AM"),
    ("2026-09-01", "04:00 PM"),
}

SITE_VISIT_CLOSED_DAYS = {"Sunday"}

DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]


def book_site_visit(name, phone, date, time, configuration=None):
    """
    Simulate booking a site visit for Northstar One.
    Returns a dict describing whether the booking succeeded, and why not
    when it fails, so the agent can explain the outcome to the customer.
    """

    if not name or not phone or not date or not time:
        return {
            "success": False,
            "reason": "missing_information",
            "message": "Name, phone number, date, and time are all required to book a site visit."
        }

    parsed_date = _parse_date(date)

    if parsed_date is None:
        return {
            "success": False,
            "reason": "invalid_date",
            "message": f"'{date}' is not a recognisable date. Please share a date like 2026-08-30."
        }

    if parsed_date.date() < datetime.now().date():
        return {
            "success": False,
            "reason": "past_date",
            "message": "That date has already passed. Please choose an upcoming date."
        }

    if parsed_date.strftime("%A") in SITE_VISIT_CLOSED_DAYS:
        return {
            "success": False,
            "reason": "closed_on_day",
            "message": "Site visits are not available on Sundays. Please choose another day."
        }

    if (date, time) in ALREADY_BOOKED_SLOTS:
        return {
            "success": False,
            "reason": "slot_unavailable",
            "message": f"The {time} slot on {date} is already booked. Please choose a different time."
        }

    return {
        "success": True,
        "reason": "confirmed",
        "message": f"Site visit confirmed for {name} on {date} at {time}.",
        "booking_id": _generate_booking_id(date, time, phone),
        "name": name,
        "phone": phone,
        "date": date,
        "time": time,
        "configuration": configuration
    }


def _parse_date(date_str):

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    return None


def _generate_booking_id(date, time, phone):

    raw = f"{date}{time}{phone}".replace(" ", "").replace(":", "").replace("-", "")

    return "NSV-" + raw[-6:].upper()
