import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMagnifyingGlass, faCircleXmark } from '@fortawesome/free-solid-svg-icons';

export default function Searchbar() {
  const [query, setQuery] = useState('');
  const [isVisible, setIsVisible] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Focus the input when search bar becomes visible
  useEffect(() => {
    if (isVisible && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isVisible]);

  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (query.trim()) {
      navigate(`/entries/?q=${encodeURIComponent(query.trim())}`);
      setQuery('');
      setIsVisible(false);
    }
  };

  const toggleSearchBar = () => {
    setIsVisible(!isVisible);
  };

  return (
    <div className="search-container">
      <button 
        onClick={toggleSearchBar}
        className="search-toggle-button"
        aria-label={isVisible ? "Hide search" : "Show search"}
      >
      <FontAwesomeIcon icon={isVisible ? faCircleXmark : faMagnifyingGlass} />
      </button>
      
      {isVisible && (
        <form onSubmit={handleSearch} className="search-bar-form">
          <input
            ref={searchInputRef}
            id="search"
            type="search"
            placeholder="Search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </form>
      )}
    </div>
  );
}