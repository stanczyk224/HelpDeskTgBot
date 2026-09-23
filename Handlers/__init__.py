# Handlers/__init__.py
from aiogram import Router

from Handlers.start_handler import router as start_router
from Handlers.ticket_handler import router as ticket_router
from Handlers.admin_handler import router as admin_router
from Handlers.ticket_callbacks_handler import router as ticket_callbacks_router

main_router = Router()

main_router.include_router(ticket_callbacks_router)
main_router.include_router(start_router)
main_router.include_router(ticket_router)
main_router.include_router(admin_router)