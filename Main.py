import asyncio

from utils import bot
from app.handlers import router


async def main() -> None:
    await asyncio.gather(
        run_bot(),
    )


async def run_bot() -> None:
    try:
        bot.dispatcher.include_router(router)
        await bot.dispatcher.start_polling(bot.bot)
    except KeyboardInterrupt:
        await bot.bot.close()

if __name__ == '__main__':
    asyncio.run(main())
