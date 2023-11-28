import React, { useState } from "react";
import axios from "axios";
import Alert from "react-bootstrap/Alert";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { useNavigate } from "react-router-dom";
import { url } from "./URL";
function Login(props) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [wrong, setWrong] = useState(false);

  const navigate = useNavigate();
  const handleLogin = (event) => {
    event.preventDefault();
    const data = { username, password };
    axios
      .post(`${url}/login`, data)
      .then((response) => {
        if (response.data.message === "Login successful!") {
          props.onSuccess();
          navigate("/data");
        } else {
          setWrong(true);
          throw response;
        }
      })
      .catch((error) => {
        if (error.message === "Request failed with status code 401")
          setWrong(true);
        console.error(error);
      });
  };

  return (
    <div style={{ padding: "10px" }}>
      <h1 style={{ padding: "10px" }}>Login</h1>
      <Form onSubmit={handleLogin}>
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
        {wrong && <Alert variant={"danger"}>Wrong Login or password</Alert>}
      </Form>
    </div>
  );
}

export default Login;
