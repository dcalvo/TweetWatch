import React, {useRef} from "react";
import { TwitterTweetEmbed } from "react-twitter-embed";
import '../stylesheets/Tweet.css';

const Tweet = ({ json }) => {
  const { id, text, public_metrics, sentiment } = json.data;
  const dragCntr = useRef(false);

  const options = {
    cards: "hidden",
    align: "center",
    width: "550",
    conversation: "none",
  };

  const printObjects = (object) => Object.keys(object).map((key) =>
    <li key={key}>{key}: {typeof object[key] === 'object' && object[key] !== null
        ?<ul>{printObjects(object[key])}</ul>
        : object[key]}</li>
  );

  const navigateToTwitter = () => {
      if(!dragCntr.current) {
          window.open(`https://twitter.com/foobar/status/${id}`);
      }
  }

  const setDragTrue = () => {
      dragCntr.current = true
  }

  const setDragFalse = () => {
      dragCntr.current = false
  }

  return (
      <blockquote className={"twitter-tweet"} onMouseDown={setDragFalse} onMouseMove={setDragTrue} onMouseUp={navigateToTwitter}>
        <p>{`Tweet ID: ${id}`}</p>
        <p>{text}</p>
        <ul>
          {printObjects(public_metrics)}
        </ul>
        <ul>
          {printObjects(sentiment)}
        </ul>
      </blockquote>
  );
};

export default Tweet;
