import React from 'react';

function CitationDisplay({ citations }) {
  if (!citations || citations.length === 0) return null;
  return (
    <div style={{ marginTop: 16 }}>
      <h4>Citations</h4>
      <ul>
        {citations.map((c, idx) => (
          <li key={idx}>{c.author} ({c.year}), <i>{c.title}</i>, {c.journal}</li>
        ))}
      </ul>
    </div>
  );
}

export default CitationDisplay;
