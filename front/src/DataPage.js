import "./App.css";
import { useState, useEffect } from "react";
import Graph from "./components/Graph";
import Table from "./components/Table";
import Alert from "react-bootstrap/Alert";
import axios from "axios";
import MyForm from "./components/MyForm";
import FileUpload from "./components/FileUpload";
import { useNavigate } from "react-router";
import { url } from "./URL";

function DataPage(props) {
  // const data = [
  //   { date: "2023-02-16 15:59:59", id: 100, in: 1, out: 50 },
  //   { date: "2023-02-16 15:59:59", id: 200, in: 2, out: 75 },
  //   { date: "2023-02-16 15:59:59", id: 300, in: 3, out: 125 },
  //   { date: "2023-02-16 15:59:59", id: 400, in: 4, out: 250 },
  //   { date: "2023-02-16 15:59:59", id: 500, in: 5, out: 375 },
  // ];
  const [appState, setAppState] = useState({
    loading: false,
    data: [
      { date: "2023-02-16 15:59:59", id: 100, in: 1, out: 50 },
      { date: "2023-02-16 15:59:59", id: 200, in: 2, out: 75 },
      { date: "2023-02-16 15:59:59", id: 300, in: 3, out: 125 },
      { date: "2023-02-16 15:59:59", id: 400, in: 4, out: 250 },
      { date: "2023-02-16 15:59:59", id: 500, in: 5, out: 375 },
    ],
  });
  const navigate = useNavigate();

  useEffect(() => {
    if (!props.logged) {
      navigate("/login");
      return;
    }
    setAppState({ loading: true });
    const apiUrl = `${url}/get_rows_this_week`; //
    axios.get(apiUrl).then((resp) => {
      const allData = resp.data;
      setAppState({
        loading: false,
        data: allData,
      });
    });
  }, [setAppState, props.logged, navigate]);
  function onSubmit(values) {
    // console.log(values);
    //
    setAppState({ loading: true });
    const apiUrl = `${url}/get_rows`; //
    axios.get(apiUrl, { params: values }).then((resp) => {
      const allData = resp.data;
      setAppState({
        loading: false,
        data: allData,
      });
    });
  }

  return (
    <div
      className="App"
      style={{
        display: "flex",
        justifyContent: "center",
        flexDirection: "column",
        alignItems: "center",
        margin: "10px",
        gap: "10px",
      }}
    >
      <div style={{ display: "flex", gap: "10px", width: "80%" }}>
        <MyForm submit={onSubmit} />
        {!appState.loading && <Table data={appState.data} />}
      </div>
      <div style={{ display: "flex", gap: "10px", width: "80%" }}>
        {!appState.loading && <Graph data={appState.data} />}
        {!appState.loading && <Graph data={appState.data} />}
      </div>
      {appState.loading && <Alert variant="warning">Данные загружаются</Alert>}
      <FileUpload />
    </div>
  );
}

export default DataPage;
