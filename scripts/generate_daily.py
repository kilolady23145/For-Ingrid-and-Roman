import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types

# 1. 安全正向的新聞來源 RSS (科學、動物、太空、世界趣聞)
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "https://www.sciencedaily.com/rss/plants_animals.xml",
    "https://www.nasa.gov/news-release/feed/"
]

def fetch_news_candidates():
    headlines = []
    headers = {'User-Agent': 'Mozilla/5.0 (KidsEnglishReader/1.0)'}
    for url in RSS_FEEDS:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                for item in root.findall('.//item')[:5]:
                    title = item.findtext('title', '')
                    desc = item.findtext('description', '')
                    if title:
                        headlines.append(f"Title: {title}\nSummary: {desc}\n")
        except Exception as e:
            print(f"Warning: Failed to fetch {url}: {e}")
    return "\n---\n".join(headlines[:12])

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("找不到 GEMINI_API_KEY！請確認已在 GitHub Secrets 設定。")

    news_raw = fetch_news_candidates()
    tw_tz = timezone(timedelta(hours=8))
    today_str = datetime.now(tw_tz).strftime("%Y-%m-%d")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a warm, expert ESL children's news editor in Taiwan.
From the news candidates below, pick the SINGLE most joyful, fascinating, kid-friendly topic (animals, space, nature, cool inventions, or inspiring events; strictly NO violence, politics, war, or disasters).

Rewrite it into an engaging daily English reading article for elementary/junior-high students (CEFR A2 level, around 130-170 words, split into 2 or 3 short paragraphs).

Return ONLY valid JSON matching this exact structure:
{{
  "date": "{today_str}",
  "category": "Emoji + Category Name (e.g., 🚀 Space Explorer / 🐾 Animal World / 🌱 Earth Heroes)",
  "level": "國小高年級 (A2)",
  "title": "Catchy English Title",
  "title_zh": "繁體中文標題",
  "paragraphs": [
    {{
      "en": "English paragraph text...",
      "zh": "自然流暢的台灣繁體中文翻譯..."
    }}
  ],
  "vocabulary": {{
    "exact_lowercase_word_in_article": {{
      "word": "base dictionary form (e.g., discover)",
      "syllables": "syllable breakdown with dots (e.g., dis·cov·er)",
      "pos": "詞性 (e.g., v. 動詞 / n. 名詞 / adj. 形容詞)",
      "zh": "符合本文語境的簡短繁體中文意思",
      "explanation": "用台灣小朋友聽得懂的親切白話文解釋這個字的意思（約 15-25 字）",
      "example": "A simple, kid-friendly English example sentence."
    }}
  }},
  "quiz": [
    {{
      "question": "1. Clear English reading comprehension question?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": 0,
      "explanation": "親切鼓勵的台灣繁體中文解析，說明為什麼選這個答案，幫助孩子理解文章。"
    }}
  ]
}}

CRITICAL RULES:
1. Include 8 to 12 key words in `vocabulary`. Each key in `vocabulary` MUST be the exact lowercase word as it appears in the English paragraphs (without punctuation) so the webpage can highlight it!
2. Create exactly 4 `quiz` questions covering: Main Idea, Detail, Inference, and Vocabulary in Context (aligned with Taiwan elementary reading literacy standards). `answer` is the 0-based index (0, 1, 2, or 3).
3. Use Traditional Chinese (Taiwan usage, 繁體中文) for all Chinese fields.

News Candidates:
{news_raw}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.6
        )
    )

    data = json.loads(response.text)

    os.makedirs("data/archive", exist_ok=True)
    with open("data/today.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(f"data/archive/{today_str}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功產生 {today_str} 的兒童英文新聞：{data.get('title')}")

if __name__ == "__main__":
    main()
