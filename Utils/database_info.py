from sqlalchemy import select

from db import SessionLocal
from Models.user_model import User
from Models.ticket_model import Ticket
from Models.ticket_notification_model import TicketNotification


def main() -> None:
    with SessionLocal() as session:
        users = session.scalars(
            select(User).order_by(User.id)
        ).all()

        tickets = session.scalars(
            select(Ticket).order_by(Ticket.id)
        ).all()

        notifications = session.scalars(
            select(TicketNotification).order_by(TicketNotification.id)
        ).all()

        print("=== USERS ===")

        for user in users:
            print(
                f"id={user.id}, "
                f"telegram_id={user.telegram_id}, "
                f"name={user.full_name!r}, "
                f"role={user.role}"
            )

        print("\n=== TICKETS ===")

        for ticket in tickets:
            print(
                f"id={ticket.id}, "
                f"title={ticket.title!r}, "
                f"status={ticket.status}, "
                f"user_id={ticket.user_id}, "
                f"assigned_admin_id={ticket.assigned_admin_id}, "
                f"completed_by_admin_id={ticket.completed_by_admin_id}"
            )

        print("\n=== NOTIFICATIONS ===")

        for notification in notifications:
            print(
                f"id={notification.id}, "
                f"ticket_id={notification.ticket_id}, "
                f"chat_id={notification.chat_id}, "
                f"message_id={notification.message_id}, "
                f"kind={notification.kind}"
            )


if __name__ == "__main__":
    main()
