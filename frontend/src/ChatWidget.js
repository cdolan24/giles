import React, { useState } from 'react';


import { searchPapers } from './api';
import CitationDisplay from './CitationDisplay';
import SearchFilters from './SearchFilters';


function ChatWidget() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [citations, setCitations] = useState([]);
  const [filters, setFilters] = useState({});

  const handleSend = async () => {
    if (!input.trim()) return;
    setMessages([...messages, { text: input, user: true }]);
    setLoading(true);
    try {
      // Pass filters to backend
      const queryParams = { ...filters };
      const results = await searchPapers(input, queryParams);
      console.log('Backend response:', results); // Log raw backend response for debugging
      if (Array.isArray(results)) {
        // Check if any error objects are present in the array
        const errorObj = results.find(r => r && r.error);
        if (errorObj) {
          setMessages(msgs => [
            ...msgs,
            { text: `Error: ${errorObj.error} (${errorObj.error_code || ''})`, user: false }
          ]);
          setCitations([]);
        } else {
          setMessages(msgs => [
            ...msgs,
            { text: `Recommended papers: ${results.map(r => r.title).join(', ')}`, user: false }
          ]);
          setCitations(results.map(r => ({
            author: r.author || 'Unknown',
            year: r.year || 'N/A',
            title: r.title,
            journal: r.journal || 'N/A'
          })));
        }
      } else if (results && results.error) {
        setMessages(msgs => [
          ...msgs,
          { text: `Error: ${results.error} (${results.error_code || ''})`, user: false }
        ]);
        setCitations([]);
      } else {
        setMessages(msgs => [
          ...msgs,
          { text: 'Unexpected response format from backend.', user: false }
        ]);
        setCitations([]);
      }
    } catch (e) {
      // Try to extract error_code from error response if available
      let errorMsg = 'Error fetching recommendations.';
      if (e && e.error_code) {
        errorMsg += ` (${e.error_code})`;
      }
      setMessages(msgs => [
        ...msgs,
        { text: errorMsg, user: false }
      ]);
      setCitations([]);
    }
    setLoading(false);
    setInput('');
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: 16, borderRadius: 8, maxWidth: 400 }}>
      <SearchFilters onChange={setFilters} />
      <div style={{ minHeight: 100, marginBottom: 8 }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ textAlign: msg.user ? 'right' : 'left' }}>
            {msg.text}
          </div>
        ))}
        {loading && <div>Loading...</div>}
      </div>
      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
        style={{ width: '80%' }}
        placeholder="Ask about a field of study..."
        disabled={loading}
      />
      <button onClick={handleSend} style={{ width: '18%', marginLeft: '2%' }} disabled={loading}>
        Send
      </button>
      <CitationDisplay citations={citations} />
    </div>
  );
}

export default ChatWidget;
