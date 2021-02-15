import React from "react";
import { TwitterTweetEmbed } from "react-twitter-embed";

const Tweet = ({ json }) => {
  const { id, text, public_metrics, sentiment } = json.data;

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

  return (
      <React.Fragment>
        <ul>
          <li>{id}</li>
          <li>{text}</li>
          <li>
            <ul>
              {printObjects(public_metrics)}
            </ul>
          </li>
          <li>
            <ul>
              {printObjects(sentiment)}
            </ul>
          </li>
        </ul>
      </React.Fragment>
  );
};

export default Tweet;
