import {useState, useEffect } from "react";
import Title from "shared/components/Title";
import { Link } from "react-router-dom";
import {api} from 'api';
import { useLocation } from 'react-router-dom';
import { Button } from "reactstrap";
import ModalManager from "shared/components/ModalManager";

const EntryList = () => {
  const location = useLocation();
  const query = new URLSearchParams(location.search).get('q');
  const [entries, setEntries] = useState<{ slug: string; title: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const [modalContentType, setModalContentType] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.getEntries(query || "")
      .then((data) => {
        setEntries(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [query]);

  const handleRequestNewEntry = () => {
    setModalContentType('requestNewEntryForm');
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setModalContentType(null);
  };

  return (
    <>
        {/* ModalManager at top level */}
        <ModalManager
          isOpen={modalOpen}
          onClose={handleCloseModal}
          contentType={modalContentType || ''}
        />
        <Title text="Entries"/>
        <div className="center-container">
          <div className="header">
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <Button onClick={handleRequestNewEntry}>
                Request New Entry
              </Button>
            </div>
          </div>
          <div id="entries-list" className="content">
              {loading && <p>Loading entries...</p>}
              {error && <p style={{ color: 'red' }}>Error: {error}</p>}
              {!loading && !error && !entries.length && query && 
                <>
                  <p>No entries found.</p>
                  <Button onClick={() => {api.requestNewEntry(query)}}>
                    Request New Entry for "{query}"
                  </Button>
                </>
              }
              {!loading && !error && !entries.length && 
                <>
                  <p>No entries found.</p>
                  <Link to={`/entries/create/`}>
                    <Button>Create a new Entry</Button>
                  </Link>
                </>
              }
              {!loading && !error && entries.map((entry) => (
                  <Link to={`/entries/${entry.slug}/`} key={entry.slug}>
                  <p className="tag">{entry.title}</p>
                  </Link>
              ))}
          </div>
        </div>
    </>
    );
};

export default EntryList;