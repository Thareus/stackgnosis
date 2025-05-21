import { useState } from 'react';
import Submit from 'shared/components/Submit';
import { api } from 'api';
import { Navigate } from 'react-router-dom';

type FormErrors = Record<string, string[]>;

function RegisterForm() {
  const [formData, setFormData] = useState({
    first_name:'',
    last_name:'',
    username: '',
    email: '',
    password: '',
    password2: '',
});
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [redirectToLogin, setRedirectToLogin] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
        const response = await api.registerUser(formData)
        if (!response.ok) {
          const data = await response.json();
          if (typeof data === "object" && data !== null) {
            setErrors(data);
          } else {
            setErrors({ non_field_errors: ["Something went wrong."] });
          }
          return;
        } else {
            setMessage("Registration successful!");
            setErrors({});
            setTimeout(() => {
                setRedirectToLogin(true);
            }, 2000);
        }      
      } catch (err: unknown) {
        setErrors({ non_field_errors: ["Network error or server unreachable."] });
      }
  };

  if (redirectToLogin) {
    return <Navigate to="/login" replace={true} />;
  }

  return (
    <form className="register" onSubmit={handleSubmit}>
      <input name="first_name" onChange={handleChange} value={formData.first_name} placeholder="First Name" />
      {errors.first_name?.map((msg, idx) => (
        <div key={idx} className="error">
            {msg}
        </div>
      ))}
      <input name="last_name" onChange={handleChange} value={formData.last_name} placeholder="Last Name" />
      {errors.last_name?.map((msg, idx) => (
        <div key={idx} className="error">
            {msg}
        </div>
      ))}
      <input name="username" onChange={handleChange} value={formData.username} placeholder="Username" />
      {errors.username?.map((msg, idx) => (
        <div key={idx} className="error">
            {msg}
        </div>
      ))}
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
      <input type="password" name="password2" onChange={handleChange} value={formData.password2} placeholder="Repeat Password" />
      
      <Submit isLoading={isLoading} label="Register" />
      
      <p>{message}</p>
      {errors.non_field_errors?.map((msg, idx) => (
        <p key={idx} className="error">
            {msg}
        </p>
      ))}
    </form>
  );
}

export default RegisterForm;