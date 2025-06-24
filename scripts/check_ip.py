import asyncio
import aiohttp
from aiohttp import ClientTimeout

INPUT_FILE = "ip.txt"
OUTPUT_FILE = "proxyip.txt"

WORKER_DOMAIN = "minisub.pages.dev"  # 你的 Cloudflare Pages 或 Workers 域名
CHECK_HOSTS = {
    "chat.openai.com": "ChatGPT",
    "dash.cloudflare.com": "Cloudflare"
}

TIMEOUT = 10  # 秒

async def test_ip(ip: str, session: aiohttp.ClientSession) -> bool:
    headers_template = {
        "User-Agent": "Mozilla/5.0",
        "CF-Connecting-IP": "1.1.1.1",  # 可选：模拟真实请求
    }

    for host, tag in CHECK_HOSTS.items():
        try:
            url = f"http://{ip}"
            headers = headers_template.copy()
            headers["Host"] = host

            async with session.get(url, headers=headers, timeout=ClientTimeout(total=TIMEOUT)) as resp:
                text = await resp.text()
                if "cf-error" in text or resp.status != 200:
                    return False
        except Exception:
            return False
    return True

async def main():
    with open(INPUT_FILE, "r") as f:
        ip_list = [line.strip() for line in f if line.strip()]

    results = []
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [test_ip(ip, session) for ip in ip_list]
        check_results = await asyncio.gather(*tasks)

    for ip, is_valid in zip(ip_list, check_results):
        if is_valid:
            results.append(ip)

    with open(OUTPUT_FILE, "w") as f:
        for ip in results:
            f.write(ip + "\n")

    print(f"✅ 有效IP数量: {len(results)}")

if __name__ == "__main__":
    asyncio.run(main())
