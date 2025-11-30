import React, { useState } from 'react';

function SearchFilters({ onChange }) {
  const [filters, setFilters] = useState({ author: '', year: '', journal: '', open_access: false, citation_count: '' });

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setFilters(f => {
      const newFilters = { ...f, [name]: type === 'checkbox' ? checked : value };
      onChange(newFilters);
      return newFilters;
    });
  };

  return (
    <div style={{ marginBottom: 8 }}>
      <input name="author" value={filters.author} onChange={handleChange} placeholder="Author" style={{ width: '18%', marginRight: 4 }} />
      <input name="year" value={filters.year} onChange={handleChange} placeholder="Year" style={{ width: '12%', marginRight: 4 }} />
      <input name="journal" value={filters.journal} onChange={handleChange} placeholder="Journal" style={{ width: '18%', marginRight: 4 }} />
      <input name="citation_count" value={filters.citation_count} onChange={handleChange} placeholder="Citations" style={{ width: '12%', marginRight: 4 }} />
      <label style={{ marginLeft: 8 }}>
        <input type="checkbox" name="open_access" checked={filters.open_access} onChange={handleChange} /> Open Access
      </label>
    </div>
  );
}

export default SearchFilters;
