import asyncio
import aiohttp
import time

INPUT_FILE = "ip.txt"
OUTPUT_FILE = "proxyip.txt"
TIMEOUT = 10
TEST_SIZE = 500 * 1024  # 500 KB 测速
WORKER_HOST = "banana.cffamw.cloudns.org"

TEST_DOMAINS = ["chat.openai.com", "dash.cloudflare.com"]

async def test_ip(ip, session):
    url = f"http://{ip}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for domain in TEST_DOMAINS:
        headers["Host"] = domain
        try:
            async with session.get(url, headers=headers, timeout=TIMEOUT) as resp:
                if resp.status != 200:
                    return None
        except Exception:
            return None
    return ip


async def main():
    with open(INPUT_FILE) as f:
        ip_list = [line.strip() for line in f if line.strip()]

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [test_ip(ip, session) for ip in ip_list]
        results = await asyncio.gather(*tasks)

    valid_ips = [ip for ip in results if ip]
    with open(OUTPUT_FILE, "w") as f:
        for ip in valid_ips:
            f.write(ip + "\n")

    print(f"✅ 有效 IP 数量：{len(valid_ips)}")

if __name__ == "__main__":
    asyncio.run(main())
