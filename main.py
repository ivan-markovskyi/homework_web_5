import aiohttp
import asyncio
from datetime import datetime, timedelta
import platform
import sys


class HttpError(Exception):
    pass


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    raise HttpError(f"Error status: {resp.status} for {url}")
        except (aiohttp.ClientConnectorError, aiohttp.InvalidURL) as err:
            raise HttpError(f"Connection error: {url}", str(err))


async def get_info_from_APIPrivat(data: dict) -> dict:
    all_curency = data["exchangeRate"]
    USD_list = [el for el in all_curency if el["currency"] == "USD"]
    EUR_list = [el for el in all_curency if el["currency"] == "EUR"]

    end_result = {
        data["date"]: {
            "USD": {
                "sale": USD_list[0]["saleRate"],
                "purchase": USD_list[0]["purchaseRate"],
            },
            "EUR": {
                "sale": EUR_list[0]["saleRate"],
                "purchase": EUR_list[0]["purchaseRate"],
            },
        }
    }
    return end_result


async def main(number_of_days: int) -> list:
    result = []
    number_of_days -= 1

    while number_of_days >= 0:
        d = datetime.now() - timedelta(days=int(number_of_days))
        shift = d.strftime("%d.%m.%Y")
        number_of_days -= 1
        try:
            response = await request(
                f"https://api.privatbank.ua/p24api/exchange_rates?date={shift}"
            )
            info = await get_info_from_APIPrivat(response)
            result.append(info)

        except HttpError as err:
            print(err)
            return None
    return result


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        if int(sys.argv[1]) in range(1, 11):
            res = asyncio.run(main(int(sys.argv[1])))
            print(res)
        else:
            print("Передайте ціле число не більше 10")
    except IndexError:
        print("Аргументи командного рядка не містять необхідних даних")
    except ValueError:
        print("Введіть ціле число від 1 до 10")
