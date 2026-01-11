from aiogram import Router
from .user import router as user_router
from .buying import router as buying_router
from .admin import router as admin_router

router = Router()

# Порядок важен: специфичные роутеры выше, общие ниже
router.include_router(admin_router)
router.include_router(buying_router)
router.include_router(user_router)