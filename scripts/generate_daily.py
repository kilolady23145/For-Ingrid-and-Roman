<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ingrid & Roman's Daily English News</title>
  <style>
    :root {
      --bg: #f4f7fb;
      --card: #ffffff;
      --primary: #2563eb;
      --primary-light: #dbeafe;
      --accent: #f59e0b;
      --text: #1e293b;
      --muted: #64748b;
      --success: #16a34a;
      --danger: #dc2626;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans TC", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.7;
      padding-bottom: 60px;
    }
    header {
      background: linear-gradient(135deg, #1d4ed8, #3b82f6);
      color: white;
      padding: 24px 20px;
      text-align: center;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
    }
    header h1 { margin: 0; font-size: 1.55rem; letter-spacing: 0.3px; }
    header p { margin: 6px 0 0; opacity: 0.92; font-size: 0.95rem; }

    .container { max-width: 820px; margin: 22px auto; padding: 0 16px; }
    .card {
      background: var(--card);
      border-radius: 18px;
      padding: 24px;
      margin-bottom: 20px;
      box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
    }
    .meta-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      margin-bottom: 12px;
      font-size: 0.88rem;
      color: var(--muted);
    }
    .badge {
      background: var(--primary-light);
      color: var(--primary);
      font-weight: 700;
      padding: 4px 12px;
      border-radius: 999px;
    }
    h2.article-title {
      margin: 6px 0 16px;
      font-size: 1.55rem;
      line-height: 1.35;
      color: #0f172a;
    }

    /* 新聞真實圖片區塊 */
    .news-figure {
      margin: 0 0 20px 0;
      border-radius: 14px;
      overflow: hidden;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
    }
    .news-figure img {
      width: 100%;
      max-height: 430px;
      object-fit: cover;
      display: block;
    }
    .news-caption {
      padding: 10px 14px;
      font-size: 0.9rem;
      color: #334155;
      background: #f8fafc;
      line-height: 1.45;
    }
    .news-caption .cap-zh {
      display: block;
      color: var(--muted);
      font-size: 0.84rem;
      margin-top: 3px;
    }
    .news-credit {
      display: block;
      font-size: 0.76rem;
      color: #94a3b8;
      margin-top: 4px;
    }

    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 18px;
    }
    button.btn {
      border: none;
      background: var(--primary);
      color: white;
      padding: 9px 15px;
      border-radius: 10px;
      font-size: 0.92rem;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.1s, opacity 0.2s;
    }
    button.btn.secondary {
      background: #e2e8f0;
      color: #1e293b;
    }
    button.btn:active { transform: scale(0.98); }

    .tip-box {
      background: #fffbeb;
      border-left: 4px solid var(--accent);
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 0.9rem;
      color: #92400e;
      margin-bottom: 18px;
    }

    .para-block { margin-bottom: 18px; }
    .para-en { font-size: 1.14rem; line-height: 1.85; margin: 0; }
    .para-zh {
      margin: 8px 0 0;
      padding: 10px 14px;
      background: #f8fafc;
      border-radius: 10px;
      color: #475569;
      font-size: 0.96rem;
      display: none;
    }
    .show-zh .para-zh { display: block; }

    .word-token {
      cursor: pointer;
      border-radius: 4px;
      padding: 0 2px;
      transition: background 0.15s;
    }
    .word-token:hover { background: #dbeafe; }
    .word-token.is-vocab {
      border-bottom: 2px dotted var(--primary);
      font-weight: 500;
    }

    /* 單字卡區塊 */
    .vocab-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 12px;
    }
    .vocab-item {
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 12px 14px;
      background: #fcfdff;
    }
    .vocab-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 700;
      color: var(--primary);
      font-size: 1.05rem;
    }
    .speak-mini {
      background: var(--primary-light);
      color: var(--primary);
      border: none;
      border-radius: 8px;
      padding: 4px 8px;
      cursor: pointer;
      font-size: 0.85rem;
    }

    /* 測驗區塊 */
    .q-block {
      margin-bottom: 22px;
      padding-bottom: 18px;
      border-bottom: 1px solid #f1f5f9;
    }
    .q-title { font-weight: 700; margin-bottom: 10px; font-size: 1.05rem; }
    .opt-btn {
      display: block;
      width: 100%;
      text-align: left;
      margin-bottom: 8px;
      padding: 11px 14px;
      border: 1.5px solid #cbd5e1;
      border-radius: 10px;
      background: white;
      font-size: 0.98rem;
      cursor: pointer;
    }
    .opt-btn.correct { background: #dcfce7; border-color: var(--success); color: #14532d; font-weight: 600; }
    .opt-btn.wrong { background: #fee2e2; border-color: var(--danger); color: #7f1d1d; }
    .q-exp {
      display: none;
      margin-top: 8px;
      padding: 10px 12px;
      background: #f0fdf4;
      border-radius: 8px;
      font-size: 0.92rem;
      color: #166534;
    }

    /* 點字彈出視窗 */
    #wordModal {
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      width: min(92vw, 430px);
      background: #0f172a;
      color: white;
      border-radius: 16px;
      padding: 16px 18px;
      box-shadow: 0 12px 30px rgba(0,0,0,0.28);
      display: none;
      z-index: 999;
    }
    #wordModal .close-btn {
      float: right;
      background: transparent;
      border: none;
      color: #94a3b8;
      font-size: 1.2rem;
      cursor: pointer;
    }
  </style>
</head>
<body>

<header>
  <h1>🌍 Ingrid & Roman's Daily News</h1>
  <p>每天 15 分鐘，看真實世界新聞學英文！</p>
</header>

<div class="container">
  <div class="card" id="articleCard">
    <div class="meta-bar">
      <span class="badge" id="catBadge">Loading...</span>
      <span id="dateText"></span>
      <span id="sourceText"></span>
    </div>

    <h2 class="article-title" id="articleTitle">正在載入今天的新聞...</h2>

    <!-- 新聞真實照片框（有照片才顯示，載入失敗自動隱藏防破圖） -->
    <figure class="news-figure" id="newsFigure" style="display: none;">
      <img id="newsImage" alt="Daily news photo" referrerpolicy="no-referrer" />
      <figcaption class="news-caption" id="newsCaptionBox">
        <span id="newsCaptionEn"></span>
        <span class="cap-zh" id="newsCaptionZh"></span>
        <span class="news-credit" id="newsCredit"></span>
      </figcaption>
    </figure>

    <div class="toolbar">
      <button class="btn" onclick="speakArticle(0.92)">🔊 朗讀全文</button>
      <button class="btn secondary" onclick="speakArticle(0.75)">🐢 慢速朗讀</button>
      <button class="btn secondary" onclick="stopSpeak()">⏹️ 停止</button>
      <button class="btn secondary" onclick="toggleZh()">🈶 顯示 / 隱藏中文翻譯</button>
    </div>

    <div class="tip-box">
      💡 <strong>小提示：</strong>文章裡有底線的是今日重點單字；遇到<strong>任何不認識的字</strong>，直接點它就能聽發音、看中文意思喔！
    </div>

    <div id="paragraphsBox"></div>
  </div>

  <div class="card">
    <h3>📚 今日重點單字 (Key Vocabulary)</h3>
    <div class="vocab-grid" id="vocabBox"></div>
  </div>

  <div class="card">
    <h3>🧠 閱讀理解挑戰 (Reading Quiz)</h3>
    <div id="quizBox"></div>
    <div id="scoreBox" style="font-weight:700; font-size:1.1rem; color:var(--primary);"></div>
  </div>
</div>

<div id="wordModal">
  <button class="close-btn" onclick="document.getElementById('wordModal').style.display='none'">✕</button>
  <div style="font-size:1.25rem; font-weight:700;" id="mWord">word</div>
  <div style="font-size:0.9rem; color:#93c5fd; margin:4px 0;" id="mPos"></div>
  <div style="font-size:1rem; margin:6px 0;" id="mMeaning">查詢中...</div>
  <div style="margin-top:10px; display:flex; gap:8px;">
    <button class="btn" style="padding:6px 12px; font-size:0.85rem;" id="mSpeakBtn">🔊 美式發音</button>
    <button class="btn secondary" style="padding:6px 12px; font-size:0.85rem;" id="mSlowBtn">🐢 慢速</button>
  </div>
</div>

<script>
  let lesson = null;
  let vocabMap = {};
  let answeredCount = 0;
  let correctCount = 0;
  let dictAudioUrl = "";

  async function loadLesson() {
    const res = await fetch('./data/today.json?t=' + Date.now());
    lesson = await res.json();

    document.getElementById('catBadge').textContent = lesson.category || 'Daily News';
    document.getElementById('dateText').textContent = '📅 ' + (lesson.date || '');
    if (lesson.source_name) {
      const srcEl = document.getElementById('sourceText');
      if (lesson.source_url) {
        srcEl.innerHTML = `📰 來源：<a href="${lesson.source_url}" target="_blank" rel="noopener" style="color:#2563eb;text-decoration:none;">${lesson.source_name}</a>`;
      } else {
        srcEl.textContent = '📰 來源：' + lesson.source_name;
      }
    }
    document.getElementById('articleTitle').textContent = lesson.title;

    // 處理真實新聞圖片顯示與防破圖
    const fig = document.getElementById('newsFigure');
    const img = document.getElementById('newsImage');
    if (lesson.image_url) {
      img.onerror = () => { fig.style.display = 'none'; };
      img.onload = () => { fig.style.display = 'block'; };
      img.src = lesson.image_url;

      document.getElementById('newsCaptionEn').textContent = lesson.image_caption || '';
      document.getElementById('newsCaptionZh').textContent = lesson.image_caption_zh || '';
      document.getElementById('newsCredit').textContent = lesson.image_credit ? `📷 ${lesson.image_credit}` : '';
    } else {
      fig.style.display = 'none';
    }

    // 建立重點單字索引
    vocabMap = {};
    (lesson.vocab || []).forEach(v => {
      vocabMap[v.word.toLowerCase()] = v;
    });

    // 渲染文章段落（每個單字可點擊）
    const pBox = document.getElementById('paragraphsBox');
    pBox.innerHTML = '';
    (lesson.paragraphs || []).forEach(p => {
      const block = document.createElement('div');
      block.className = 'para-block';

      const pEn = document.createElement('p');
      pEn.className = 'para-en';
      pEn.innerHTML = tokenizeParagraph(p.en);

      const pZh = document.createElement('p');
      pZh.className = 'para-zh';
      pZh.textContent = p.zh;

      block.appendChild(pEn);
      block.appendChild(pZh);
      pBox.appendChild(block);
    });

    // 渲染單字卡
    const vBox = document.getElementById('vocabBox');
    vBox.innerHTML = '';
    (lesson.vocab || []).forEach(v => {
      const item = document.createElement('div');
      item.className = 'vocab-item';
      item.innerHTML = `
        <div class="vocab-head">
          <span>${v.word} <small style="color:#64748b;font-weight:400;">${v.pos || ''}</small></span>
          <button class="speak-mini" onclick="speakWord('${v.word.replace(/'/g, "\\'")}', 0.9)">🔊</button>
        </div>
        <div style="margin-top:4px;font-weight:600;">${v.zh}</div>
        <div style="margin-top:4px;font-size:0.86rem;color:#64748b;">${v.example || ''}</div>
      `;
      vBox.appendChild(item);
    });

    // 渲染閱讀測驗
    const qBox = document.getElementById('quizBox');
    qBox.innerHTML = '';
    answeredCount = 0;
    correctCount = 0;
    (lesson.questions || []).forEach((q, qIdx) => {
      const qb = document.createElement('div');
      qb.className = 'q-block';
      const title = document.createElement('div');
      title.className = 'q-title';
      title.textContent = `${qIdx + 1}. ${q.q}`;
      qb.appendChild(title);

      const exp = document.createElement('div');
      exp.className = 'q-exp';
      exp.textContent = '💡 ' + q.explanation;

      q.options.forEach((opt, oIdx) => {
        const btn = document.createElement('button');
        btn.className = 'opt-btn';
        btn.textContent = `${String.fromCharCode(65 + oIdx)}. ${opt}`;
        btn.onclick = () => checkAnswer(qb, btn, oIdx, q.answer, exp, lesson.questions.length);
        qb.appendChild(btn);
      });

      qb.appendChild(exp);
      qBox.appendChild(qb);
    });
  }

  function tokenizeParagraph(text) {
    return text.replace(/([A-Za-z]+(?:'[A-Za-z]+)?)/g, (match) => {
      const lower = match.toLowerCase();
      const isVocab = vocabMap[lower] || vocabMap[lower.replace(/s$|ed$|ing$/, '')];
      const cls = isVocab ? 'word-token is-vocab' : 'word-token';
      const safe = match.replace(/'/g, "\\'");
      return `<span class="${cls}" onclick="lookupWord('${safe}')">${match}</span>`;
    });
  }

  function checkAnswer(qb, clickedBtn, chosen, ans, expEl, total) {
    if (qb.dataset.done) return;
    qb.dataset.done = '1';
    const buttons = qb.querySelectorAll('.opt-btn');
    buttons[ans].classList.add('correct');
    if (chosen === ans) {
      correctCount++;
    } else {
      clickedBtn.classList.add('wrong');
    }
    expEl.style.display = 'block';
    answeredCount++;
    if (answeredCount === total) {
      document.getElementById('scoreBox').textContent = `🎉 完成今日挑戰！得分：${correctCount} / ${total}`;
    }
  }

  function toggleZh() {
    document.getElementById('articleCard').classList.toggle('show-zh');
  }

  function speakTextWithTTS(text, rate = 0.9) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'en-US';
    utter.rate = rate;
    const voices = window.speechSynthesis.getVoices();
    const usVoice = voices.find(v => v.lang === 'en-US' && /Samantha|Ava|Alex|Google US/i.test(v.name))
                 || voices.find(v => v.lang === 'en-US');
    if (usVoice) utter.voice = usVoice;
    window.speechSynthesis.speak(utter);
  }

  function speakWord(word, rate = 0.9) {
    // 若字典 API 有提供真人錄音 mp3 且為正常語速，優先播放真人 mp3（對手機相容性更友善）
    if (dictAudioUrl && rate >= 0.85) {
      const audio = new Audio(dictAudioUrl);
      audio.play().catch(() => speakTextWithTTS(word, rate));
      return;
    }
    speakTextWithTTS(word, rate);
  }

  function speakArticle(rate) {
    if (!lesson) return;
    const fullText = lesson.title + '. ' + lesson.paragraphs.map(p => p.en).join(' ');
    speakTextWithTTS(fullText, rate);
  }

  function stopSpeak() {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  }

  async function lookupWord(word) {
    const modal = document.getElementById('wordModal');
    const mWord = document.getElementById('mWord');
    const mPos = document.getElementById('mPos');
    const mMeaning = document.getElementById('mMeaning');
    dictAudioUrl = "";

    modal.style.display = 'block';
    mWord.textContent = word;
    mPos.textContent = '';
    mMeaning.textContent = '查詢中...';

    document.getElementById('mSpeakBtn').onclick = () => speakWord(word, 0.92);
    document.getElementById('mSlowBtn').onclick = () => speakTextWithTTS(word, 0.65);

    const lower = word.toLowerCase();
    const hit = vocabMap[lower] || vocabMap[lower.replace(/s$|ed$|ing$/, '')];

    // 嘗試向免費字典抓真人發音 mp3 與音標
    try {
      const dRes = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(lower)}`);
      if (dRes.ok) {
        const dJson = await dRes.json();
        const phonetics = dJson[0]?.phonetics || [];
        const usAudio = phonetics.find(p => p.audio && p.audio.includes('-us')) || phonetics.find(p => p.audio);
        if (usAudio?.audio) dictAudioUrl = usAudio.audio;
        const phoneticText = dJson[0]?.phonetic || phonetics.find(p => p.text)?.text || '';
        if (phoneticText) mPos.textContent = phoneticText;
      }
    } catch (e) {}

    speakWord(word, 0.92);

    if (hit) {
      mPos.textContent = (mPos.textContent ? mPos.textContent + ' · ' : '') + (hit.pos || '');
      mMeaning.textContent = hit.zh;
      return;
    }

    try {
      const tRes = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(lower)}&langpair=en|zh-TW`);
      const tJson = await tRes.json();
      mMeaning.textContent = tJson?.responseData?.translatedText || '請參考上下文理解字義';
    } catch (e) {
      mMeaning.textContent = '目前無法連線翻譯服務';
    }
  }

  loadLesson();
</script>
</body>
</html>
