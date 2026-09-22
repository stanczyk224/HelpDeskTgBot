from db import SessionLocal, Base, engine
from Enums.role_enum import Role
from Service import ticket_service, user_service
from Repositories import user_repository, ticket_repository

# пересоздаём таблицы, чтобы тест был чистым при каждом запуске
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


def test_register_and_promote():
    with SessionLocal() as session:
        user_service.register_user(
            session,
            full_name="Alex Samirov",
            job_title="IT Specialist",
            cabinet="204",
            role=Role.user
        )

    with SessionLocal() as session:
        alex = user_repository.find_user_by_full_name(session, "Alex Samirov")
        print(alex)

    with SessionLocal() as session:
        user_service.register_user(
            session,
            full_name="Denis Muydinov",
            job_title="IT Admin",
            cabinet="101",
            role=Role.admin
        )

    with SessionLocal() as session:
        boss = user_repository.find_user_by_full_name(session, "Denis Muydinov")
        target = user_repository.find_user_by_full_name(session, "Alex Samirov")
        target_id = target.id          # <-- забираем чистое значение, пока сессия жива
        user_service.promote_to_admin(session, actor=boss, user_id=target_id)

    with SessionLocal() as session:
        updated = user_repository.find_user_by_user_id(session, user_id=target_id)  # <-- используем int, не объект
        print(f"After promote: role={updated.role}")


def test_ticket_flow():
    with SessionLocal() as session:
        author = user_repository.find_user_by_full_name(session, "Alex Samirov")
        author_id = author.id
        ticket_service.create_ticket(
            session,
            description="Как дела",
            user_id=author_id,
            title="Привет"
        )

    with SessionLocal() as session:
        author = user_repository.find_user_by_full_name(session, "Alex Samirov")
        author_id = author.id
        ticket_service.create_ticket(
            session,
            description="Принтер не печатает второй день",
            user_id=author_id,
            title="Сломан принтер"
        )

    with SessionLocal() as session:
        tickets = ticket_repository.find_all_tickets(session)
        print(f"Tickets found: {len(tickets)}")
        for ticket in tickets:
            print(ticket)


if __name__ == "__main__":
    test_register_and_promote()
    test_ticket_flow()