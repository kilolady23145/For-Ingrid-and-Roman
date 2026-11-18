import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types

# 1. 國際科學、自然、太空與科技深度新聞來源 RSS
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
    """自動向 Google 查詢目前帳號可用的最新 Flash 文字模型，永遠不怕改版！"""
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
    print("📋 準備依序嘗試的模型清單:", candidates)
    return candidates

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("找不到 GEMINI_API_KEY！請確認已在 GitHub Secrets 設定。")

    news_raw = fetch_news_candidates()
    tw_tz = timezone(timedelta(hours=8))
    today_str = datetime.now(tw_tz).strftime("%Y-%m-%d")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an elite American middle-school journalism editor (writing in the style of Smithsonian TweenTribune Grade 7-8, NPR Science, or Time Edge) paired with an expert bilingual educator in Taiwan.

From the news candidates below, select the SINGLE most intellectually engaging, awe-inspiring topic (science breakthroughs, space exploration, wildlife behavior, climate innovation, archaeology, or technology; strictly NO graphic violence, partisan politics, war, or tragic crime).

Write an authentic, well-structured journalistic feature article calibrated specifically to **US Grade 7–8 native reading level (Lexile 1000L–1150L / CEFR B2)**:
- **Length & Structure:** 380 to 480 English words, organized into 4 or 5 substantial paragraphs (1. Engaging hook & core discovery; 2. How it works / scientific mechanism or context; 3. Deeper nuance, challenges, or researcher perspective; 4. Broader real-world implications & conclusion).
- **Language Quality:** Use varied sentence structures (relative clauses, participial phrases, nuanced transitions like "consequently," "nevertheless," "intriguingly") and rich Tier-2/Tier-3 academic vocabulary—clear and journalistic, never overly childish.

Return ONLY valid JSON matching this exact structure:
{{
  "date": "{today_str}",
  "category": "Emoji + Category Name (e.g., 🔭 Space & Cosmos / 🧬 Science Frontier / 🌍 Planet & Wildlife / 💡 Tech Innovation)",
  "level": "US Grade 7–8 (Lexile 1050L｜CEFR B2)",
  "title": "Compelling Journalistic English Headline",
  "title_zh": "精準吸睛的台灣繁體中文新聞標題",
  "paragraphs": [
    {{
      "en": "Full Grade 7-8 English paragraph...",
      "zh": "自然流暢、符合台灣優質科普雜誌語感的繁體中文段落翻譯..."
    }}
  ],
  "vocabulary": {{
    "exact_lowercase_word_in_article": {{
      "word": "dictionary headword / base form (e.g., resilient)",
      "syllables": "syllable breakdown with dots (e.g., re·sil·ient)",
      "pos": "詞性 (e.g., adj. 形容詞 / v. 動詞 / n. 名詞)",
      "zh": "貼合本文語境的精準繁體中文意思",
      "explanation": "用清楚生動的台灣繁體中文解析這個學術字彙在文章裡的概念與用法（約 25-40 字）",
      "example": "A natural US Grade 7-8 level English example sentence."
    }}
  }},
  "quiz": [
    {{
      "question": "1. Challenging Grade 7-8 reading comprehension question?",
      "options": [
        "A. Plausible, well-phrased option",
        "B. Plausible, well-phrased option",
        "C. Plausible, well-phrased option",
        "D. Plausible, well-phrased option"
      ],
      "answer": 0,
      "explanation": "深度且溫和鼓勵的台灣繁體中文解析：說明正確答案在文中的證據與推理脈絡，並點出誘答選項為何不正確。"
    }}
  ]
}}

CRITICAL RULES:
1. Include **12 to 15 high-value Tier-2 academic or domain key words** in `vocabulary`. IMPORTANT: Each JSON key in `vocabulary` MUST be the **exact lowercase inflected word as it literally appears in the English paragraphs** (without punctuation, e.g., if the text says "researchers hypothesized", the key must be `"hypothesized"` while `"word"` can be `"hypothesize"`) so the webpage's highlighter matches 100% of them!
2. Create **exactly 6 `quiz` questions** aligned with US Grade 7–8 Common Core Reading Informational Text (RI.7-8) standards, with smart distractors (avoid obvious throwaway wrong answers):
   - Q1: Central Idea & Summary
   - Q2: Key Supporting Evidence / Detail
   - Q3: Vocabulary in Context (nuanced meaning of a word/phrase in the passage)
   - Q4: Logical Inference (what can be reasonably inferred though not directly stated)
   - Q5: Author's Purpose or Text Structure (why the author included a specific paragraph/comparison)
   - Q6: Cause-and-Effect or Real-World Application
   `answer` MUST be the 0-based integer index (0, 1, 2, or 3).
3. Use Traditional Chinese (Taiwan usage, 台灣繁體中文) for all Chinese fields.

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
                    temperature=0.65,
                    max_output_tokens=8192
                )
            )
            print(f"🎉 成功使用模型: {model_name}！")
            break
        except Exception as e:
            print(f"⚠️ 模型 {model_name} 無法使用，自動切換下一個 ({e})")
            last_err = e

    if response is None:
        raise RuntimeError(f"所有候選模型皆無法呼叫: {last_err}")

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`").removeprefix("json").strip()

    data = json.loads(raw_text)

    os.makedirs("data/archive", exist_ok=True)
    with open("data/today.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(f"data/archive/{today_str}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功產生 {today_str} 的 US Grade 7-8 進階英文新聞：{data.get('title')}")

if __name__ == "__main__":
    main()
