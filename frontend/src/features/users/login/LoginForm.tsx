import React, { useState, useCallback } from "react";
import { Navigate } from 'react-router-dom';
import Submit from 'shared/components/Submit';
import { api } from 'api';


type FormErrors = Record<string, string[]>;

type LoginSuccessData = {
  token: string;
  email: string;
  slug: string;
};

function LoginForm() {
  const [formData, setFormData] = useState({
      email: '',
      password: '',
      slug: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [errors] = useState<FormErrors>({});
  const [redirectToHome, setRedirectToHome] = useState(false);
  
  const handleLoginSuccess = useCallback((data: LoginSuccessData) => {
    console.log("Login successful:", data);
    localStorage.setItem('accessToken', data.token);
    localStorage.setItem('userEmail', data.email);
    localStorage.setItem('userSlug', data.slug);
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    if (!formData.email || !formData.password) {
      setMessage('Please enter both email and password')
      setIsLoading(false);
      return
    }

    try {
      const response = await api.loginUser(formData)
      const data = await response.json();

      if (response.ok) {
          setMessage('Login successful!');
          // Call the callback function passed from App.js
          handleLoginSuccess(data);
          // setTimeout(() => {
          //   setRedirectToHome(true);
          // }, 2000);
      } else {
          let errorMessage = 'Login failed.';
          if (data.non_field_errors) {
              errorMessage = `Error: ${data.non_field_errors[0]}`;
          } else if (data.detail) {
                errorMessage = `Error: ${data.detail}`;
          } else if (typeof data === 'object' && data !== null) {
                errorMessage = `Error: ${JSON.stringify(data)}`;
          }
          setMessage(errorMessage);
      }
    } catch (error) {
        console.error("Login error:", error);
        setMessage('An error occurred during login. Please try again later.');
    } finally {
        setIsLoading(false);
    }
  };

  if (redirectToHome) {
    return <Navigate to="/" replace />;
  }

  return (
    <>
    <form className="login" onSubmit={handleSubmit}>
      <input name="email" onChange={handleChange} value={formData.email} placeholder="Email" />
      {errors.email?.map((msg, idx) => (
        <div key={idx} className="error">
            {msg}
        </div>
      ))}
      <input type="password" name="password" onChange={handleChange} value={formData.password} placeholder="Password" />
      {errors.password?.map((msg, idx) => (
        <p key={idx} className="error">
            {msg}
        </p>
      ))}
      <div>
        <Submit label="Login" isLoading={isLoading} />
      </div>
      <p>{message}</p>
      {errors.non_field_errors?.map((msg, idx) => (
        <p key={idx} className="error">
            {msg}
        </p>
      ))}
    </form>
    <a href="/registration">
      <button
        disabled={isLoading}
        style={{
            width: "100%",
            backgroundColor: "transparent",
            color: "white",
            border: "none",
            padding: "0.5rem 1rem",
            borderRadius: "0.25rem",
            boxShadow: `0px 0px 30px var(--color-main-theme) inset`
        }}>
          Register
      </button>
    </a>
    </>
  );
}

export default LoginForm;