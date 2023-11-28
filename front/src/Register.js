import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

import Alert from "react-bootstrap/Alert";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { url } from "./URL";
function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [wrong, setWrong] = useState(false);

  const navigate = useNavigate();
  const handleRegister = (event) => {
    event.preventDefault();
    const data = { username, password };
    axios
      .post(`${url}/register`, data)
      .then((response) => {
        if (response.data.message === "User registered successfully!")
          navigate("/login");
        else throw response;
      })
      .catch((error) => {
        setWrong(true);
        console.error(error);
      });
  };

  return (
    <div style={{ padding: "10px" }}>
      <h1 style={{ padding: "10px" }}>Register</h1>
      <Form onSubmit={handleRegister}>
        <Form.Group className="mb-3">
          Username:
          <Form.Control
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </Form.Group>
        <Form.Group className="mb-3">
          Password:
          <Form.Control
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </Form.Group>
        <Button type="submit">Login</Button>

        <Link to={"/login"} style={{ padding: "15px" }}>
          <Button>Already have an account?</Button>
        </Link>

        {wrong && <Alert variant={"danger"}>Wrong Login or password</Alert>}
      </Form>
    </div>
  );
}
export default Register;
