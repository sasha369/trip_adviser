from datetime import timedelta
from urllib.parse import quote_plus

from django.db import transaction

from core.exceptions import DomainError

from .models import Day, Goal, Trip

GAP = 10  # шаг для sort_order


def _date_range(start, end):
    """Просчитывает дни между start и end. \\
        Возвращает список дней"""
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]


# -------- Путешествия --------


def create_trip(user, data: dict) -> Trip:
    travelers = data.pop("travelers", [])
    with transaction.atomic():
        # атомарная транзакция - значит бд ничего не сохранит если выйдет ошибка во время выполнения
        trip = Trip.objects.create(user=user, **data)
        if travelers:
            trip.travelers.set(travelers)
        Day.objects.bulk_create(
            [
                Day(trip=trip, date=d)
                for d in _date_range(trip.start_date, trip.end_date)
            ]
        )
    return trip


def update_trip(trip: Trip, data: dict) -> Trip:
    """При сдвиге дат дни пересобираются"""
    travelers = data.pop("travelers", None)
    new_start = data.get("start_date", trip.start_date)
    new_end = data.get("end_date", trip.end_date)

    with transaction.atomic():
        for field, value in data.items():
            setattr(trip, field, value)
        trip.save()

        if travelers is not None:
            trip.travelers.set(travelers)

        expected = set(_date_range(new_start, new_end))
        existing = {d.date: d for d in trip.days.all()}

        dropped = [d for date, d in existing.items() if date not in expected]
        if any(d.goals.exists() for d in dropped):
            raise DomainError(
                "dates_drop_goal",
                "В днях за пределами новых дат есть цели - перенесите или удалите их",
            )
        for day in dropped:
            day.delete()

        Day.objects.bulk_create(
            [Day(trip=trip, date=d) for d in expected - set(existing)]
        )
    return trip


def copy_trip(trip: Trip, *, start_date, end_date) -> Trip:
    """Копирование структуры на новые даты, кроме выполнения и билетов"""
    if end_date < start_date:
        raise DomainError("invalid_dates", "Дата окончания раньше даты начала")

    with transaction.atomic():
        new = Trip.objects.create(
            user=trip.user,
            title=trip.title,
            start_date=start_date,
            end_date=end_date,
            origin=trip.origin,
            destination=trip.destination,
        )
        new.travelers.set(trip.travelers.all())

        old_days = list(trip.days.prefetch_related("goals").order_by("date"))
        for i, date in enumerate(_date_range(start_date, end_date)):
            old = old_days[i] if i < len(old_days) else None
            new_day = Day.objects.create(
                trip=new,
                date=date,
                title=old.title if old else "",
                description=old.description if old else "",
                geo_location=old.geo_location if old else "",
            )
            if old:
                Goal.objects.bulk_create(
                    [
                        Goal(
                            day=new_day,
                            title=g.title,
                            description=g.description,
                            is_mandatory=g.is_mandatory,
                            start_time=g.start_time,
                            end_time=g.end_time,
                            sort_order=g.sort_order,
                        )
                        for g in old.goals.all()
                    ]
                )
    return new


def route_options(trip: Trip) -> dict:
    """Ссылки на маршрут и поиск билетов"""
    o, d = quote_plus(trip.origin), quote_plus(trip.destination)
    return {
        "map_url": f"https://yandex.ru/maps/?rtext={o}~{d}&rtt=auto",
        "options": [
            {
                "transport": "plane",
                "search_url": f"https://www.aviasales.ru/?from={o}&to={d}",
            },
            {
                "transport": "train",
                "search_url": f"https://www.tutu.ru/poezda/?from={o}&to={d}",
            },
            {
                "transport": "bus",
                "search_url": f"https://www.tutu.ru/bus/?from={o}&to={d}",
            },
            {
                "transport": "car",
                "search_url": f"https://yandex.ru/maps/?rtext={o}~{d}&rtt=auto",
            },
        ],
    }
