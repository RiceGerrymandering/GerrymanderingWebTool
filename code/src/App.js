import React, { Component } from 'react';
//import map from './political_map_image.png';
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
    //console.log("Success!")
    axios.get('http://localhost:3001/test?one="1"&two="1"&three="2"')
      .then(response => this.setState({image: response.data}))
  }

  render() {
    var src = this.state.image
    return (
      <div className="App">
        <header className="App-header">
        </header>
        <button className='button' onClick={this.handle_click}>Re-district</button>
        <div>
          <img src={src}/>
        </div>
      </div>

    );
  }
}

export default App;
