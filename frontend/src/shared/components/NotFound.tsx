import { Link } from "react-router-dom";
import Title from "./Title";

export default function NotFound() {
  return (
    <>
    <Title text="Oops"/>
    <div className="center-container">
      <div className="content">
        <p className="">Oops! The page you're looking for doesn't exist.</p>
        <a href="/" className="show">
          Go back Home
        </a>
      </div>
    </div>
    </>
  );
}