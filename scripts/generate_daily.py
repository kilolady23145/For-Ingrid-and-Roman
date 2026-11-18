import os
import re
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types

# 國際科學、太空、自然生態與科技突破新聞來源 RSS（純內建讀取，免裝外掛）
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "https://www.sciencedaily.com/rss/top/science.xml",
    "https://www.sciencedaily.com/rss/plants_animals.xml",
    "https://www.nasa.gov/news-release/feed/"
]

def fetch_news_candidates():
    headlines = []
    headers = {'User-Agent': 'Mozilla/5.0 (KidsEnglishReader/2.0)'}
    for url in RSS_FEEDS:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                for item in root.findall('.//item')[:5]:
                    title = item.findtext('title', '')
                    desc = item.findtext('description', '')
                    if title:
                        headlines.append(f"Title: {title}\nSummary: {desc}\n")
        except Exception as e:
            print(f"Warning: Failed to fetch {url}: {e}")
    return "\n---\n".join(headlines[:15])

def get_candidate_models(client):
    """自動向 Google 查詢目前帳號可用的最新 Flash 模型"""
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

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("找不到 GEMINI_API_KEY！請確認已在 GitHub Secrets 設定。")

    news_raw = fetch_news_candidates()
    tw_tz = timezone(timedelta(hours=8))
    today_str = datetime.now(tw_tz).strftime("%Y-%m-%d")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an elite American middle-school science & world-news editor (writing at the caliber of Smithsonian TweenTribune Grade 7–8, NPR Science, and Time Edge) teamed up with an expert bilingual literacy teacher in Taiwan.

From the news candidates below, choose the SINGLE most intellectually fascinating topic (scientific discoveries, space exploration, wildlife behavior, climate solutions, archaeology, or innovative engineering; strictly NO graphic violence, partisan politics, war, or tragic crime).

Write an authentic, thought-provoking feature article calibrated strictly to **US Grade 7–8 native student level (Lexile 1000L–1150L / CEFR B2)**:
- **Length & Structure:** 380 to 480 English words across 4 to 5 well-developed paragraphs (1. Compelling journalistic lead & core discovery; 2. Scientific mechanism or historical context; 3. Deeper inquiry, researcher perspective, or remaining challenges; 4. Broader global significance & forward-looking conclusion).
- **Syntax & Tone:** Use sophisticated yet clear academic prose—incorporating complex sentences, relative clauses, participial phrases, and logical transitions (e.g., "consequently," "nevertheless," "by contrast," "remarkably"). Never talk down to the reader.

Return ONLY valid JSON matching this exact schema:
{{
  "date": "{today_str}",
  "category": "Emoji + Category (e.g., 🔭 Space & Cosmos / 🧬 Science Frontier / 🌍 Planet & Wildlife / 💡 Future Tech)",
  "level": "US Grade 7–8 (Lexile 1050L｜CEFR B2)",
  "title": "Engaging Journalistic English Headline",
  "title_zh": "精準吸睛的台灣繁體中文新聞標題",
  "paragraphs": [
    {{
      "en": "Full US Grade 7-8 English paragraph...",
      "zh": "自然流暢、具科普雜誌質感的台灣繁體中文翻譯..."
    }}
  ],
  "vocabulary": {{
    "exact_lowercase_word_in_article": {{
      "word": "dictionary base form (e.g., phenomenon)",
      "syllables": "syllable breakdown with dots (e.g., phe·nom·e·non)",
      "pos": "詞性 (e.g., n. 名詞 / v. 動詞 / adj. 形容詞 / adv. 副詞)",
      "zh": "貼合本文語境的精準繁體中文意思",
      "explanation": "用清楚易懂的台灣繁體中文解析此學術字彙在文中的核心概念與語感（約 25-40 字）",
      "example": "A natural US Grade 7-8 level English example sentence."
    }}
  }},
  "quiz": [
    {{
      "question": "1. Rigorous US Grade 7-8 reading comprehension question?",
      "options": [
        "A. Well-crafted, plausible option",
        "B. Well-crafted, plausible option",
        "C. Well-crafted, plausible option",
        "D. Well-crafted, plausible option"
      ],
      "answer": 0,
      "explanation": "深度且溫和鼓勵的台灣繁體中文解析：引導學生回到文章線索進行推理，並說明為何此選項最精確。"
    }}
  ]
}}

CRITICAL RULES:
1. Include **12 to 15 Tier-2 academic or key domain words** in `vocabulary`. Each JSON key in `vocabulary` MUST be the **exact lowercase word form as it literally appears in the English paragraphs** (without punctuation) so the frontend word highlighter matches every single one!
2. Create **6 rigorous `quiz` questions** aligned with US Common Core Reading Informational Text (RI.7–8) standards, using smart, non-obvious distractors:
   - Q1: Central Idea & Objective Summary
   - Q2: Textual Evidence & Key Detail
   - Q3: Academic Vocabulary in Context
   - Q4: Logical Inference (drawing conclusions from implicit clues)
   - Q5: Author's Craft / Text Structure (purpose of a specific paragraph, quote, or comparison)
   - Q6: Cause-and-Effect or Scientific Implications
   `answer` MUST be the 0-based integer index (0, 1, 2, or 3).
3. Use Traditional Chinese (Taiwan usage, 台灣繁體中文) for all Chinese text.

News Candidates:
{news_raw}
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
            print(f"⚠️ 模型 {model_name} 無法使用，自動切換下一個 ({e})")
            last_err = e

    if response is None:
        raise RuntimeError(f"所有候選模型皆無法呼叫: {last_err}")

    data = parse_json_safely(response.text)

    os.makedirs("data/archive", exist_ok=True)
    with open("data/today.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(f"data/archive/{today_str}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功產生 {today_str} 的 US Grade 7-8 英文新聞：{data.get('title')}")

if __name__ == "__main__":
    main()
