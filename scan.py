import os
import argparse
import asyncio
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Browser, BrowserContext
from PIL import Image, ImageDraw, ImageFont
import io
import subprocess
from asyncio import Semaphore
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)  # Auto reset colors after each print

OUTPUT_DIR = "output"
SCREENSHOT_DIR = os.path.join(OUTPUT_DIR, "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
CONCURRENCY_LIMIT = 12  # Tune for performance


def sanitize_filename(name):
    return name.replace("http://", "").replace("https://", "").replace("/", "_").strip()


def get_unique_filename(base_name, directory, ext=".pdf"):
    filename = f"{base_name}{ext}"
    counter = 1
    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base_name}_{counter}{ext}"
        counter += 1
    return filename


def add_label_to_image(image_bytes, label):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
        banner_font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        banner_font = ImageFont.load_default()

    label_height = 80
    banner_height = 30

    new_image = Image.new("RGB", (image.width, image.height + label_height), (255, 255, 255))
    new_image.paste(image, (0, label_height))
    draw = ImageDraw.Draw(new_image)

    draw.rectangle([(0, 0), (image.width, banner_height)], fill=(0, 0, 64))
    draw.rectangle([(0, banner_height), (image.width, label_height)], fill=(0, 0, 0))

    draw.text((10, 5), "Created by RockSec", font=banner_font, fill=(255, 255, 255))
    draw.text((10, banner_height + 10), label, font=font, fill=(255, 255, 255))

    return new_image


async def capture_single_url(sem: Semaphore, browser: Browser, url: str, screenshot_images: list):
    async with sem:
        try:
            context: BrowserContext = await browser.new_context()
            page = await context.new_page()
            if not url.startswith("http"):
                url = "http://" + url
            print(f"{Fore.BLUE}[+] Visiting: {url}")
            await page.goto(url, timeout=60000)
            image_bytes = await page.screenshot(full_page=True)
            labeled_image = add_label_to_image(image_bytes, url)
            screenshot_images.append(labeled_image)
            await context.close()
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to capture {url}: {e}")


async def capture_urls(urls, output_pdf_name):
    screenshot_images = []
    sem = Semaphore(CONCURRENCY_LIMIT)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        tasks = [capture_single_url(sem, browser, url, screenshot_images) for url in urls]
        await asyncio.gather(*tasks)
        await browser.close()

    if screenshot_images:
        final_pdf_name = get_unique_filename(output_pdf_name, SCREENSHOT_DIR)
        pdf_path = os.path.join(SCREENSHOT_DIR, final_pdf_name)
        screenshot_images[0].save(
            pdf_path,
            save_all=True,
            append_images=screenshot_images[1:]
        )
        print(f"{Fore.GREEN}[✔] Screenshots saved to PDF: {pdf_path}")
    else:
        print(f"{Fore.RED}[!] No screenshots were captured.")


def discover_subdomains(domain):
    print(f"{Fore.BLUE}[+] Discovering subdomains for {domain} ...")
    try:
        result = subprocess.run(["assetfinder", "--subs-only", domain], capture_output=True, text=True)
        subdomains = result.stdout.strip().split("\n")
        return [sub for sub in subdomains if sub]
    except Exception as e:
        print(f"{Fore.RED}[!] Subdomain discovery failed: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Website Screenshot Capture Tool by RockSec")
    parser.add_argument("--url", help="Single domain to scan")
    parser.add_argument("--subdomains", help="Scan subdomains of a domain")
    parser.add_argument("--urlfile", help="File containing list of URLs")

    args = parser.parse_args()
    urls_to_scan = []
    output_pdf_name = "screenshots"

    if args.url:
        urls_to_scan.append(args.url)
        output_pdf_name = sanitize_filename(args.url)

    elif args.subdomains:
        urls_to_scan.extend(discover_subdomains(args.subdomains))
        output_pdf_name = f"{sanitize_filename(args.subdomains)}_subdomains"

    elif args.urlfile:
        with open(args.urlfile, "r") as f:
            urls_to_scan.extend([line.strip() for line in f.readlines() if line.strip()])
        output_pdf_name = sanitize_filename(os.path.basename(args.urlfile))

    else:
        parser.print_help()
        return

    asyncio.run(capture_urls(urls_to_scan, output_pdf_name))


if __name__ == "__main__":
    main()
