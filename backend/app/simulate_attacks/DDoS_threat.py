# simulate_ddos.py
import asyncio
import httpx

TARGET_URL = "https://api.lx-gateway.tech/api/target"


async def send_request(session, client_id):
    try:
        response = await session.get(TARGET_URL)
        print(f"[Client {client_id}] {response.json()}")
    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")


async def simulate_ddos(clients=50, delay_between_requests=0.1):
    async with httpx.AsyncClient() as session:
        tasks = []
        for i in range(clients):
            tasks.append(send_request(session, i))
            await asyncio.sleep(delay_between_requests)  # mimic delay
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(simulate_ddos(clients=100, delay_between_requests=0.05))
