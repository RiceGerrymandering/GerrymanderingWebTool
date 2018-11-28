import React, { Component } from 'react';
import map from './political_map_image.png';
import './App.css';

class App extends Component {

  render() {
    return (
      <div className="App">
        <header className="App-header">
        </header>
        <div className="Interactive-Map">
        	<img src={map}/>
        </div>
      </div>
    );
  }
}

export default App;
