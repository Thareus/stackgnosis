import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Title from "shared/components/Title";
import { api } from "api";

const BookmarksPage = () => {
    const [bookmarks, setBookmarks] = useState<{ slug: string; title: string }[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const userSlug = localStorage.getItem('userSlug') || "";
    

      useEffect(() => {
        if (!userSlug) {
            window.location.href = "/users/login";
        }
        api.getBookmarks(userSlug)
          .then((data) => {
            setBookmarks(data);
            setLoading(false);
          })
          .catch((err) => {
            setError(err.message);
            setLoading(false);
          });
      }, []);
  
      return (
      <>
          <Title text="Bookmarks"/>
          <div className="center-container">
          <div id="entries-list" className="content">
              {loading && <p>Loading bookmarks...</p>}
              {error && <p style={{ color: 'red' }}>Error: {error}</p>}
              {!loading && !error && !bookmarks.length && <p>You have no entries currently bookmarked.</p>}
              {!loading && !error && bookmarks.map((bookmark) => (
                  <Link to={`/entries/${bookmark.slug}/`} key={bookmark.slug}>
                  <p className="tag">{bookmark.title}</p>
                  </Link>
              ))}
          </div>
          </div>
      </>
      );
  };
  
  export default BookmarksPage;