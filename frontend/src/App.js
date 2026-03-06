import React from 'react';
import Chatbot from './Chatbot';
import FileUpload from './FileUpload';

function App() {
  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
      <h1>RAG Chatbot</h1>
      <FileUpload />
      <Chatbot />
    </div>
  );
}

export default App;
