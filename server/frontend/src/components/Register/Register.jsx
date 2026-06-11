import React, { useState } from 'react';
import Header from '../Header/Header';
import './Register.css';

const Register = () => {
  const [userName, setUserName] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const register = async (event) => {
    event.preventDefault();
    const response = await fetch(`${window.location.origin}/djangoapp/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userName,
        firstName,
        lastName,
        email,
        password,
      }),
    });
    const result = await response.json();
    if (result.status === 'Registered') {
      sessionStorage.setItem('username', result.userName);
      sessionStorage.setItem('firstname', firstName);
      sessionStorage.setItem('lastname', lastName);
      window.location.href = '/';
    } else {
      alert(result.error || 'Registration failed.');
    }
  };

  return (
    <div>
      <Header />
      <form className="register_panel" onSubmit={register}>
        <h2>Create your account</h2>
        <input type="text" placeholder="Username" onChange={(e) => setUserName(e.target.value)} required />
        <input type="text" placeholder="First Name" onChange={(e) => setFirstName(e.target.value)} required />
        <input type="text" placeholder="Last Name" onChange={(e) => setLastName(e.target.value)} required />
        <input type="email" placeholder="Email" onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} required />
        <button className="action_button" type="submit">Register</button>
      </form>
    </div>
  );
};

export default Register;
