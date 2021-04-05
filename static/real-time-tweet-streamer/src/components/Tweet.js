import React, {useRef} from "react";
import { TwitterTweetEmbed } from "react-twitter-embed";
import '../stylesheets/Tweet.css';

const Tweet = ({ json }) => {
  const { id, text, public_metrics, sentiment } = json.data;
  const dragCntr = useRef(false);

  const {tokens, words, positive, negative, calculation, ...sent_to_print} = sentiment;

  const sorted_words = calculation
      .map(word_obj => [Object.keys(word_obj)[0], Object.values(word_obj)[0]])
      .sort((a, b) => b[1] - a[1]);

  const words_to_print = {
      positive: Object.fromEntries(sorted_words.slice(0, 3).filter(word => word[1] > 0)),
      negative: Object.fromEntries(sorted_words.slice(  -3).filter(word => word[1] < 0)),
  }

  const options = {
    cards: "hidden",
    align: "center",
    width: "550",
    conversation: "none",
  };

  const printObjects = (object) => Object.keys(object)
      .filter(key => typeof object[key] !== 'object' || Object.values(object[key]).length > 0)
      .map((key) =>
    <li key={key}>{key}: {typeof object[key] === 'object' && object[key] !== null
        ?<ul>{printObjects(object[key])}</ul>
        : object[key]}</li>
  );

  const navigateToTwitter = (e) => {
      if(!dragCntr.current && e.button !== 2) {
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
      <blockquote className="twitter-tweet" onMouseDown={setDragFalse} onMouseMove={setDragTrue} onMouseUp={navigateToTwitter}>
        <p>{`Tweet ID: ${id}`}</p>
        <p>{text}</p>
          <div className="grid">
            <div className="metrics">
                <h3>Public Metrics:</h3>
                {printObjects(public_metrics)}
            </div>
            <div className="sentiment">
                <h3>Sentiment:</h3>
                {printObjects(sent_to_print)}
                {printObjects(words_to_print)}
            </div>
          </div>
      </blockquote>
  );
};

export default Tweet;
