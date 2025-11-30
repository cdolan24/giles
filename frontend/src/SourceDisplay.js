import React from 'react';

function SourceDisplay({ sources }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div style={{ marginTop: 16 }}>
      <h4>Sources</h4>
      <ul>
        {sources.map((s, idx) => (
          <li key={idx}>{s}</li>
        ))}
      </ul>
    </div>
  );
}

export default SourceDisplay;
