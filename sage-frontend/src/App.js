import React, { useState, useEffect, useRef } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMessage = { from: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    setTyping(true);

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage.text }),
      });

      const data = await response.json();
      const botMessage = {
        from: "bot",
        text: data.answer || "⚠️ No response from backend",
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "❌ Backend not running or unreachable." },
      ]);
    }

    setTyping(false);
  }

  const quickQuestions = [
    "What are the library hours?",
    "What facilities are available on campus?",
    "What clubs are available?",
    "What is the hostel fee?",
    "Tell me about placements",
  ];

  return (
    <div style={styles.page}>

      {/* LEFT QUICK QUESTION PANEL */}
      <div style={styles.leftPanel}>
        <h3 style={{ marginBottom: 10 }}>📌 Quick Links</h3>
        {quickQuestions.map((q, i) => (
          <button
            key={i}
            style={styles.quickButton}
            onClick={() =>
              setMessages((prev) => [...prev, { from: "user", text: q }])
            }
          >
            {q}
          </button>
        ))}
      </div>

      {/* CHAT WINDOW */}
      <div style={styles.chatContainer}>
        <div style={styles.header}>
          <img src="/ptu-logo.png" alt="logo" style={{ width: 40, marginRight: 10 }} />
          <h2>SAGE University Assistant</h2>
        </div>

        <div style={styles.messagesBox}>
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                ...styles.messageBubble,
                alignSelf: msg.from === "user" ? "flex-end" : "flex-start",
                background: msg.from === "user" ? "#276ef1" : "#f1f1f1",
                color: msg.from === "user" ? "white" : "black",
              }}
            >
              {msg.text}
            </div>
          ))}

          {typing && (
            <div style={styles.typingBubble}>
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div style={styles.inputRow}>
          <input
            style={styles.input}
            placeholder="Ask anything about admissions, academics, clubs, fees..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button style={styles.button} onClick={sendMessage}>Send</button>
        </div>
      </div>

     {/* RIGHT PANEL – COLLEGE INFO */}
<div style={styles.rightPanel}>
  <h3 style={styles.panelTitle}>📘 College Info</h3>

  <p style={styles.infoLine}>🏫 <b>Campus:</b> Pondicherry Technological University</p>
  <p style={styles.infoLine}>🎓 <b>Programs:</b> B.Tech, M.Tech, MBA, MCA, PhD</p>
  <p style={styles.infoLine}>📚 <b>Departments:</b> CSE, ECE, EEE, Mechanical, Civil, IT, Chemical</p>
  <p style={styles.infoLine}>👨‍🏫 <b>Faculty:</b> 120+ Professors & Research Scholars</p>
  <p style={styles.infoLine}>📅 <b>Working Days:</b> Monday – Saturday</p>
  <p style={styles.infoLine}>⏰ <b>Office Hours:</b> 9:00 AM – 5:00 PM</p>
</div>


      {/* FLOATING HELP BUTTON */}
      <div
  style={styles.helpBtn}
  onClick={() => alert("This is SAGE University Assistant.\nAsk anything about academics, fees, admissions, clubs!") }

>
  ❓ Help / About
</div>


      {/* Typing animation CSS */}
      <style>
        {`
          .dot {
            height: 8px;
            width: 8px;
            margin: 0 3px;
            background-color: #ccc;
            border-radius: 50%;
            display: inline-block;
            animation: bounce 1.4s infinite ease-in-out both;
          }

          .dot:nth-child(1) { animation-delay: -0.32s; }
          .dot:nth-child(2) { animation-delay: -0.16s; }

          @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
          }
        `}
      </style>
    </div>
  );
}

// ---------------- STYLES ----------------
const styles = {
  page: {
    background: "#05c8f9",
    height: "100vh",
    width: "100vw",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    gap: "20px",
  },

  leftPanel: {
    width: "180px",
    height: "650px",
    background: "#05c8f9",
    borderRadius: "12px",
    padding: "15px",
    boxShadow: "0px 0px 15px rgba(0,0,0,0.2)",
  },

  quickButton: {
    width: "100%",
    padding: "10px",
    borderRadius: "8px",
    marginBottom: "10px",
    background: "#f1f1f1",
    border: "1px solid #ccc",
    cursor: "pointer",
  },

  chatContainer: {
    width: "850px",
    height: "650px",
    borderRadius: "15px",
    boxShadow: "0px 0px 25px rgba(0,0,0,0.15)",
    padding: "20px",
    display: "flex",
    flexDirection: "column",

    /* --- WATERMARK LOGO --- */
    backgroundImage: "url('/ptu-logo.png')",
    backgroundRepeat: "no-repeat",
    backgroundPosition: "center",
    backgroundSize: "300px",

    /* --- LIGHT BACKGROUND COLOR --- */
    backgroundColor: "rgba(248, 229, 229, 0.85)",
},



  header: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 10,
    borderBottom: "1px solid #ccc",
    paddingBottom: 10,
  },

  messagesBox: {
    flex: 1,
    overflowY: "auto",
    padding: "10px",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },

  messageBubble: {
    maxWidth: "75%",
    padding: "12px 16px",
    borderRadius: "12px",
    fontSize: "15px",
  },

  typingBubble: {
    display: "flex",
    background: "#f1f1f1",
    padding: "8px 12px",
    borderRadius: 10,
    width: 50,
    marginBottom: 5,
  },

  inputRow: {
    display: "flex",
    gap: 10,
  },

  input: {
    flex: 1,
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid #aaa",
  },

  button: {
    padding: "12px 18px",
    background: "#065f92",
    color: "white",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
  },

  rightPanel: {
    width: "230px",
    height: "650px",
    
    borderRadius: "12px",
    padding: "15px",
    background: "#05c8f9",
    boxShadow: "0px 0px 15px rgba(0,0,0,0.2)",
  },

  helpBtn: {
    position: "fixed",
    bottom: "20px",
    right: "20px",
    background: "#007bff",
    color: "white",
    padding: "12px 20px",
    borderRadius: "30px",
    cursor: "pointer",
    boxShadow: "0px 3px 10px rgba(0,0,0,0.3)",
  },
};

export default App;
