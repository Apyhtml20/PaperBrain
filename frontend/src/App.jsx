import { useState, useEffect, useRef } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const api = async (endpoint, method = "GET", body = null, token = null) => {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method, headers, body: body ? JSON.stringify(body) : null,
  });
  if (!res.ok) { const err = await res.json(); throw new Error(err.detail || "API Error"); }
  return res.json();
};

// ── TRANSLATIONS ──────────────────────────────────────────────────────────────
const TRANSLATIONS = {
  en: {
    tagline: "Your intelligent study assistant",
    signIn: "Sign in",
    createAccount: "Create account",
    username: "Username",
    email: "Email",
    password: "Password",
    processing: "Processing...",
    chatSubtitle: "Ask anything or explore your documents",
    quizSubtitle: "Test your knowledge",
    flashcardsSubtitle: "Study with smart cards",
    explainSubtitle: "Get clear explanations",
    uploadSubtitle: "Manage your course materials",
    profileSubtitle: "Your learning progress",
    generalChat: "General Chat",
    myDocs: "My Documents (RAG)",
    shiftEnter: "Shift+Enter for new line",
    chatPlaceholderRag: "Ask a question...",
    chatPlaceholder: "Type your message...",
    quizGenerator: "Quiz Generator",
    topic: "Topic",
    topicPlaceholderQuiz: "Enter a topic...",
    questions: "Questions",
    difficulty: "Difficulty",
    easy: "Easy",
    medium: "Medium",
    hard: "Hard",
    startQuiz: "Start Quiz",
    generating: "Generating...",
    result: "Result",
    correct: "Correct",
    wrong: "Wrong",
    time: "Time",
    newQuiz: "New Quiz",
    excellentWork: "Excellent work",
    goodEffort: "Good effort",
    keepStudying: "Keep studying",
    explanation: "Explanation",
    previous: "Previous",
    next: "Next",
    submit: "Submit",
    flashcardGenerator: "Flashcard Generator",
    topicPlaceholderFC: "Enter a topic...",
    generateFlashcards: "Generate Flashcards",
    noFlashcards: "No flashcards generated.",
    newTopic: "New Topic",
    question: "Question",
    answer: "Answer",
    clickReveal: "Click to reveal answer",
    clickQuestion: "Click to see question",
    conceptExplainer: "Concept Explainer",
    concept: "Concept",
    topicPlaceholderExplain: "Enter a concept...",
    level: "Level",
    beginner: "Beginner",
    intermediate: "Intermediate",
    advanced: "Advanced",
    explain: "Explain",
    output: "Output",
    documentManager: "Document Manager",
    subject: "Subject",
    indexingDoc: "Indexing document...",
    chunkingNote: "Chunking + embedding into ChromaDB",
    dragOrClick: "Drag a file or click to upload",
    dropping: "Drop your file here",
    indexedDocs: "Indexed Documents",
    noDocsYet: "No documents yet",
    uploadNote: "Upload your course materials to use RAG in Chat",
    files: "files",
    chunks: "chunks",
    delete: "Delete",
    unsupportedFormat: "Unsupported format. Accepted: PDF, TXT, DOCX",
    sessions: "Sessions",
    quizzes: "Quizzes",
    average: "Average",
    best: "Best",
    quizHistory: "Quiz History",
    memberSince: "Member since",
    dayStreak: "Day streak",
    failedProfile: "Failed to load profile.",
    out: "Out",
    learning: "Learning",
    resources: "Resources",
    noQuestionsGenerated: "No questions generated.",
    nav: { chat: "Chat", quiz: "Quiz", flashcards: "Flashcards", explain: "Explain", upload: "Documents", profile: "Profile" },
  },
  fr: {
    tagline: "Votre assistant d'étude intelligent",
    signIn: "Se connecter",
    createAccount: "Créer un compte",
    username: "Nom d'utilisateur",
    email: "E-mail",
    password: "Mot de passe",
    processing: "Traitement...",
    chatSubtitle: "Posez vos questions ou explorez vos documents",
    quizSubtitle: "Testez vos connaissances",
    flashcardsSubtitle: "Étudiez avec des fiches intelligentes",
    explainSubtitle: "Obtenez des explications claires",
    uploadSubtitle: "Gérez vos supports de cours",
    profileSubtitle: "Votre progression d'apprentissage",
    generalChat: "Chat Général",
    myDocs: "Mes Documents (RAG)",
    shiftEnter: "Maj+Entrée pour nouvelle ligne",
    chatPlaceholderRag: "Posez une question...",
    chatPlaceholder: "Tapez votre message...",
    quizGenerator: "Générateur de Quiz",
    topic: "Sujet",
    topicPlaceholderQuiz: "Entrez un sujet...",
    questions: "Questions",
    difficulty: "Difficulté",
    easy: "Facile",
    medium: "Moyen",
    hard: "Difficile",
    startQuiz: "Démarrer le Quiz",
    generating: "Génération...",
    result: "Résultat",
    correct: "Correct",
    wrong: "Faux",
    time: "Temps",
    newQuiz: "Nouveau Quiz",
    excellentWork: "Excellent travail",
    goodEffort: "Bon effort",
    keepStudying: "Continuez à étudier",
    explanation: "Explication",
    previous: "Précédent",
    next: "Suivant",
    submit: "Soumettre",
    flashcardGenerator: "Générateur de Fiches",
    topicPlaceholderFC: "Entrez un sujet...",
    generateFlashcards: "Générer les Fiches",
    noFlashcards: "Aucune fiche générée.",
    newTopic: "Nouveau Sujet",
    question: "Question",
    answer: "Réponse",
    clickReveal: "Cliquer pour révéler la réponse",
    clickQuestion: "Cliquer pour voir la question",
    conceptExplainer: "Explication de Concept",
    concept: "Concept",
    topicPlaceholderExplain: "Entrez un concept...",
    level: "Niveau",
    beginner: "Débutant",
    intermediate: "Intermédiaire",
    advanced: "Avancé",
    explain: "Expliquer",
    output: "Résultat",
    documentManager: "Gestionnaire de Documents",
    subject: "Matière",
    indexingDoc: "Indexation du document...",
    chunkingNote: "Découpage + intégration dans ChromaDB",
    dragOrClick: "Glissez un fichier ou cliquez pour télécharger",
    dropping: "Déposez votre fichier ici",
    indexedDocs: "Documents Indexés",
    noDocsYet: "Aucun document pour l'instant",
    uploadNote: "Téléchargez vos supports de cours pour utiliser le RAG dans le Chat",
    files: "fichiers",
    chunks: "segments",
    delete: "Supprimer",
    unsupportedFormat: "Format non pris en charge. Acceptés : PDF, TXT, DOCX",
    sessions: "Sessions",
    quizzes: "Quiz",
    average: "Moyenne",
    best: "Meilleur",
    quizHistory: "Historique des Quiz",
    memberSince: "Membre depuis",
    dayStreak: "Jours consécutifs",
    failedProfile: "Échec du chargement du profil.",
    out: "Déco",
    learning: "Apprentissage",
    resources: "Ressources",
    noQuestionsGenerated: "Aucune question générée.",
    nav: { chat: "Chat", quiz: "Quiz", flashcards: "Fiches", explain: "Expliquer", upload: "Documents", profile: "Profil" },
  },
};

const GlobalStyle = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=DM+Serif+Display:ital@0;1&display=swap');
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body, #root { width: 100%; height: 100%; background: #F7F5F0; overflow: hidden; font-family: 'DM Sans', sans-serif; }
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #E7E5E0; border-radius: 4px; }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes bounce { 0%,60%,100% { transform: translateY(0); opacity: 0.4; } 30% { transform: translateY(-4px); opacity: 1; } }
    button:disabled { opacity: 0.4; cursor: not-allowed !important; }
    input, select, textarea, button { font-family: 'DM Sans', sans-serif; }
    .fade-up { animation: fadeUp 0.35s ease forwards; }
  `}</style>
);

const C = {
  bg: "#F7F5F0",
  surface: "#FFFFFF",
  card: "#FFFFFF",
  sidebar: "#1C1917",
  sidebarHover: "#292524",
  sidebarActive: "#292524",
  sidebarText: "#A8A29E",
  sidebarMuted: "#57534E",
  border: "#E7E5E0",
  borderStrong: "#D6D3CD",
  accent: "#C2410C",
  accentMid: "#EA580C",
  accentLight: "#FEF3EC",
  accentBorder: "#FDDCCA",
  text: "#1C1917",
  secondary: "#78716C",
  muted: "#A8A29E",
  green: "#16A34A",
  yellow: "#D97706",
  red: "#DC2626",
  white: "#FFFFFF",
};

// ── LANGUAGE SWITCHER ─────────────────────────────────────────────────────────
const LangSwitcher = ({ lang, setLang }) => (
  <div style={{
    display: "flex", gap: 0,
    border: `1px solid ${C.border}`,
    borderRadius: 6, overflow: "hidden",
    flexShrink: 0,
  }}>
    {["en", "fr"].map(l => (
      <button key={l} onClick={() => setLang(l)} style={{
        padding: "5px 10px",
        fontSize: 11,
        fontWeight: 600,
        letterSpacing: 0.4,
        textTransform: "uppercase",
        border: "none",
        cursor: "pointer",
        background: lang === l ? C.accentMid : "transparent",
        color: lang === l ? C.white : C.muted,
        transition: "all 0.15s",
        fontFamily: "'DM Sans', sans-serif",
      }}>{l}</button>
    ))}
  </div>
);

// ── SHARED COMPONENTS ─────────────────────────────────────────────────────────
const SectionBar = ({ label }) => (
  <div style={{ marginBottom: 24 }}>
    <h3 style={{ fontSize: 13, fontWeight: 600, color: C.muted, letterSpacing: 0.5, textTransform: "uppercase" }}>{label}</h3>
    <div style={{ height: 1, background: C.border, marginTop: 10 }} />
  </div>
);

const Tag = ({ children, color = C.accent }) => (
  <span style={{
    fontSize: 11, fontWeight: 500, color,
    background: color === C.accent ? C.accentLight : `${color}15`,
    border: `1px solid ${color}30`,
    padding: "2px 10px", borderRadius: 20, letterSpacing: 0.3,
  }}>{children}</span>
);

const Spinner = () => (
  <span style={{
    display: "inline-block", width: 15, height: 15,
    border: `2px solid ${C.border}`, borderTopColor: C.accent,
    borderRadius: "50%", animation: "spin 0.7s linear infinite", flexShrink: 0,
  }} />
);

// ── AUTH ──────────────────────────────────────────────────────────────────────
const AuthPage = ({ onLogin, t, lang, setLang }) => {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handle = async () => {
    setError(""); setLoading(true);
    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const body = mode === "login"
        ? { email: form.email, password: form.password }
        : { username: form.username, email: form.email, password: form.password };
      const data = await api(endpoint, "POST", body);
      onLogin(data);
    } catch (e) { setError(e.message); }
    setLoading(false);
  };

  return (
    <><GlobalStyle />
      <div style={{
        width: "100vw", height: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
        backgroundImage: `url('/Background.jpg')`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        position: "fixed", top: 0, left: 0,
      }}>

        {/* Overlay */}
        <div style={{
          position: "absolute", inset: 0,
          background: "rgba(0,0,0,0.35)",
          backdropFilter: "blur(2px)",
        }} />

        {/* Lang switcher top-right */}
        <div style={{ position: "fixed", top: 20, right: 24, display: "flex", gap: 6, alignItems: "center", zIndex: 10 }}>
          <div style={{ display: "flex", border: `1px solid rgba(255,255,255,0.3)`, borderRadius: 6, overflow: "hidden" }}>
            {["en", "fr"].map(l => (
              <button key={l} onClick={() => setLang(l)} style={{
                padding: "5px 10px", fontSize: 11, fontWeight: 600, letterSpacing: 0.4,
                textTransform: "uppercase", border: "none", cursor: "pointer",
                background: lang === l ? C.accentMid : "rgba(255,255,255,0.15)",
                color: "#fff",
                transition: "all 0.15s", fontFamily: "'DM Sans', sans-serif",
              }}>{l}</button>
            ))}
          </div>
        </div>

        {/* Card */}
        <div style={{ width: 420, animation: "fadeUp 0.4s ease", position: "relative", zIndex: 1 }}>
          <div style={{ textAlign: "center", marginBottom: 36 }}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
              <div style={{ width: 36, height: 36, background: C.accent, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
              </div>
              <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24, color: "#fff" }}>Paper<span style={{ color: C.accentMid }}>Brain</span></span>
            </div>
            <p style={{ fontSize: 14, color: "rgba(255,255,255,0.8)" }}>{t.tagline}</p>
          </div>

          <div style={{ background: "rgba(255,255,255,0.95)", border: `1px solid rgba(255,255,255,0.2)`, borderRadius: 16, padding: 36, backdropFilter: "blur(10px)" }}>
            <div style={{ display: "flex", gap: 0, marginBottom: 28, border: `1px solid ${C.border}`, borderRadius: 10, overflow: "hidden" }}>
              {["login", "register"].map(tab => (
                <button key={tab} onClick={() => setMode(tab)} style={{
                  flex: 1, padding: "10px 0", border: "none", cursor: "pointer", fontSize: 13, fontWeight: 500,
                  background: mode === tab ? C.text : "transparent",
                  color: mode === tab ? C.white : C.muted,
                  transition: "all 0.2s",
                }}>
                  {tab === "login" ? t.signIn : t.createAccount}
                </button>
              ))}
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {mode === "register" && (
                <div>
                  <div style={S.label}>{t.username}</div>
                  <input style={{ ...S.input, marginTop: 6 }} placeholder="johndoe"
                    value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
                </div>
              )}
              <div>
                <div style={S.label}>{t.email}</div>
                <input style={{ ...S.input, marginTop: 6 }} type="email" placeholder="john@example.com"
                  value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
              </div>
              <div>
                <div style={S.label}>{t.password}</div>
                <input style={{ ...S.input, marginTop: 6 }} type="password" placeholder="••••••••"
                  value={form.password} onChange={e => setForm({ ...form, password: e.target.value })}
                  onKeyDown={e => e.key === "Enter" && handle()} />
              </div>

              {error && (
                <div style={{ background: "#FEF2F2", border: `1px solid #FECACA`, borderRadius: 8, padding: "10px 14px", fontSize: 13, color: C.red }}>
                  {error}
                </div>
              )}

              <button style={{ ...S.btnPrimary, marginTop: 4 }} onClick={handle} disabled={loading}>
                {loading ? <><Spinner /> {t.processing}</> : mode === "login" ? t.signIn : t.createAccount}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

// ── CHAT ──────────────────────────────────────────────────────────────────────
const ChatPage = ({ token, username, t }) => {
  const [messages, setMessages] = useState([
    { role: "ai", text: `Hello ${username} — PaperBrain is ready.\n\n${t.generalChat}: open questions\nRAG Mode: answers from your uploaded documents` }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("chat");
  const endRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  const handleInput = (e) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
  };

  const send = async () => {
    if (!input.trim() || loading) return;
    const q = input.trim(); setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    setLoading(true);
    setMessages(m => [...m, { role: "user", text: q }]);
    try {
      const endpoint = mode === "rag" ? "/rag-qa" : "/chat";
      const data = await api(endpoint, "POST", { query: q, user_id: username }, token);
      const sources = data.sources?.length > 0 ? `\n\nSources: ${data.sources.join(", ")}` : "";
      setMessages(m => [...m, { role: "ai", text: (data.answer || "No response.") + sources }]);
    } catch (e) {
      setMessages(m => [...m, { role: "ai", text: "Error: " + e.message }]);
    }
    setLoading(false);
  };

  const initials = username?.[0]?.toUpperCase() || "U";

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", maxWidth: 860, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20, flexShrink: 0 }}>
        <span style={{ fontSize: 13, color: C.muted, fontWeight: 500 }}>Mode:</span>
        {[{ id: "chat", label: t.generalChat }, { id: "rag", label: t.myDocs }].map(m => (
          <button key={m.id} onClick={() => setMode(m.id)} style={{
            padding: "7px 18px", cursor: "pointer", fontSize: 13, fontWeight: 500,
            borderRadius: 20, transition: "all 0.15s",
            background: mode === m.id ? C.text : C.surface,
            border: `1px solid ${mode === m.id ? C.text : C.border}`,
            color: mode === m.id ? C.white : C.secondary,
          }}>{m.label}</button>
        ))}
      </div>

      <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 18, paddingBottom: 16 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: "flex", gap: 12, justifyContent: m.role === "user" ? "flex-end" : "flex-start", animation: "fadeUp 0.3s ease" }}>
            {m.role === "ai" && (
              <div style={{ width: 30, height: 30, borderRadius: "50%", background: C.accentLight, border: `1px solid ${C.accentBorder}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 2 }}>
                <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: 13, color: C.accent }}>P</span>
              </div>
            )}
            <div style={{
              maxWidth: "70%", padding: "12px 16px", fontSize: 14, lineHeight: 1.75, whiteSpace: "pre-wrap",
              background: m.role === "user" ? C.text : C.surface,
              border: `1px solid ${m.role === "user" ? "transparent" : C.border}`,
              borderRadius: m.role === "user" ? "12px 4px 12px 12px" : "4px 12px 12px 12px",
              color: m.role === "user" ? C.white : C.text,
            }}>{m.text}</div>
            {m.role === "user" && (
              <div style={{ width: 30, height: 30, borderRadius: "50%", background: C.text, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 2, fontSize: 11, fontWeight: 600, color: C.white }}>
                {initials}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div style={{ display: "flex", gap: 12 }}>
            <div style={{ width: 30, height: 30, borderRadius: "50%", background: C.accentLight, border: `1px solid ${C.accentBorder}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: 13, color: C.accent }}>P</span>
            </div>
            <div style={{ padding: "12px 16px", background: C.surface, border: `1px solid ${C.border}`, borderRadius: "4px 12px 12px 12px", display: "flex", alignItems: "center", gap: 6 }}>
              {[0, 1, 2].map(i => <span key={i} style={{ width: 5, height: 5, borderRadius: "50%", background: C.muted, display: "block", animation: `bounce 1.2s ${i * 0.2}s infinite` }} />)}
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div style={{ paddingTop: 16, borderTop: `1px solid ${C.border}`, flexShrink: 0 }}>
        <div style={{ background: C.surface, border: `1px solid ${C.borderStrong}`, borderRadius: 14, display: "flex", alignItems: "flex-end", gap: 10, padding: "11px 13px", transition: "box-shadow 0.15s" }}>
          <textarea ref={textareaRef} style={{ flex: 1, border: "none", outline: "none", background: "transparent", fontSize: 14, color: C.text, resize: "none", minHeight: 22, maxHeight: 120, lineHeight: 1.6, fontFamily: "'DM Sans', sans-serif" }}
            placeholder={mode === "rag" ? t.chatPlaceholderRag : t.chatPlaceholder}
            value={input} onChange={handleInput} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }} rows={1} />
          <button style={{ width: 34, height: 34, borderRadius: 8, background: input.trim() ? C.text : C.border, border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, transition: "all 0.15s" }}
            onClick={send} disabled={loading || !input.trim()}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </button>
        </div>
        <div style={{ fontSize: 11, color: C.muted, textAlign: "center", marginTop: 8 }}>{t.shiftEnter}</div>
      </div>
    </div>
  );
};

// ── QUIZ ──────────────────────────────────────────────────────────────────────
const QuizPage = ({ token, t }) => {
  const [step, setStep] = useState("config");
  const [config, setConfig] = useState({ topic: "", num_questions: 5, difficulty: "medium" });
  const [questions, setQuestions] = useState([]);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [score, setScore] = useState(null);
  const [startTime, setStartTime] = useState(null);

  const startQuiz = async () => {
    if (!config.topic.trim()) return;
    setLoading(true);
    try {
      const data = await api("/quiz", "POST", config, token);
      setQuestions(data.questions || []);
      setStep("quiz"); setCurrent(0); setAnswers({}); setStartTime(Date.now());
    } catch (e) { alert(e.message); }
    setLoading(false);
  };

  const finish = async () => {
    const correct = questions.filter((q, i) => answers[i] === q.correct_answer).length;
    const scoreVal = Math.round((correct / questions.length) * 100);
    const duration = Math.round((Date.now() - startTime) / 1000);
    setScore({ correct, total: questions.length, value: scoreVal, duration });
    setStep("result");
    try { await api("/quiz/result", "POST", { topic: config.topic, score: scoreVal, total_questions: questions.length, correct_answers: correct, difficulty: config.difficulty, duration_sec: duration }, token); } catch (e) { }
  };

  if (step === "config") return (
    <div style={{ maxWidth: 600, margin: "0 auto" }}>
      <SectionBar label={t.quizGenerator} />
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 14, padding: 32 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div>
            <div style={S.label}>{t.topic}</div>
            <input style={{ ...S.input, marginTop: 6 }} placeholder={t.topicPlaceholderQuiz}
              value={config.topic} onChange={e => setConfig({ ...config, topic: e.target.value })} />
          </div>
          <div style={{ display: "flex", gap: 16 }}>
            <div style={{ flex: 1 }}>
              <div style={S.label}>{t.questions}</div>
              <select style={{ ...S.input, marginTop: 6 }} value={config.num_questions}
                onChange={e => setConfig({ ...config, num_questions: parseInt(e.target.value) })}>
                {[3, 5, 10].map(n => <option key={n} value={n}>{n} {t.questions.toLowerCase()}</option>)}
              </select>
            </div>
            <div style={{ flex: 1 }}>
              <div style={S.label}>{t.difficulty}</div>
              <select style={{ ...S.input, marginTop: 6 }} value={config.difficulty}
                onChange={e => setConfig({ ...config, difficulty: e.target.value })}>
                <option value="easy">{t.easy}</option>
                <option value="medium">{t.medium}</option>
                <option value="hard">{t.hard}</option>
              </select>
            </div>
          </div>
          <button style={S.btnPrimary} onClick={startQuiz} disabled={loading || !config.topic.trim()}>
            {loading ? <><Spinner /> {t.generating}</> : t.startQuiz}
          </button>
        </div>
      </div>
    </div>
  );

  if (step === "quiz") {
    const q = questions[current];
    if (!q) return <div style={{ textAlign: "center", color: C.muted, padding: 40 }}>{t.noQuestionsGenerated}</div>;
    return (
      <div style={{ maxWidth: 720, margin: "0 auto" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
          <span style={{ fontSize: 13, color: C.muted, fontWeight: 500, minWidth: 60 }}>{current + 1} / {questions.length}</span>
          <div style={{ flex: 1, height: 4, background: C.border, borderRadius: 4 }}>
            <div style={{ height: "100%", background: C.accent, borderRadius: 4, width: `${((current + 1) / questions.length) * 100}%`, transition: "width 0.4s" }} />
          </div>
          <Tag>{config.difficulty}</Tag>
        </div>
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 14, padding: 32 }}>
          <p style={{ fontSize: 16, fontWeight: 600, marginBottom: 28, lineHeight: 1.6, color: C.text }}>{q.question}</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 24 }}>
            {(q.options || []).map((opt, i) => {
              const letter = ["A", "B", "C", "D"][i];
              const ua = answers[current];
              let borderColor = C.border, bgColor = "transparent", textColor = C.text;
              if (ua) {
                if (letter === q.correct_answer) { borderColor = C.green; bgColor = "#F0FDF4"; textColor = C.green; }
                else if (letter === ua) { borderColor = C.red; bgColor = "#FEF2F2"; textColor = C.red; }
              }
              return (
                <button key={i} onClick={() => !ua && setAnswers(a => ({ ...a, [current]: letter }))}
                  style={{ display: "flex", alignItems: "center", gap: 14, padding: "14px 18px", background: bgColor, border: `1px solid ${borderColor}`, borderRadius: 10, cursor: ua ? "default" : "pointer", color: textColor, fontSize: 14, textAlign: "left", width: "100%", transition: "all 0.2s" }}>
                  <span style={{ fontSize: 12, fontWeight: 600, color: "inherit", minWidth: 22, height: 22, borderRadius: "50%", border: `1.5px solid currentColor`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>{letter}</span>
                  {opt}
                </button>
              );
            })}
          </div>
          {answers[current] && q.explanation && (
            <div style={{ background: "#F0FDF4", border: `1px solid #BBF7D0`, borderRadius: 10, padding: 16, fontSize: 13, color: "#15803D", marginBottom: 20 }}>
              <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 6, textTransform: "uppercase", letterSpacing: 0.5 }}>{t.explanation}</div>
              {q.explanation}
            </div>
          )}
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
            {current > 0 && <button style={S.btnSecondary} onClick={() => setCurrent(c => c - 1)}>{t.previous}</button>}
            <div style={{ flex: 1 }} />
            {current < questions.length - 1
              ? <button style={S.btnPrimary} onClick={() => setCurrent(c => c + 1)} disabled={!answers[current]}>{t.next}</button>
              : <button style={S.btnPrimary} onClick={finish} disabled={Object.keys(answers).length < questions.length}>{t.submit}</button>
            }
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", justifyContent: "center" }}>
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 16, padding: 48, textAlign: "center", maxWidth: 420, width: "100%" }}>
        <div style={{ fontSize: 13, color: C.muted, fontWeight: 500, letterSpacing: 0.5, textTransform: "uppercase", marginBottom: 20 }}>{t.result}</div>
        <div style={{ fontSize: 72, fontWeight: 700, fontFamily: "'DM Serif Display', serif", color: C.accent, lineHeight: 1, marginBottom: 8 }}>{score.value}<span style={{ fontSize: 28, color: C.muted }}>%</span></div>
        <div style={{ fontSize: 14, fontWeight: 600, color: score.value >= 80 ? C.green : score.value >= 60 ? C.yellow : C.red, marginBottom: 32 }}>
          {score.value >= 80 ? t.excellentWork : score.value >= 60 ? t.goodEffort : t.keepStudying}
        </div>
        <div style={{ display: "flex", justifyContent: "center", gap: 40, marginBottom: 36 }}>
          {[{ l: t.correct, v: score.correct }, { l: t.wrong, v: score.total - score.correct }, { l: t.time, v: `${score.duration}s` }].map((s, i) => (
            <div key={i}>
              <div style={{ fontSize: 26, fontWeight: 700, color: C.text }}>{s.v}</div>
              <div style={{ fontSize: 12, color: C.muted, marginTop: 4 }}>{s.l}</div>
            </div>
          ))}
        </div>
        <button style={S.btnPrimary} onClick={() => setStep("config")}>{t.newQuiz}</button>
      </div>
    </div>
  );
};

// ── FLASHCARDS ────────────────────────────────────────────────────────────────
const FlashcardsPage = ({ token, t }) => {
  const [step, setStep] = useState("config");
  const [topic, setTopic] = useState("");
  const [cards, setCards] = useState([]);
  const [current, setCurrent] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    try {
      const data = await api("/flashcards", "POST", { topic, num_cards: 8 }, token);
      setCards(data.flashcards || []);
      setCurrent(0); setFlipped(false); setStep("study");
    } catch (e) { alert(e.message); }
    setLoading(false);
  };

  if (step === "config") return (
    <div style={{ maxWidth: 600, margin: "0 auto" }}>
      <SectionBar label={t.flashcardGenerator} />
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 14, padding: 32 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <div style={S.label}>{t.topic}</div>
            <input style={{ ...S.input, marginTop: 6 }} placeholder={t.topicPlaceholderFC}
              value={topic} onChange={e => setTopic(e.target.value)} />
          </div>
          <button style={S.btnPrimary} onClick={generate} disabled={loading || !topic.trim()}>
            {loading ? <><Spinner /> {t.generating}</> : t.generateFlashcards}
          </button>
        </div>
      </div>
    </div>
  );

  if (!cards.length) return <div style={{ textAlign: "center", color: C.muted, padding: 40 }}>{t.noFlashcards}</div>;
  const card = cards[current];

  return (
    <div style={{ maxWidth: 640, margin: "0 auto", display: "flex", flexDirection: "column", alignItems: "center", gap: 28 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
        <span style={{ fontSize: 13, color: C.muted }}>{current + 1} / {cards.length}</span>
        <button style={S.btnSecondary} onClick={() => setStep("config")}>{t.newTopic}</button>
      </div>
      <div onClick={() => setFlipped(f => !f)} style={{
        width: "100%", minHeight: 280, cursor: "pointer", transition: "all 0.25s",
        background: flipped ? C.accentLight : C.surface,
        border: `1px solid ${flipped ? C.accentBorder : C.border}`,
        borderRadius: 16, position: "relative", display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <div style={{ padding: 48, textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
          <span style={{ fontSize: 11, fontWeight: 600, color: flipped ? C.accent : C.muted, textTransform: "uppercase", letterSpacing: 1 }}>
            {flipped ? t.answer : t.question}
          </span>
          <p style={{ fontSize: 18, fontWeight: 600, lineHeight: 1.6, color: C.text }}>{flipped ? card.back : card.front}</p>
          <span style={{ fontSize: 12, color: C.muted }}>{flipped ? t.clickQuestion : t.clickReveal}</span>
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        <button style={S.btnSecondary} onClick={() => { setCurrent(c => (c - 1 + cards.length) % cards.length); setFlipped(false); }}>{t.previous}</button>
        <div style={{ display: "flex", gap: 6 }}>
          {cards.map((_, i) => (
            <div key={i} onClick={() => { setCurrent(i); setFlipped(false); }} style={{
              width: i === current ? 20 : 6, height: 6, borderRadius: 3,
              background: i === current ? C.accent : C.border, cursor: "pointer", transition: "all 0.3s",
            }} />
          ))}
        </div>
        <button style={S.btnSecondary} onClick={() => { setCurrent(c => (c + 1) % cards.length); setFlipped(false); }}>{t.next}</button>
      </div>
    </div>
  );
};

// ── EXPLAIN ───────────────────────────────────────────────────────────────────
const ExplainPage = ({ token, t }) => {
  const [concept, setConcept] = useState("");
  const [level, setLevel] = useState("intermediate");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const explain = async () => {
    if (!concept.trim()) return;
    setLoading(true); setResult("");
    try {
      const data = await api("/explain", "POST", { concept, level }, token);
      setResult(data.explanation || "No result.");
    } catch (e) { setResult("Error: " + e.message); }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 760, margin: "0 auto" }}>
      <SectionBar label={t.conceptExplainer} />
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 14, padding: 32, marginBottom: 20 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <div style={S.label}>{t.concept}</div>
            <input style={{ ...S.input, marginTop: 6 }} placeholder={t.topicPlaceholderExplain}
              value={concept} onChange={e => setConcept(e.target.value)} />
          </div>
          <div>
            <div style={S.label}>{t.level}</div>
            <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
              {[{ id: "beginner", l: t.beginner }, { id: "intermediate", l: t.intermediate }, { id: "advanced", l: t.advanced }].map(x => (
                <button key={x.id} onClick={() => setLevel(x.id)} style={{
                  flex: 1, padding: "10px", cursor: "pointer", fontSize: 13, fontWeight: 500, borderRadius: 8,
                  background: level === x.id ? C.text : "transparent",
                  border: `1px solid ${level === x.id ? C.text : C.border}`,
                  color: level === x.id ? C.white : C.secondary, transition: "all 0.15s",
                }}>{x.l}</button>
              ))}
            </div>
          </div>
          <button style={S.btnPrimary} onClick={explain} disabled={loading || !concept.trim()}>
            {loading ? <><Spinner /> {t.generating}</> : t.explain}
          </button>
        </div>
      </div>
      {result && (
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 14, padding: 32 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: C.muted, textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 16 }}>{t.output}</div>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: 14, lineHeight: 1.9, color: C.text, margin: 0, fontFamily: "'DM Sans', sans-serif" }}>{result}</pre>
        </div>
      )}
    </div>
  );
};

// ── UPLOAD ────────────────────────────────────────────────────────────────────
const UploadPage = ({ token, t }) => {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [subject, setSubject] = useState("general");
  const [message, setMessage] = useState(null);
  const fileRef = useRef(null);
  const subjects = ["general", "biology", "chemistry", "physics", "mathematics", "history", "computer science", "languages"];

  useEffect(() => { loadDocs(); }, []);

  const loadDocs = async () => {
    try { const d = await api("/documents", "GET", null, token); setDocuments(d.documents || []); } catch (e) { }
  };

  const uploadFile = async (file) => {
    if (!file) return;
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (![".pdf", ".txt", ".docx"].includes(ext)) { setMessage({ type: "error", text: t.unsupportedFormat }); return; }
    setUploading(true); setMessage(null);
    const fd = new FormData();
    fd.append("file", file); fd.append("subject", subject);
    try {
      const res = await fetch(`${API_BASE}/upload`, { method: "POST", headers: token ? { Authorization: `Bearer ${token}` } : {}, body: fd });
      const d = await res.json();
      if (!res.ok) throw new Error(d.detail || "Upload error");
      setMessage({ type: "success", text: `${d.message} — ${d.chunks} ${t.chunks} indexed` });
      loadDocs();
    } catch (e) { setMessage({ type: "error", text: e.message }); }
    setUploading(false);
  };

  const deleteDoc = async (filename) => {
    if (!window.confirm(`Delete "${filename}"?`)) return;
    try {
      await api(`/documents/${encodeURIComponent(filename)}`, "DELETE", null, token);
      setMessage({ type: "success", text: `"${filename}" deleted` });
      loadDocs();
    } catch (e) { setMessage({ type: "error", text: e.message }); }
  };

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", display: "flex", flexDirection: "column", gap: 20 }}>
      <SectionBar label={t.documentManager} />
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 14, padding: 24 }}>
        <div style={S.label}>{t.subject}</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 10 }}>
          {subjects.map(s => (
            <button key={s} onClick={() => setSubject(s)} style={{
              padding: "5px 14px", cursor: "pointer", fontSize: 12, fontWeight: 500, borderRadius: 20,
              background: subject === s ? C.text : "transparent",
              border: `1px solid ${subject === s ? C.text : C.border}`,
              color: subject === s ? C.white : C.secondary, transition: "all 0.15s",
            }}>{s}</button>
          ))}
        </div>
      </div>

      <div
        style={{ border: `1px dashed ${dragging ? C.accent : C.borderStrong}`, padding: 52, cursor: "pointer", background: dragging ? C.accentLight : C.surface, borderRadius: 14, textAlign: "center", transition: "all 0.2s" }}
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); uploadFile(e.dataTransfer.files[0]); }}
        onClick={() => fileRef.current?.click()}>
        <input ref={fileRef} type="file" accept=".pdf,.txt,.docx" style={{ display: "none" }} onChange={e => uploadFile(e.target.files[0])} />
        {uploading ? (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
            <Spinner />
            <p style={{ fontSize: 14, fontWeight: 500, color: C.accent }}>{t.indexingDoc}</p>
            <p style={{ fontSize: 13, color: C.muted }}>{t.chunkingNote}</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
            <div style={{ width: 44, height: 44, borderRadius: "50%", background: C.accentLight, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={C.accent} strokeWidth="2" strokeLinecap="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            </div>
            <p style={{ fontSize: 14, fontWeight: 600, color: C.text }}>{dragging ? t.dropping : t.dragOrClick}</p>
            <div style={{ display: "flex", gap: 8 }}>
              {["PDF", "TXT", "DOCX"].map(tag => <Tag key={tag}>{tag}</Tag>)}
            </div>
          </div>
        )}
      </div>

      {message && (
        <div style={{ padding: "12px 16px", fontSize: 13, borderRadius: 10, background: message.type === "error" ? "#FEF2F2" : "#F0FDF4", border: `1px solid ${message.type === "error" ? "#FECACA" : "#BBF7D0"}`, color: message.type === "error" ? C.red : C.green }}>
          {message.text}
        </div>
      )}

      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 14, overflow: "hidden" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 20px", borderBottom: `1px solid ${C.border}` }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: C.text }}>{t.indexedDocs}</span>
          <Tag>{documents.length} {t.files}</Tag>
        </div>
        {documents.length === 0 ? (
          <div style={{ padding: 48, textAlign: "center", color: C.muted }}>
            <p style={{ fontSize: 14, fontWeight: 500 }}>{t.noDocsYet}</p>
            <p style={{ fontSize: 13, marginTop: 6 }}>{t.uploadNote}</p>
          </div>
        ) : documents.map((doc, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 16, padding: "14px 20px", borderBottom: `1px solid ${C.border}` }}>
            <div style={{ width: 36, height: 36, borderRadius: 8, background: C.accentLight, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={C.accent} strokeWidth="2" strokeLinecap="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 14, fontWeight: 500, color: C.text }}>{doc.filename}</div>
              <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
                <Tag>{doc.subject}</Tag>
                <span style={{ fontSize: 11, color: C.muted }}>{doc.chunks} {t.chunks}</span>
              </div>
            </div>
            <button onClick={() => deleteDoc(doc.filename)}
              style={{ padding: "6px 14px", background: "transparent", border: `1px solid #FECACA`, borderRadius: 8, color: C.red, cursor: "pointer", fontSize: 12, fontWeight: 500 }}>
              {t.delete}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// ── PROFILE ───────────────────────────────────────────────────────────────────
const ProfilePage = ({ token, t }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api("/profile", "GET", null, token).then(setProfile).catch(console.error).finally(() => setLoading(false));
  }, [token]);

  if (loading) return <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 200 }}><Spinner /></div>;
  if (!profile) return <div style={{ textAlign: "center", padding: 40, color: C.muted }}>{t.failedProfile}</div>;
  const { user, stats, recent_quiz } = profile;

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 14, padding: 32, display: "flex", alignItems: "center", gap: 24 }}>
        <div style={{ width: 64, height: 64, borderRadius: "50%", background: "linear-gradient(135deg, #EA580C, #DC2626)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <span style={{ fontSize: 24, fontWeight: 700, color: C.white }}>{user.username?.[0]?.toUpperCase()}</span>
        </div>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: C.text }}>{user.username}</h2>
          <p style={{ fontSize: 13, color: C.muted, margin: "4px 0 10px" }}>{user.email}</p>
          <Tag>{user.niveau}</Tag>
        </div>
        <div style={{ textAlign: "center", background: C.accentLight, borderRadius: 12, padding: "16px 24px", flexShrink: 0 }}>
          <div style={{ fontSize: 32, fontWeight: 700, fontFamily: "'DM Serif Display', serif", color: C.accent, lineHeight: 1 }}>{user.streak_days}</div>
          <div style={{ fontSize: 12, color: C.secondary, marginTop: 4, fontWeight: 500 }}>{t.dayStreak}</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
        {[{ l: t.sessions, v: stats.total_sessions }, { l: t.quizzes, v: stats.total_quiz }, { l: t.average, v: `${stats.average_score}%` }, { l: t.best, v: `${stats.best_score}%` }].map((s, i) => (
          <div key={i} style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20, textAlign: "center" }}>
            <div style={{ fontSize: 26, fontWeight: 700, fontFamily: "'DM Serif Display', serif", color: C.accent }}>{s.v}</div>
            <div style={{ fontSize: 12, color: C.muted, marginTop: 6 }}>{s.l}</div>
          </div>
        ))}
      </div>

      {recent_quiz?.length > 0 && (
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 14, overflow: "hidden" }}>
          <div style={{ padding: "16px 20px", borderBottom: `1px solid ${C.border}` }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: C.text }}>{t.quizHistory}</span>
          </div>
          {recent_quiz.map((r, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "14px 20px", borderBottom: `1px solid ${C.border}` }}>
              <div>
                <div style={{ fontSize: 14, fontWeight: 500, color: C.text }}>{r.topic}</div>
                <div style={{ fontSize: 12, color: C.muted, marginTop: 4 }}>{r.date} · {r.difficulty}</div>
              </div>
              <div style={{ padding: "4px 16px", fontSize: 14, fontWeight: 700, borderRadius: 20, background: r.score >= 80 ? "#F0FDF4" : r.score >= 60 ? "#FFFBEB" : "#FEF2F2", color: r.score >= 80 ? C.green : r.score >= 60 ? C.yellow : C.red }}>
                {r.score}%
              </div>
            </div>
          ))}
        </div>
      )}
      <div style={{ fontSize: 12, color: C.muted, textAlign: "center" }}>{t.memberSince} {user.member_since}</div>
    </div>
  );
};

// ── MAIN APP ──────────────────────────────────────────────────────────────────
const NAV_ITEMS = [
  { id: "chat",       section: "learning", icon: "M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" },
  { id: "quiz",       section: null,       icon: "M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" },
  { id: "flashcards", section: null,       icon: "M19 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2zM3 9h18" },
  { id: "explain",    section: null,       icon: "M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10zM12 8v4M12 16h.01" },
  { id: "upload",     section: "resources",icon: "M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8" },
  { id: "profile",    section: null,       icon: "M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 3a4 4 0 100 8 4 4 0 000-8z" },
];

const SIDEBAR_W = 210;

export default function App() {
  const [auth, setAuth] = useState(null);
  const [page, setPage] = useState("chat");
  const [lang, setLang] = useState("en");

  const t = TRANSLATIONS[lang];

  if (!auth) return <AuthPage onLogin={setAuth} t={t} lang={lang} setLang={setLang} />;

  const sections = [];
  let current = null;
  for (const item of NAV_ITEMS) {
    if (item.section) { current = { key: item.section, items: [item] }; sections.push(current); }
    else if (current) current.items.push(item);
  }

  const currentPage = NAV_ITEMS.find(p => p.id === page);
  const pageSubtitles = {
    chat: t.chatSubtitle, quiz: t.quizSubtitle, flashcards: t.flashcardsSubtitle,
    explain: t.explainSubtitle, upload: t.uploadSubtitle, profile: t.profileSubtitle,
  };

  return (
    <><GlobalStyle />
      <div style={{ display: "flex", width: "100vw", height: "100vh", background: C.bg, overflow: "hidden", position: "fixed", top: 0, left: 0 }}>

        {/* SIDEBAR */}
        <aside style={{ width: SIDEBAR_W, minWidth: SIDEBAR_W, background: C.sidebar, display: "flex", flexDirection: "column", padding: "24px 0 20px", height: "100vh", flexShrink: 0 }}>

          {/* Logo — sans switcher de langue */}
          <div style={{ padding: "0 18px 22px", borderBottom: `1px solid #292524` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 28, height: 28, background: C.accent, borderRadius: 7, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
              </div>
              <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: 16, color: C.white }}>Paper<span style={{ color: C.accentMid }}>Brain</span></span>
            </div>
          </div>

          <nav style={{ flex: 1, padding: "16px 10px", display: "flex", flexDirection: "column", gap: 2 }}>
            {sections.map(sec => (
              <div key={sec.key}>
                <div style={{ fontSize: 10, letterSpacing: 1, textTransform: "uppercase", color: "#57534E", padding: "10px 10px 5px", fontWeight: 500 }}>
                  {sec.key === "learning" ? t.learning : t.resources}
                </div>
                {sec.items.map(item => (
                  <button key={item.id} onClick={() => setPage(item.id)} style={{
                    display: "flex", alignItems: "center", gap: 9, padding: "9px 10px", borderRadius: 7,
                    color: page === item.id ? C.white : C.sidebarText,
                    background: page === item.id ? "#292524" : "transparent",
                    border: "none", cursor: "pointer", fontSize: 13, fontWeight: page === item.id ? 500 : 400,
                    textAlign: "left", width: "100%", transition: "all 0.15s",
                  }}>
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={page === item.id ? C.accentMid : "currentColor"} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                      <path d={item.icon} />
                    </svg>
                    {t.nav[item.id]}
                  </button>
                ))}
              </div>
            ))}
          </nav>

          {/* User row */}
          <div style={{ padding: "14px 10px 0", borderTop: `1px solid #292524` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 10px" }}>
              <div style={{ width: 28, height: 28, borderRadius: "50%", background: "linear-gradient(135deg,#EA580C,#DC2626)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 600, color: C.white, flexShrink: 0 }}>
                {auth.username?.[0]?.toUpperCase()}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, color: "#E7E5E0", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{auth.username}</div>
              </div>
              <button onClick={() => setAuth(null)} style={{ padding: "4px 8px", background: "transparent", border: `1px solid #333`, borderRadius: 5, color: C.sidebarText, cursor: "pointer", fontSize: 10, fontWeight: 500, flexShrink: 0 }}>
                {t.out}
              </button>
            </div>
          </div>
        </aside>

        {/* MAIN */}
        <main style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", overflow: "hidden", height: "100vh" }}>

          {/* Header avec lang switcher à droite */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "20px 32px 0", flexShrink: 0 }}>
            <div>
              <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24, color: C.text, letterSpacing: -0.5 }}>{t.nav[page]}</div>
              <div style={{ fontSize: 13, color: C.muted, marginTop: 2 }}>{pageSubtitles[page]}</div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <LangSwitcher lang={lang} setLang={setLang} />
              <div style={{ fontSize: 12, color: C.muted, background: C.surface, border: `1px solid ${C.border}`, borderRadius: 20, padding: "5px 14px" }}>
                {new Date().toLocaleDateString(lang === "fr" ? "fr-FR" : "en-US", { weekday: "short", month: "short", day: "numeric" })}
              </div>
            </div>
          </div>

          <div style={{ flex: 1, overflow: "auto", padding: "24px 32px 32px" }}>
            {page === "chat"       && <ChatPage       token={auth.access_token} username={auth.username} t={t} />}
            {page === "quiz"       && <QuizPage       token={auth.access_token} t={t} />}
            {page === "flashcards" && <FlashcardsPage token={auth.access_token} t={t} />}
            {page === "explain"    && <ExplainPage    token={auth.access_token} t={t} />}
            {page === "upload"     && <UploadPage     token={auth.access_token} t={t} />}
            {page === "profile"    && <ProfilePage    token={auth.access_token} t={t} />}
          </div>
        </main>
      </div>
    </>
  );
}

const S = {
  input: {
    padding: "11px 14px", background: C.bg, border: `1px solid ${C.border}`,
    color: C.text, fontSize: 14, outline: "none", width: "100%", borderRadius: 10,
    fontFamily: "'DM Sans', sans-serif", transition: "border-color 0.2s",
  },
  btnPrimary: {
    padding: "12px 24px", background: C.text, border: `1px solid ${C.text}`,
    color: C.white, fontSize: 13, fontWeight: 600, cursor: "pointer", width: "100%",
    borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
    transition: "all 0.15s", fontFamily: "'DM Sans', sans-serif",
  },
  btnSecondary: {
    padding: "10px 20px", background: C.surface, border: `1px solid ${C.border}`,
    color: C.secondary, fontSize: 13, cursor: "pointer", borderRadius: 10,
    fontFamily: "'DM Sans', sans-serif", fontWeight: 500, transition: "all 0.15s",
  },
  label: { fontSize: 12, fontWeight: 600, color: C.muted, letterSpacing: 0.3, textTransform: "uppercase" },
};