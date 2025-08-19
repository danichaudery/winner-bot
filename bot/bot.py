import asyncio
from dotenv import load_dotenv
from .utils.signals import SignalsService


async def main() -> None:
    load_dotenv()
    service = SignalsService()
    await service.start_background_scheduler()
    try:
        # Run forever until interrupted
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await service.shutdown_background_scheduler()


if __name__ == "__main__":
    asyncio.run(main())

