import {useEffect, useState} from "react";
import { useAuth } from 'shared/context/AuthContext';
import { Link } from 'react-router-dom';
import Title from "shared/components/Title";
import { api } from "api";

const HomePage = () => {
  const [entries, setEntries] = useState<{ slug: string; title: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getEntries()
      .then((data) => {
        setEntries(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);
  
  const { isAuthenticated } = useAuth();
  return (
    <>
    <Title text="Stackgnosis"/>
    <div className="center-container">
      <div className="header">
      </div>
      <div className="content">
        <div className="welcome">
          <h3>Welcome to Stackgnosis!</h3>
          <p>Learn from, analyze, and share knowledge about various technologies and technical concepts.</p>
          <p>From understanding WebAssembly to containerization with Docker, GraphQL vs REST APIs, OAuth 2.0 vs OpenID Connect, and the event loop in JavaScript.</p>
        </div>
        <hr></hr>
        <div>
          <h4>Explore topics</h4>
          <div id="entry-wall" className="tag-wall">
            {!isAuthenticated && (
              <div style={{ marginTop: '1rem' }}>
                <Link to="/login">
                  <p className="tag">You are not logged in. Click here to login.</p>
                </Link>
              </div>
            )} 
            {loading && isAuthenticated && <p>Loading entries...</p>}
            {error && isAuthenticated && <p style={{ color: 'red' }}>Error: {error}</p>}
            {!loading && !error && isAuthenticated && entries.map((entry) => (
              <Link to={`/entries/${entry.slug}/`} key={entry.slug}>
                <p className="tag">{entry.title}</p>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
    </>
  );
};

export default HomePage;