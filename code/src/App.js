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
    this.found = ''
  }

    post_stats(map) {
      var stats = document.getElementsByClassName("stats")[0];

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var competitiveness_score = map.c1;
      var c1 = document.createElement("c1");
      c1.innerHTML = "<code> Competitiveness Score: " + competitiveness_score + "</code>";
      stats.appendChild(c1);

      var compactness_score = map.c2;
      var c2 = document.createElement("c2");
      c2.innerHTML = "<code> Compactness Score: " + compactness_score + "</code>";
      stats.appendChild(c2);

      var fairness_score = map.f;
      var f = document.createElement("f");
      f.innerHTML = "<code> Fairness Score: " + fairness_score + "</code>";
      stats.appendChild(f);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);
      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var competitiveness_percentile = map.c1p;
      var c1p = document.createElement("c1p");
      c1p.innerHTML = "<code> Competitiveness Percentile: " + competitiveness_percentile + "</code>";
      stats.appendChild(c1p);

      var compactness_percentile = map.c2p;
      var c2p = document.createElement("c2p");
      c2p.innerHTML = "<code> Compactness Percentile: " + compactness_percentile + "</code>";
      stats.appendChild(c2p);

      var fairness_percentile = map.fp;
      var fp = document.createElement("fp");
      fp.innerHTML = "<code> Fairness Percentile: " + fairness_percentile + "</code>";
      stats.appendChild(fp);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);
      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var efficiency_gap = map.e;
      var e = document.createElement("e");
      e.innerHTML = "<code> Efficiency Gap: " + efficiency_gap + "</code>";
      stats.appendChild(e);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);
      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var districts = document.createElement("districts");
      districts.innerHTML = "<code> Districts: </code>";
      stats.appendChild(districts);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      for (var key in map.d) {
        if (map.d.hasOwnProperty(key)) {
          var d_votes = map.d[key];
          var r_votes = map.r[key];
          var dist = document.createElement("dist");
          dist.innerHTML = "<code> District " + key + " Democratic votes: " + d_votes + " Republican votes: " + r_votes + "</code> </br>";
          stats.appendChild(dist);
        }
      }

  }

  handle_click() {
    var competitiveness = parseInt(document.getElementById("competitiveness").value);
    var compactness = parseInt(document.getElementById("compactness").value);
    var fairness = parseInt(document.getElementById("fairness").value);
    var stateVal = document.getElementById("state").value;
    var url = 'https://test-gerry.herokuapp.com/test?competitiveness=' + competitiveness + '&compactness=' + compactness + '&fairness=' + fairness + '&state=' + stateVal
    //var url = 'http://localhost:3001/test?competitiveness=' + competitiveness + '&compactness=' + compactness + '&fairness=' + fairness + '&state=' + stateVal
    console.log(url)
    axios.get(url)
      .then(response => this.setState({image: response.data})).then(value => {
        //console.log(this.state.image)
        console.log(this.state.image.localeCompare('No Map!'))
        // if (this.state.image.localeCompare('No Map!') == 0) {
        //   this.found = 'No Map Found!'
        // } else {
        //   this.found = ''
        // }
      })
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
          {this.found}
        </div>
        <div className="stats">
          <div><code>District results after re-districting: </code></div>
        </div>
      </div>

    );
  }
}

export default App;
