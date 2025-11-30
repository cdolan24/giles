import React from 'react';

function CrossSourceExplainer({ sources }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div style={{ marginTop: 16 }}>
      <h4>Cross-Source Comparison</h4>
      <ul>
        {sources.map((s, idx) => (
          <li key={idx}>{s.title} - {s.author || 'Unknown'} ({s.year || 'N/A'}) [{s.journal || 'N/A'}]</li>
        ))}
      </ul>
    </div>
  );
}

export default CrossSourceExplainer;
