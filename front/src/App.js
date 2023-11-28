import React, { Suspense, useState } from "react";
import { Route, Routes, Link, BrowserRouter } from "react-router-dom";

import DataPage from "./DataPage";
import Register from "./Register";
import Login from "./Login";
import "./App.css";

function App() {
  const [logged, setLoggeed] = useState(true);
  function login() {
    setLoggeed(true);
  }

  return (
    <BrowserRouter>
      <div>
        <Suspense fallback={<div>Loading...</div>}>
          {/* <div className="container">
            <Link to={"/data"}>Data</Link>
            <Link to={"/"}>Register</Link>
            <Link to={"/login"}>Login</Link>
          </div> */}
          <Routes>
            <Route path={"/data"} element={<DataPage logged={logged} />} />
            <Route path={"/"} element={<Register />} />
            <Route path={"/login"} element={<Login onSuccess={login} />} />
          </Routes>
        </Suspense>
      </div>
    </BrowserRouter>
  );
}

export default App;
