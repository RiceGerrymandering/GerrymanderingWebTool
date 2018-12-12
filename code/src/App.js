import React, { Component } from 'react';
import './App.css';
import axios from 'axios'

class App extends Component {

  constructor() {
    super()
    this.state = {
      image: ''
    }
    this.handle_click = this.handle_click.bind(this)
  }

  handle_click() {
    var competitiveness = parseInt(document.getElementById("competitiveness").value);
    var compactness = parseInt(document.getElementById("compactness").value);
    var fairness = parseInt(document.getElementById("fairness").value);
    var stateVal = document.getElementById("state").value;
    var url = 'https://test-gerry.herokuapp.com/test?competitiveness=' + competitiveness + '&compactness=' + compactness + '&fairness=' + fairness + '&state="' + stateVal + '"'
    //var url = 'http://localhost:3001/test?competitiveness=' + competitiveness + '&compactness=' + compactness + '&fairness=' + fairness + '&state="' + state + '"'
    console.log(url)
    axios.get(url)
      .then(response => this.setState({image: response.data}))
  }

  render() {
    var src = this.state.image
    return (
      <div className="App">
        <header className="App-header">
        </header>
        <div className="Toggle-Boxes">
          <code>Competitiveness: </code>
          <select id="competitiveness">
            <option>1</option>
            <option>2</option>
            <option>3</option>
            <option>4</option>
            <option>5</option>
          </select>
          <code> Compactness: </code>
          <select id="compactness">
            <option>1</option>
            <option>2</option>
            <option>3</option>
            <option>4</option>
            <option>5</option>
          </select>
          <code> Fairness: </code>
          <select id="fairness">
            <option>1</option>
            <option>2</option>
            <option>3</option>
            <option>4</option>
            <option>5</option>
          </select>
          <code> State: </code>
          <select id="state">
            <option>NH</option>
            <option>TX</option>
          </select>
        </div>
        <button className='button' onClick={this.handle_click}>Re-district</button>
        <div>
          <img src={src}/>
        </div>
      </div>

    );
  }
}

export default App;
