import React, { useState } from 'react';
import Submit from 'shared/components/Submit';
import { Navigate } from 'react-router-dom';
import { api } from 'api';

type FormErrors = Record<string, string[]>;

const CreateEntry: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});

  const userEmail = localStorage.getItem('userEmail');
  const [formData, setFormData] = useState({
      title:'',
      description:'',
      created_by: userEmail || "",
      updated_by: userEmail || ""
  }); 

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
        setIsLoading(true);
        const response = await api.createEntry(formData)
        if (!response.ok) {
          const data = await response.json();
          if (typeof data === "object" && data !== null) {
            setErrors(data);
          } else {
            setErrors({ non_field_errors: ["Something went wrong."] });
          }
          return;
        } else {
            setMessage("Entry Created!");
            setFormData({ title: '', description: '', created_by: '', updated_by: '' });
            setTimeout(() => {
                <Navigate to="/entries/" replace />;
            }, 2000);
        }      
        setErrors({});
        setIsLoading(false);
      } catch (err: unknown) {
        setErrors({ non_field_errors: ["Network error or server unreachable."] });
        setIsLoading(false);
      }
  };

  return (
    <div className="center-container">
        <div className="header">
            <h1>Create New Entry</h1>
        </div>
        <div className="content">
          <form onSubmit={handleSubmit}>
            <div>
                <label htmlFor="title">Title</label>
                <input name="title" onChange={handleChange} value={formData.title} placeholder="Title" required/>
                {errors.title?.map((msg, idx) => (
                    <div key={idx} className="error">
                        {msg}
                    </div>
                ))}
            </div>
            <div>
                <label htmlFor="description">Description</label>
                <textarea
                id="description"
                rows={8}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
                />
                {errors.description?.map((msg, idx) => (
                    <div key={idx} className="error">
                        {msg}
                    </div>
                ))}
            </div>
            <Submit isLoading={isLoading} label="Create Entry"/>
          </form>
        </div>
    </div>
  );
};

export default CreateEntry;