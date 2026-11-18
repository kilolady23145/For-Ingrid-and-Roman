import os
import re
import json
import random
import html
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import feedparser

# 新聞來源：BBC 科學環境、NASA、ScienceDaily 動物與太空
RSS_FEEDS = [
    ("BBC Science & Nature", "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    ("NASA Breaking News", "https://www.nasa.gov/news-release/feed/"),
    ("ScienceDaily Animals", "https://www.sciencedaily.com/rss/plants_animals.xml"),
    ("ScienceDaily Space", "https://www.sciencedaily.com/rss/space_time.xml"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def http_get_text(url: str, timeout: int = 10, max_bytes: int = 200000) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read(max_bytes)
        return raw.decode("utf-8", errors="ignore")


def upgrade_image_quality(url: str) -> str:
    """將常見新聞縮圖網址升級為較清晰的尺寸"""
    if not url:
        return ""
    url = html.unescape(url.strip())
    if url.startswith("//"):
        url = "https:" + url
    if "ichef.bbci.co.uk" in url:
        url = re.sub(r"/news/\d+/", "/news/976/", url)
    return url


def extract_rss_image(entry) -> str:
    """第一順位：從 RSS 項目中尋找新聞原圖"""
    for media in entry.get("media_content", []) or []:
        url = media.get("url", "")
        medium = media.get("medium", "")
        mtype = media.get("type", "")
        if url and ("image" in medium or "image" in mtype or re.search(r"\.(jpg|jpeg|png|webp)", url, re.I)):
            return upgrade_image_quality(url)

    for thumb in entry.get("media_thumbnail", []) or []:
        if thumb.get("url"):
            return upgrade_image_quality(thumb["url"])

    for link in entry.get("links", []) or []:
        if "image" in link.get("type", "") and link.get("href"):
            return upgrade_image_quality(link["href"])

    summary_html = entry.get("summary", "") or ""
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', summary_html, re.I)
    if match:
        return upgrade_image_quality(match.group(1))

    return ""


def extract_og_image(article_url: str) -> str:
    """第二順位：連線到新聞原網頁抓取公開封面大圖 (og:image)"""
    if not article_url:
        return ""
    try:
        text = http_get_text(article_url, timeout=10, max_bytes=70000)
        patterns = [
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
            r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.I)
            if m:
                img_url = urllib.parse.urljoin(article_url, html.unescape(m.group(1)))
                if not any(bad in img_url.lower() for bad in ["logo", "favicon", "default-share"]):
                    return upgrade_image_quality(img_url)
    except Exception as e:
        print(f"og:image 抓取略過: {e}")
    return ""


def search_wikimedia_photo(query: str) -> tuple:
    """第三順位備案：若原新聞無圖，從維基共享資源搜尋真實照片"""
    if not query:
        return "", ""
    try:
        q = urllib.parse.quote(query)
        api_url = (
            "https://commons.wikimedia.org/w/api.php"
            f"?action=query&generator=search&gsrnamespace=6&gsrsearch={q}"
            "&gsrlimit=5&prop=imageinfo&iiprop=url&iiurlwidth=960&format=json"
        )
        req = urllib.request.Request(api_url, headers={"User-Agent": "IngridRomanDailyReader/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for _, page in pages.items():
            title = page.get("title", "").lower()
            if not title.endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            info_list = page.get("imageinfo", [])
            if info_list:
                thumb_url = info_list[0].get("thumburl") or info_list[0].get("url", "")
                if thumb_url:
                    return thumb_url, "Photo via Wikimedia Commons"
    except Exception as e:
        print(f"Wikimedia 備用圖搜尋略過: {e}")
    return "", ""


def clean_html(raw_html: str) -> str:
    clean = re.sub(r"<[^>]+>", " ", raw_html or "")
    return re.sub(r"\s+", " ", html.unescape(clean)).strip()


def fetch_candidate_articles():
    candidates = []
    for source_name, feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:8]:
                title = clean_html(entry.get("title", ""))
                summary = clean_html(entry.get("summary", "") or entry.get("description", ""))
                link = entry.get("link", "")
                if len(title) < 10 or len(summary) < 40:
                    continue
                lower_text = f"{title} {summary}".lower()
                if any(w in lower_text for w in ["murder", "war", "suicide", "terror", "sexual", "shooting", "deadly crash"]):
                    continue
                rss_img = extract_rss_image(entry)
                candidates.append({
                    "source": source_name,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "rss_image": rss_img,
                })
        except Exception as e:
            print(f"讀取 RSS 失敗 ({source_name}): {e}")
    return candidates


def get_candidate_models(api_key: str) -> list:
    """自動向 Google 查詢此金鑰目前可用的 Gemini Flash 文字模型"""
    discovered = []
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        req = urllib.request.Request(list_url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for m in data.get("models", []):
            name = m.get("name", "").replace("models/", "")
            methods = m.get("supportedGenerationMethods", [])
            if "generateContent" not in methods:
                continue
            lower = name.lower()
            if "gemini" not in lower:
                continue
            if any(skip in lower for skip in ["tts", "image", "vision", "embedding", "aqa", "audio", "robotics", "computer-use"]):
                continue
            discovered.append(name)
    except Exception as e:
        print(f"自動查詢模型清單略過: {e}")

    # 優先使用 flash 系列（速度快、額度最充裕），由新到舊排列
    flash_models = sorted([m for m in discovered if "flash" in m and "lite" not in m], reverse=True)
    other_models = sorted([m for m in discovered if m not in flash_models], reverse=True)
    fallbacks = ["gemini-2.5-flash", "gemini-2.0-flash"]

    ordered = []
    for m in flash_models + other_models + fallbacks:
        if m not in ordered:
            ordered.append(m)
    return ordered


def generate_json_with_gemini(api_key: str, prompt: str) -> dict:
    """逐一嘗試可用模型，確保不會因為單一模型停用而失敗"""
    models = get_candidate_models(api_key)
    print(f"偵測到候選模型順序: {models[:6]}")

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.5,
            "responseMimeType": "application/json",
        },
    }
    body_bytes = json.dumps(payload).encode("utf-8")

    last_error = None
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=body_bytes, headers={"Content-Type": "application/json"}, method="POST")
        try:
            print(f"正在嘗試模型: {model_name} ...")
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            raw_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
            raw_text = re.sub(r"\s*```$", "", raw_text)
            parsed = json.loads(raw_text)
            print(f"✅ 成功使用模型: {model_name}")
            return parsed
        except Exception as e:
            print(f"⚠️ 模型 {model_name} 無法使用，自動換下一個 ({e})")
            last_error = e

    raise RuntimeError(f"所有候選模型皆無法完成請求，最後錯誤: {last_error}")


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 GEMINI_API_KEY，請確認 GitHub Secrets 設定！")

    candidates = fetch_candidate_articles()
    if not candidates:
        raise RuntimeError("今天沒有抓到可用的新聞候選清單。")

    # 優先挑選本身就有附圖的新聞
    with_images = [c for c in candidates if c["rss_image"]]
    pool = with_images if len(with_images) >= 3 else candidates
    chosen = random.choice(pool[:12])

    print(f"今日選中新聞: [{chosen['source']}] {chosen['title']}")

    image_url = chosen["rss_image"]
    image_credit = f"News photo from {chosen['source']}"
    if not image_url:
        og_img = extract_og_image(chosen["link"])
        if og_img:
            image_url = og_img
            image_credit = f"News photo from {chosen['source']}"

    prompt = f"""
You are creating a daily English news reading lesson for two Taiwanese kids (upper elementary to Grade 7, targeting US Grade 5-6 informational reading level, engaging and clear).

Source News:
- Source: {chosen['source']}
- Original Title: {chosen['title']}
- Original Summary: {chosen['summary']}

Rewrite this real news story into an engaging, accurate 3-paragraph article (around 220-300 words total). Do NOT invent fake facts beyond the summary and well-established science background.

Return ONLY valid JSON matching this exact structure:
{{
  "title": "Engaging English headline for kids",
  "category": "Science & Nature",
  "image_caption": "1 short, clear English sentence explaining what this news story is about, suitable under a photo.",
  "image_caption_zh": "圖片說明的繁體中文翻譯（台灣用語）",
  "backup_image_query": "2 to 3 concrete English nouns for searching a real photo if needed, e.g. 'sea otter' or 'mars rover'",
  "paragraphs": [
    {{
      "en": "Paragraph 1 in natural, vivid English (around 70-100 words).",
      "zh": "第一段自然流暢的繁體中文翻譯（台灣慣用語）。"
    }},
    {{
      "en": "Paragraph 2...",
      "zh": "第二段繁體中文翻譯..."
    }},
    {{
      "en": "Paragraph 3...",
      "zh": "第三段繁體中文翻譯..."
    }}
  ],
  "vocab": [
    {{
      "word": "key word from the article",
      "pos": "n. / v. / adj. / adv.",
      "zh": "繁體中文解釋（簡潔清楚）",
      "example": "A short example sentence for kids."
    }}
  ],
  "questions": [
    {{
      "q": "Reading comprehension question",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": 0,
      "explanation": "用繁體中文溫和清楚地解釋為什麼這個選項正確。"
    }}
  ]
}}

Requirements:
- Exactly 3 paragraphs in `paragraphs`.
- 8 to 10 useful vocabulary words in `vocab` that actually appear in the article.
- Exactly 4 multiple-choice questions in `questions`, `answer` is index 0, 1, 2, or 3.
- Use Traditional Chinese (Taiwan phrasing, e.g., 太空人, 科學家, 資訊, 影片).
"""

    lesson_data = generate_json_with_gemini(api_key, prompt)

    if not image_url:
        backup_query = lesson_data.get("backup_image_query", "")
        wiki_url, wiki_credit = search_wikimedia_photo(backup_query)
        if wiki_url:
            image_url = wiki_url
            image_credit = wiki_credit

    tw_now = datetime.now(timezone(timedelta(hours=8)))
    date_str = tw_now.strftime("%Y-%m-%d")

    final_json = {
        "date": date_str,
        "source_name": chosen["source"],
        "source_url": chosen["link"],
        "title": lesson_data["title"],
        "category": lesson_data.get("category", "Science News"),
        "image_url": image_url,
        "image_caption": lesson_data.get("image_caption", ""),
        "image_caption_zh": lesson_data.get("image_caption_zh", ""),
        "image_credit": image_credit if image_url else "",
        "paragraphs": lesson_data["paragraphs"],
        "vocab": lesson_data["vocab"],
        "questions": lesson_data["questions"],
    }

    os.makedirs("data/archive", exist_ok=True)
    with open("data/today.json", "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)
    with open(f"data/archive/{date_str}.json", "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)

    print(f"🎉 成功產生今日教材！圖片網址: {image_url or '無（前端將自動隱藏圖片框）'}")


if __name__ == "__main__":
    main()
