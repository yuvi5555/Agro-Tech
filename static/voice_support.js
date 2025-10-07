// Supported languages (lang code + display name)
const supportedLanguages = {
  "en-US": "English",
  "hi-IN": "हिंदी",
  "mr-IN": "मराठी",
};

// Function to translate text using Google Translate API
async function translateText(text, targetLang) {
  try {
    const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=${targetLang}&dt=t&q=${encodeURIComponent(text)}`;
    const response = await fetch(url);
    const result = await response.json();

    // Extract translated text
    let translatedText = "";
    if (Array.isArray(result) && Array.isArray(result[0])) {
      result[0].forEach((item) => {
        if (item[0]) translatedText += item[0];
      });
    }
    return translatedText || text;
  } catch (err) {
    console.error("Translation API Error:", err);
    return text;
  }
}

// Function to play text using gTTS via Django backend
function speakWithGTTS(text, lang) {
  let gttsLang = "en";
  if (lang === "hi-IN") gttsLang = "hi";
  if (lang === "mr-IN") gttsLang = "mr";

  const urlText = encodeURIComponent(text);
  const audioUrl = `/tts_audio/?text=${urlText}&lang=${gttsLang}`;

  const audio = new Audio(audioUrl);
  audio.play();
}

// -----------------------------
// Create floating voice button
// -----------------------------
const btn = document.createElement("button");
btn.innerHTML = "🔊 Voice";
btn.style.position = "fixed";
btn.style.bottom = "20px";
btn.style.right = "20px";
btn.style.padding = "12px 16px";
btn.style.borderRadius = "50%";
btn.style.background = "#007BFF";
btn.style.color = "white";
btn.style.border = "none";
btn.style.cursor = "pointer";
btn.style.zIndex = "9999";
btn.title = "Click to select language and hear text";
document.body.appendChild(btn);

// -----------------------------
// Create language modal
// -----------------------------
const modal = document.createElement("div");
modal.style.position = "fixed";
modal.style.bottom = "80px";
modal.style.right = "20px";
modal.style.padding = "15px 20px";
modal.style.background = "white";
modal.style.border = "2px solid #007BFF";
modal.style.borderRadius = "10px";
modal.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
modal.style.zIndex = "10000";
modal.style.display = "none";

// Dropdown
const langSelect = document.createElement("select");
langSelect.style.padding = "8px";
langSelect.style.marginBottom = "10px";
langSelect.style.fontSize = "14px";
langSelect.style.width = "100%";
langSelect.style.borderRadius = "5px";
langSelect.style.border = "1px solid #007BFF";

for (let code in supportedLanguages) {
  const option = document.createElement("option");
  option.value = code;
  option.textContent = supportedLanguages[code];
  langSelect.appendChild(option);
}
modal.appendChild(langSelect);

// Translate & Read button
const speakBtn = document.createElement("button");
speakBtn.textContent = "Translate & Read";
speakBtn.style.padding = "8px 12px";
speakBtn.style.marginTop = "10px";
speakBtn.style.background = "#28a745";
speakBtn.style.color = "white";
speakBtn.style.border = "none";
speakBtn.style.borderRadius = "5px";
speakBtn.style.cursor = "pointer";
speakBtn.style.width = "100%";
modal.appendChild(speakBtn);

// Close button
const closeBtn = document.createElement("button");
closeBtn.textContent = "Close";
closeBtn.style.padding = "8px 12px";
closeBtn.style.marginTop = "10px";
closeBtn.style.background = "#dc3545";
closeBtn.style.color = "white";
closeBtn.style.border = "none";
closeBtn.style.borderRadius = "5px";
closeBtn.style.cursor = "pointer";
closeBtn.style.width = "100%";
modal.appendChild(closeBtn);

document.body.appendChild(modal);

// -----------------------------
// Button events
// -----------------------------
btn.addEventListener("click", () => {
  modal.style.display = modal.style.display === "none" ? "block" : "none";
});

closeBtn.addEventListener("click", () => {
  modal.style.display = "none";
});

speakBtn.addEventListener("click", async () => {
  const text = document.body.innerText;
  const lang = langSelect.value;

  let targetLang = "en";
  if (lang === "hi-IN") targetLang = "hi";
  if (lang === "mr-IN") targetLang = "mr";

  const translatedText = await translateText(text, targetLang);
  speakWithGTTS(translatedText, lang);
});
