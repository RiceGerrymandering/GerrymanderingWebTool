import React, { Component } from 'react';
import map from './political_map_image.png';
import './App.css';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <p>
            <code>Welcome to Gerrymand-inator 2018. Gerrymander to your heart's desires..</code>
          </p>
        </header>
        <div className="Interactive-Map">
        	<img src={map}/>
        </div>
      	<div className="Toggle-Meters">
      		<code>Toggle the Competitiveness, Compactness, and Fairness below.</code>
      	</div>
      </div>
    );
  }
}

export default App;
