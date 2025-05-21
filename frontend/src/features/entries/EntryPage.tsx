import React, { useState, useEffect } from "react";
import { useParams, Navigate, useNavigate, Link } from "react-router-dom";
import Title from "shared/components/Title";
import Sidebar from "shared/components/Sidebar";
import ContextMenu from "shared/components/ContextMenu";
import { LinksToggle, handleToggleChange } from "shared/components/LinksToggle";
import { api } from "api";
import Button from "shared/components/Button";
import { toast } from "shared/components/Toast";

type Entry = {
  identifier: string;
  slug: string;
  title: string;
  description: string;
  date_created: string;
  date_updated: string;
  related: Array<{ slug: string; title: string }>;
};

function parseEntry(raw: any): Entry | null {
  if (!raw.slug || !raw.title || !raw.description) return null;
  return {
    identifier: raw.identifier ?? "",
    slug: raw.slug,
    title: raw.title,
    description: raw.description,
    date_created: raw.date_created ?? "",
    date_updated: raw.date_updated ?? "",
    related: raw.related ?? [],
  };
}

interface CollapsibleSectionProps {
  title: string;
  content: string;
}

const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({ title, content }) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <section>
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="header"
      >
        <span className="mr-2">{isOpen ? '▼' : '▶'}</span>
        <span dangerouslySetInnerHTML={{ __html: title }} />
      </div>
      {isOpen && (
        <div className="section-content" dangerouslySetInnerHTML={{ __html: content }} />
      )}
    </section>
  );
};

function renderDescriptionSections(description: string) {
  if (!description) return null;

  const sections = description.split(/(?=<h3>)/); // Split at every position to the left of every <h3> tag, but keep the <h3> tag
  const split_sections: Array<[string, string]> = []
  sections.forEach((section) => {
    // Split on end of h3 tag assuming this divides header from body.
    const parts = section.split(/(?<=<\/h3>)/s);
    if (parts.length === 2) {
      split_sections.push([parts[0], parts[1]]);
    } else if (parts.length === 1) {
      // If there's no </h3>, treat the whole section as body with empty header
      split_sections.push(["", parts[0]]);
    } else {
      // If there are more than 2 parts, join the rest as body
      split_sections.push([parts[0], parts.slice(1).join("")]);
    }
  });

  return split_sections.map(([header, body], idx) => (
    <CollapsibleSection
      key={idx}
      title={header}
      content={body}
    />
  ));
}

const EntryPage = () => {
  const params = useParams();
  const slug = params.slug
  const navigate = useNavigate();
  const [entry, setEntry] = useState<Entry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [linksMode] = useState<'hide' | 'hover' | 'show'>('show');

  function deleteEntry(slug: string) {
    api.deleteEntry(slug)
      .then(() => {
        toast.success("Entry deleted successfully.");
        navigate('/entries/');
      })
      .catch(error => {
        toast.error(`Failed to delete entry: ${error.message}`);
      });
  }
  

  useEffect(() => {  
    const fetchItem = () => {
      setLoading(true);
      api.getEntry(`${slug}`)
        .then(data => {
          const parsed = parseEntry(data);
          if (parsed) {
            setEntry(parsed);
            handleToggleChange(linksMode);
          } else {
            setError("Malformed entry data.");
          }
          setLoading(false);
        })
        .catch(error => {
          setError(error.message);
          setLoading(false);
        });
    };
    fetchItem();
  }, [slug]);

  if (loading) {
    return (
      <Title text={"Loading..."}/>
    )
  }

  if (error) {
    return (
      <>
      <Title text={"Error..."}/>
      <div className="entry-container">
        <div className="header" style={{
          display: 'inherit',
          justifyContent: 'center',
        }}>
          <div
            style={{ 
              color: 'red',
              margin: '1rem 0rem',
              fontSize: '1.5em'
            }}
          >
            {error}
          </div>
          <a href="/entries/" style={{display:'inherit', justifyContent: 'center'}}>
            <p className="tag">Back to Entries</p>
          </a>
        </div>
      </div>
      </>
    );
  }

  if (!entry) {
    return <Navigate to="/entries/not-found" replace />;
  }

  return (
    <>
    <Title text={entry.title}/>
    <div className="entry-container">
      <div id="entry-header" className="header">
        <LinksToggle/>
      </div>
      <div id="entry-content" className="content">
        <div id="description">
          {renderDescriptionSections(entry.description)}
        </div>
      </div>
      <div id="entry-footer" className="footer">
        <div id="dates"
          className="flex"
          style={{
            gap: '0.5rem',
          }}
          >
          <p>Date Created:</p>
          {entry.date_created && (
            <time dateTime={entry.date_created}>
              {new Date(entry.date_created).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </time>
          )}
        </div>
        {entry.related && entry.related.length > 0 && (
          <div id="tags">
            <h4>Tags: </h4>
            <div id="entry-wall" className="tag-wall">
              {entry.related.map((tag) => (
                <Link to={`/entries/${tag.slug}`}>
                  <p className="tag">{tag.title}</p>
                </Link>
              ))}
            </div>
          </div>
        )}
        <div className="back-container">
          <Link to="/entries/">
            <p className="tag">Back to Entries</p>
          </Link>
          <Button
            onClick={() => deleteEntry(entry.slug)}
            className="delete"
            >
            Delete Entry
          </Button>
        </div>
        <Sidebar />
        <ContextMenu/>
      </div>      
    </div>
    </>
  );
};

export default EntryPage;