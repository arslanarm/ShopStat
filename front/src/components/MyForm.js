import { useState } from "react";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import Datetime from "react-datetime";
import "react-datetime/css/react-datetime.css";
import Offcanvas from "react-bootstrap/Offcanvas";

export default function MyForm({ submit }) {
  const [show, setShow] = useState(false);

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  function handleSubmit(event) {
    event.preventDefault();
    const today = new Date();
    if (selectedDate > selectedDate2 || selectedDate2 > today) {
      handleShow();
      return;
    }
    submit({
      start_date:
        selectedDate.getFullYear() +
        "-" +
        (selectedDate.getMonth() + 1) +
        "-" +
        selectedDate.getDate() +
        " " +
        selectedDate.toTimeString().slice(0, 8),
      end_date:
        selectedDate2.getFullYear() +
        "-" +
        (selectedDate2.getMonth() + 1) +
        "-" +
        selectedDate2.getDate() +
        " " +
        selectedDate2.toTimeString().slice(0, 8),
    });
  }
  const [selectedDate, setSelectedDate] = useState(
    new Date(new Date() - 604738402)
  );
  const [selectedDate2, setSelectedDate2] = useState(new Date());
  function handleDateChange(date) {
    setSelectedDate(date.toDate());
  }
  function handleDateChange2(date) {
    setSelectedDate2(date.toDate());
  }
  const dateFormat = "YYYY-MM-DD";
  return (
    <div style={{ width: 300 }}>
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Start Date</Form.Label>
          <Datetime
            value={selectedDate}
            onChange={handleDateChange}
            dateFormat={dateFormat}
            timeFormat="HH:mm:ss"
          />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>End date</Form.Label>
          <Datetime
            value={selectedDate2}
            onChange={handleDateChange2}
            dateFormat={dateFormat}
            timeFormat="HH:mm:ss"
          />
        </Form.Group>

        <Button variant="primary" type="submit">
          Look for this dates
        </Button>
      </Form>
      <Offcanvas show={show} onHide={handleClose} placement="top">
        <Offcanvas.Header closeButton>
          <Offcanvas.Title>Неверные даты</Offcanvas.Title>
        </Offcanvas.Header>
        <Offcanvas.Body>Неверные даты</Offcanvas.Body>
      </Offcanvas>
    </div>
  );
}
