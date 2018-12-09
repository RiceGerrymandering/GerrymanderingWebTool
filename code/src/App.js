import React, { Component } from 'react';
//import map from './political_map_image.png';
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
    axios.get('https://api.github.com/users/thehadadinator')
      .then(response => this.setState({username: response.data.login}))
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
        </header>
        <button className='button' onClick={this.handle_click}>Re-district</button>
        <p>{this.state.username}</p>
      </div>
    );
  }
}

export default App;
