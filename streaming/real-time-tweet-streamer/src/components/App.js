import React from "react";
import { BrowserRouter, Route } from "react-router-dom";

import Navbar from "./Navbar";
import TweetFeed from "./TweetFeed";
import RuleList from "./RuleList";

const App = (props) => {

    const [isStreaming, setIsStreaming] = React.useState(true);

    return (
      <div className="ui container">
        <div className="introduction"></div>

        <h1 className="ui header">
          <img
            className="ui image"
            src="/Twitter_Logo_Blue.png"
            alt="Twitter Logo"
          />
          <div className="content">
            Real Time Tweet Streamer
            <div className="sub header">Powered by Twitter data</div>
          </div>
        </h1>

        <div className="ui container">
          <BrowserRouter>
            <Navbar />
            <button onClick={() => setIsStreaming(p => !p)}>{isStreaming ? 'Pause!' : 'Resume!'}</button>
            <Route exact path="/" component={RuleList} />
            <Route exact path="/rules" component={RuleList} />
            <Route exact path="/tweets" isStreaming={isStreaming} render={(props) => (
                <TweetFeed {...props} isStreaming={isStreaming} />
            )} />
          </BrowserRouter>
        </div>
      </div>
    );
}

export default App;
