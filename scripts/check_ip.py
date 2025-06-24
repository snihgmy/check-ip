import asyncio
import aiohttp
import time

INPUT_FILE = "ip.txt"
ALL_FILE = "proxyip.txt"
FAST_FILE = "fastip.txt"
SLOW_FILE = "slowip.txt"

TIMEOUT = 10
TEST_SIZE = 500 * 1024  # 500 KB
SPEED_THRESHOLD = 1024  # KB/s，1MB/s

TEST_DOMAINS = ["chat.openai.com", "dash.cloudflare.com"]

async def test_ip(ip, session):
    url = f"http://{ip}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Encoding": "identity"
    }

    total_speed = []

    for domain in TEST_DOMAINS:
        headers["Host"] = domain
        try:
            start = time.time()
            async with session.get(url, headers=headers, timeout=TIMEOUT) as resp:
                if resp.status != 200:
                    return (ip, "fail", 0)
                data = await resp.content.read(TEST_SIZE)
                duration = time.time() - start
                speed = len(data) / duration / 1024  # KB/s
                total_speed.append(speed)
        except Exception:
            return (ip, "fail", 0)

    avg_speed = sum(total_speed) / len(total_speed)
    if avg_speed >= SPEED_THRESHOLD:
        return (ip, "fast", avg_speed)
    else:
        return (ip, "slow", avg_speed)

async def main():
    with open(INPUT_FILE) as f:
        ip_list = [line.strip() for line in f if line.strip()]

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [test_ip(ip, session) for ip in ip_list]
        results = await asyncio.gather(*tasks)

    fast_ips = []
    slow_ips = []
    all_ips = []

    for ip, status, speed in results:
        if status == "fail":
            continue
        all_ips.append(ip)
        if status == "fast":
            fast_ips.append(ip)
        elif status == "slow":
            slow_ips.append(ip)

    with open(ALL_FILE, "w") as f:
        f.writelines(ip + "\n" for ip in all_ips)

    with open(FAST_FILE, "w") as f:
        f.writelines(ip + "\n" for ip in fast_ips)

    with open(SLOW_FILE, "w") as f:
        f.writelines(ip + "\n" for ip in slow_ips)

    print(f"✅ 总可用 IP: {len(all_ips)}，高速 IP: {len(fast_ips)}，低速 IP: {len(slow_ips)}")

if __name__ == "__main__":
    asyncio.run(main())
