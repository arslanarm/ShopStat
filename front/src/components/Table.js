import React from "react";
import Table from "react-bootstrap/Table";

function MyTable({ data }) {
  return (
    <Table striped bordered hover>
      <thead>
        <tr>
          <th>Date</th>
          <th>ID</th>
          <th>In</th>
          <th>Out</th>
        </tr>
      </thead>
      <tbody>
        {data.map(({ date, id, in: inVal, out }) => (
          <tr key={id}>
            <td>{date}</td>
            <td>{id}</td>
            <td>{inVal}</td>
            <td>{out}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
}

export default MyTable;
