import asyncio
import logging
from datetime import datetime, UTC, timedelta

from db import SessionLocal
from Repositories import ticket_repository, ticket_notification_repository

logger = logging.getLogger(__name__)
async def cleanup_old_tickets_loop():
    try:
        while True:
            with SessionLocal() as session:
                cutoff = datetime.now(UTC) - timedelta(hours=24)
                old_tickets = ticket_repository.find_closed_before(session, cutoff)
                for ticket in old_tickets:
                    ticket_notification_repository.delete_by_ticket_id(session, ticket_id=ticket.id)
                    ticket_repository.delete_ticket_by_id(session, ticket_id=ticket.id)

            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info('Cleanup loop cancelled')
        raise

