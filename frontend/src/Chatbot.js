import React, { useState } from 'react';
import axios from 'axios';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', text: input };
    setMessages([...messages, userMsg]);
    setInput('');

    try {
      const res = await axios.get('http://localhost:8000/query', {
        params: {
          question: userMsg.text,
        }
      });
      const botMsg = {role: 'bot',text: res.data.answer,  sources: res.data.sources};
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <div
        style={{
          border: '1px solid #ccc',
          minHeight: 200,
          padding: 10,
          marginBottom: 10,
          overflowY: 'auto',
        }}
      >
        {messages.map((m, i) => (
          <div key={i} style={{ textAlign: m.role === 'user' ? 'right' : 'left' }}>
            <b>{m.role === 'user' ? 'You' : 'Bot'}:</b> {m.text}
            {m.sources && (
             <div style={{ fontSize: "12px", marginTop: "5px", color: "#666" }}>
              <b>Sources:</b>
              {m.sources.map((s, idx) => (
               <div key={idx}>
               {s.pdf} — Page {s.page}, Paragraph {s.paragraph}
               </div>
              ))}
             </div>
            )}
          </div>
        ))}
      </div>
      <input
        style={{ width: '80%' }}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        placeholder="Ask a question"
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
};

export default Chatbot;
