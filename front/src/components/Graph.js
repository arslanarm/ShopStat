import { LineChart, Line, CartesianGrid, XAxis, YAxis } from "recharts";

function Graph({ data }) {
  return (
    <LineChart width={700} height={400} data={data}>
      <Line type="monotone" dataKey="in" stroke="#8884d8" />
      <Line type="monotone" dataKey="out" stroke="#b8a4d8" />
      <CartesianGrid stroke="#ccc" />
      <XAxis dataKey="date" />
      <YAxis />
    </LineChart>
  );
}

export default Graph;
