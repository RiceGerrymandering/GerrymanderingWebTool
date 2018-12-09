import React, { Component } from 'react';
import './App.css';
import axios from 'axios'

class App extends Component {

  constructor() {
    super()
    this.state = {
      username: ''
    }
    this.handle_click = this.handle_click.bind(this)
  }

  handle_click() {
    //console.log("Success!")
    var competitiveness = document.getElementById("competitiveness").value;
    var compactness = document.getElementById("compactness").value;
    var fairness = document.getElementById("fairness").value;
    axios.get('https://example.com/?competitiveness=' + competitiveness + '&compactness=' + compactness + '&fairness=' + fairness)
      .then(response => this.setState({username: response.data.login}))
  }

  render() {
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
        </div>
        <button className='button' onClick={this.handle_click}>Re-district</button>
        <p>{this.state.username}</p>
      </div>
    );
  }
}

export default App;
