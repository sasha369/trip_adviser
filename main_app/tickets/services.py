from datetime import timedelta

from core.exceptions import DomainError
from django.db import transaction

from .models import Ticket, TicketGroup

MIN_CONNECTION = timedelta(minutes=30)
GAP = 10
STATUSES = {"required", "booked", "purchased"}
STATUS_TRANSITIONS = {
    "required": {"booked", "purchased"},
    "booked": {"purchased", "required"},
    "purchased": {"booked"},
}

# ------- Группы -------


def get_or_create_group(
    trip, direction: str | None = None, group_id=None
) -> TicketGroup:
    if group_id is not None:
        group = TicketGroup.objects.filter(id=group_id, trip=trip).first()
        if group is None:
            raise DomainError(
                "group_not_found",
                "Цепочка не найдена или принадлежит другой поездке",
                fields={"group_id": ["not_found"]},
            )
        return group
    if direction not in {"outbound", "return", "layover"}:
        raise DomainError(
            "invalid_direction",
            "Направление может быть только outbound, return или layover",
        )
    if direction in {"outbound", "return"}:
        group, _ = TicketGroup.objects.get_or_create(trip=trip, direction=direction)
        return group
    return TicketGroup.objects.create(trip=trip, direction=direction)


def next_order(group) -> int:
    last = group.tickets.order_by("-order").first()
    return last.order + GAP if last else 0


def reindex_group(group: TicketGroup) -> None:
    changed = []
    for i, ticket in enumerate(group.tickets.order_by("order", "id")):
        new_order = i * GAP
        if ticket.order != new_order:
            ticket.order = new_order
            changed.append(ticket)
    if changed:
        Ticket.objects.bulk_update(changed, ["order"])


# ------ Валидация -------


def _validate_ticket(*, trip, departure_at) -> None:
    if departure_at is None:
        raise DomainError(
            "ticket_dates_missing",
            "Отсутствует дата отправки",
            fields={"departure_at": ["required"]},
        )
    if not (trip.start_date <= departure_at.date() <= trip.end_date):
        raise DomainError(
            "ticket_dates_outside",
            "Даты билета вне дат путешествия",
            fields={"departure_at": ["outside_trip_dates"]},
        )


def _chain_violations(group) -> list[dict]:
    chain = list(group.tickets.order_by("order", "id"))
    result = []
    for prev, nxt in zip(chain, chain[1:]):
        gap = nxt.departure_at - prev.arrival_at
        if gap < MIN_CONNECTION:
            result.append(
                {
                    "between": [str(prev.id), str(nxt.id)],
                    "gap_minutes": gap.total_seconds() // 60,
                }
            )
    return result


def _validate_chain(group) -> None:
    violations = _chain_violations(group)
    if violations:
        first = violations[0]
        raise DomainError(
            "connection_gap",
            f"Стыковка {first['gap_minutes']} мин < 30 мин",
            fields={"order": ["connection_gap"], "departure_at": ["connection_gap"]},
        )


# ------- CRUD -------


def set_ticket_status(ticket, new_status: str) -> Ticket:
    if new_status not in STATUSES:
        raise DomainError(
            "invalid_status", "Неизвестный статус", fields={"status": ["invalid"]}
        )
    if new_status == ticket.status:
        return ticket
    allowed = STATUS_TRANSITIONS.get(ticket.status, set())
    if new_status not in allowed:
        raise DomainError(
            "invalid_status_transition",
            f"Нельзя перейти {ticket.status} -> {new_status}",
            fields={"status": ["invalid_transition"]},
        )
    ticket.status = new_status
    ticket.save(update_fields=["status"])
    return ticket


def create_ticket(*, trip, data, for_all_travelers: bool = False) -> Ticket:
    data = dict(data)
    group = data.pop("group", None)
    group_id = data.pop("group_id", None)
    direction = data.pop("direction", "outbound")
    travelers = data.pop("travelers", None)
    data.pop("for_all_travelers", None)
    status = data.get("status")
    if status is not None and status not in STATUSES:
        raise DomainError(
            "invalid_status",
            f"Неизвестный статус: {status}",
            fields={"status": ["invalid"]},
        )

    if group is None:
        group = get_or_create_group(trip=trip, direction=direction, group_id=group_id)
    elif group.trip_id != trip.id:
        raise DomainError(
            "group_not_found",
            "Цепочка принадлежит другой поездке",
            fields={"group": ["not_found"]},
        )

    with transaction.atomic():
        ticket = Ticket.objects.create(group=group, order=next_order(group), **data)
        _validate_ticket(trip=trip, departure_at=ticket.departure_at)
        _validate_chain(group)

        if for_all_travelers:
            ticket.travelers.set(trip.travelers.all())
        elif travelers is not None:
            ticket.travelers.set(travelers)
    return ticket


def update_ticket(ticket, data, *, group_id=None, order=None) -> Ticket:
    data = dict(data)
    group = data.pop("group", None)
    travelers = data.pop("travelers", None)
    new_status = data.pop("status", None)
    data.pop("for_all_travelers", None)
    if group is not None:
        group_id = group.id

    with transaction.atomic():
        old_group = ticket.group
        target_group = old_group
        if group_id is not None:
            target_group = get_or_create_group(trip=old_group.trip, group_id=group_id)

        for field, value in data.items():
            setattr(ticket, field, value)

        moved = target_group.pk != old_group.pk
        if moved:
            ticket.group = target_group
            ticket.order = next_order(target_group) if order is None else order
        elif order is not None:
            ticket.order = order

        ticket.save()

        if travelers is not None:
            ticket.travelers.set(travelers)

        if new_status is not None:
            set_ticket_status(ticket, new_status)

        reindex_group(old_group)
        if moved:
            reindex_group(target_group)

        _validate_ticket(trip=ticket.group.trip, departure_at=ticket.departure_at)
        for chain in {old_group, target_group}:
            _validate_chain(chain)
    return ticket


def delete_ticket(ticket: Ticket) -> None:
    group = ticket.group
    ticket_id = ticket.id
    with transaction.atomic():
        ticket.delete()
        if not group.tickets.exclude(id=ticket_id).exists():
            group.delete()
        else:
            reindex_group(group)
