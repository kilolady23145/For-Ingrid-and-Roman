import os
import re
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types

# 國際科學、太空、自然生態與科技新聞 RSS（純內建讀取，免裝 feedparser 絕不報錯！）
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "https://www.nasa.gov/news-release/feed/",
    "https://www.sciencedaily.com/rss/plants_animals.xml",
    "https://www.sciencedaily.com/rss/top/science.xml"
]

# 萬一原新聞剛好沒附圖，依主題自動配上的高畫質無版權科普配圖
FALLBACK_IMAGES = {
    "space": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80",
    "animal": "https://images.unsplash.com/photo-1474511320723-9a56873867b5?auto=format&fit=crop&w=1200&q=80",
    "tech": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
    "science": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1200&q=80"
}

def extract_image_from_item(item, raw_desc=""):
    """從 RSS 項目中搜尋新聞真實配圖（支援 BBC / NASA / 一般 RSS 圖檔標籤）"""
    for elem in item.iter():
        tag = elem.tag.lower()
        if tag.endswith("thumbnail") or tag.endswith("content") or tag.endswith("enclosure"):
            url = elem.attrib.get("url", "")
            mtype = elem.attrib.get("type", "")
            if url.startswith("http") and ("image" in mtype or re.search(r"\.(jpg|jpeg|png|webp)", url, re.I) or "ichef.bbci" in url or "nasa.gov" in url):
                # 把 BBC 縮圖自動放大成高畫質寬圖
                url = re.sub(r"/standard/\d+/", "/standard/976/", url)
                return url
    img_match = re.search(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', raw_desc, re.I)
    if img_match:
        return img_match.group(1)
    return ""

def fetch_news_candidates():
    candidates = []
    headers = {'User-Agent': 'Mozilla/5.0 (KidsEnglishReader/3.0)'}
    idx = 1
    for feed_url in RSS_FEEDS:
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                for item in root.findall('.//item')[:5]:
                    title = (item.findtext('title') or '').strip()
                    desc = (item.findtext('description') or '').strip()
                    link = (item.findtext('link') or '').strip()
                    # 也檢查 content:encoded 裡有沒有圖片
                    encoded = ""
                    for child in item:
                        if child.tag.lower().endswith("encoded") and child.text:
                            encoded = child.text
                    img_url = extract_image_from_item(item, desc + " " + encoded)
                    clean_desc = re.sub(r"<[^>]+>", " ", desc)
                    clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
                    if title:
                        candidates.append({
                            "id": idx,
                            "title": title,
                            "summary": clean_desc[:400],
                            "image_url": img_url,
                            "source_url": link
                        })
                        idx += 1
        except Exception as e:
            print(f"Warning: Failed to fetch {feed_url}: {e}")
    return candidates[:16]

def get_candidate_models(client):
    candidates = ["gemini-3.8-flash", "gemini-flash-latest"]
    skip_words = ("2.5", "2.0", "1.5", "tts", "image", "imagen", "audio", "live", "embedding", "veo")
    try:
        discovered = []
        for m in client.models.list():
            name = (m.name or "").replace("models/", "")
            actions = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", None) or []
            if actions and "generateContent" not in actions:
                continue
            if "gemini" in name and "flash" in name and not any(w in name for w in skip_words):
                discovered.append(name)
        for d in sorted(discovered, reverse=True):
            if d not in candidates:
                candidates.append(d)
    except Exception as e:
        print(f"自動查詢模型清單略過: {e}")
    return candidates

def parse_json_safely(raw_text):
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text)

def pick_fallback_image(category_text, title_text):
    combined = f"{category_text} {title_text}".lower()
    if any(k in combined for k in ("space", "nasa", "planet", "star", "moon", "mars", "galaxy", "cosmos")):
        return FALLBACK_IMAGES["space"]
    if any(k in combined for k in ("animal", "wildlife", "bird", "ocean", "whale", "species", "nature", "forest")):
        return FALLBACK_IMAGES["animal"]
    if any(k in combined for k in ("tech", "robot", "ai", "computer", "engineer", "energy")):
        return FALLBACK_IMAGES["tech"]
    return FALLBACK_IMAGES["science"]

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("找不到 GEMINI_API_KEY！請確認已在 GitHub Secrets 設定。")

    candidates = fetch_news_candidates()
    news_text = "\n---\n".join(
        f"[ID: {c['id']}]\nTitle: {c['title']}\nHasPhoto: {'YES' if c['image_url'] else 'NO'}\nSummary: {c['summary']}"
        for c in candidates
    )

    tw_tz = timezone(timedelta(hours=8))
    today_str = datetime.now(tw_tz).strftime("%Y-%m-%d")
    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an elite American middle-school science & world-news editor (Smithsonian TweenTribune Grade 7–8 / Time Edge style) working with a Taiwan bilingual literacy teacher.

From the news candidates below, select the SINGLE most fascinating, educational story (prefer candidates with HasPhoto: YES when equally interesting; strictly NO graphic violence, war, partisan politics, or crime).

Write an authentic feature article calibrated to **US Grade 7–8 native reading level (Lexile 1000L–1150L / CEFR B2)**:
- **Length & Structure:** 380 to 460 English words across 4 substantial paragraphs (1. Engaging lead & core discovery; 2. Scientific mechanism / context; 3. Researcher insights or challenges; 4. Global significance & conclusion).
- **Syntax & Vocabulary:** Use complex sentences, relative clauses, nuanced transitions, and rich Tier-2 academic vocabulary.

Return ONLY valid JSON matching this exact structure:
{{
  "selected_id": 1,
  "date": "{today_str}",
  "category": "Emoji + Category (e.g., 🔭 Space & Cosmos / 🧬 Science Frontier / 🌍 Planet & Wildlife / 💡 Future Tech)",
  "level": "US Grade 7–8 (Lexile 1050L｜CEFR B2)",
  "title": "Compelling Journalistic English Headline",
  "title_zh": "精準吸睛的台灣繁體中文新聞標題",
  "image_caption": "A concise 1-sentence English caption + 繁體中文圖說 describing the story's visual theme.",
  "paragraphs": [
    {{
      "en": "Full US Grade 7-8 English paragraph...",
      "zh": "自然流暢的台灣繁體中文段落翻譯..."
    }}
  ],
  "vocabulary": {{
    "exact_lowercase_word_in_article": {{
      "word": "dictionary base form",
      "syllables": "syl·la·ble",
      "pos": "詞性 (e.g., n. 名詞 / v. 動詞 / adj. 形容詞)",
      "zh": "精準繁體中文意思",
      "explanation": "用台灣繁體中文解析此學術字彙在文中的概念與用法（約 25-35 字）",
      "example": "A natural US Grade 7-8 English example sentence."
    }}
  }},
  "quiz": [
    {{
      "question": "1. Rigorous US Grade 7-8 reading comprehension question?",
      "options": [
        "A. Plausible option",
        "B. Plausible option",
        "C. Plausible option",
        "D. Plausible option"
      ],
      "answer": 0,
      "explanation": "溫和清楚的台灣繁體中文解析，說明正確答案的文本證據與推理。"
    }}
  ]
}}

CRITICAL RULES:
1. `selected_id` MUST match the integer ID of the news candidate you chose.
2. Include **12 to 15 Tier-2 academic words** in `vocabulary`. Each JSON key MUST be the **exact lowercase word form appearing in `paragraphs`**.
3. Create **6 `quiz` questions** (Central Idea, Evidence, Vocabulary in Context, Inference, Text Structure/Purpose, Cause & Effect). `answer` MUST be 0, 1, 2, or 3.
4. Use Traditional Chinese (Taiwan usage, 台灣繁體中文) for all Chinese fields.

News Candidates:
{news_text}
"""

    response = None
    last_err = None
    for model_name in get_candidate_models(client):
        try:
            print(f"🚀 嘗試使用模型: {model_name} ...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.65
                )
            )
            print(f"🎉 成功使用模型: {model_name}！")
            break
        except Exception as e:
            print(f"⚠️ 模型 {model_name} 無法使用 ({e})")
            last_err = e

    if response is None:
        raise RuntimeError(f"所有候選模型皆失敗: {last_err}")

    data = parse_json_safely(response.text)

    # 自動把選中新聞的真實圖片與原文連結掛上去（若無圖則自動補上高畫質科普圖）
    chosen_id = data.get("selected_id")
    matched = next((c for c in candidates if c["id"] == chosen_id), None)
    real_img = matched["image_url"] if (matched and matched.get("image_url")) else ""
    data["image_url"] = real_img or pick_fallback_image(data.get("category", ""), data.get("title", ""))
    data["source_url"] = matched["source_url"] if matched else ""

    os.makedirs("data/archive", exist_ok=True)
    with open("data/today.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(f"data/archive/{today_str}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功產生 {today_str} 新聞：{data.get('title')} | 圖片：{data.get('image_url')}")

if __name__ == "__main__":
    main()
