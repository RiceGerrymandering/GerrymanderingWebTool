import React, { Component } from 'react';
import './App.css';
import axios from 'axios'

class App extends Component {

  constructor() {
    super()
    this.state = {
      image: '',
      graph1: '',
      graph2: '',
      stats: true
    }
    this.handle_click = this.handle_click.bind(this)
  }

    post_stats(map) {
      var stats = document.getElementsByClassName("stats")[0];
      while (stats.firstChild) {
        stats.removeChild(stats.firstChild);
      } 

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var fairness_score = map.f;
      var f = document.createElement("f");
      f.innerHTML = "<code> Fairness score: " + fairness_score + "</code>";
      stats.appendChild(f);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var competitiveness_score = map.c1;
      var c1 = document.createElement("c1");
      c1.innerHTML = "<code> Competitiveness score: " + competitiveness_score + "</code>";
      stats.appendChild(c1);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var compactness_score = map.c2;
      var c2 = document.createElement("c2");
      c2.innerHTML = "<code> Compactness score: " + compactness_score + "</code>";
      stats.appendChild(c2);

//      var line_br = document.createElement("br");
//      line_br.innerHTML = "</br>"
//      stats.appendChild(line_br);
//      var line_br = document.createElement("br");
//      line_br.innerHTML = "</br>"
//      stats.appendChild(line_br);
//
//      var fairness_percentile = map.fp;
//      var fp = document.createElement("fp");
//      fp.innerHTML = "<code> Fairness Percentile: " + fairness_percentile + "</code>";
//      stats.appendChild(fp);
//
//      var competitiveness_percentile = map.c1p;
//      var c1p = document.createElement("c1p");
//      c1p.innerHTML = "<code> Competitiveness Percentile: " + competitiveness_percentile + "</code>";
//      stats.appendChild(c1p);
//
//      var compactness_percentile = map.c2p;
//      var c2p = document.createElement("c2p");
//      c2p.innerHTML = "<code> Compactness Percentile: " + compactness_percentile + "</code>";
//      stats.appendChild(c2p);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);
      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var efficiency_gap = map.e;
      var e = document.createElement("e");
      e.innerHTML = "<code> Efficiency gap (in favor of Democrats): " + efficiency_gap + "</code>";
      stats.appendChild(e);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);
      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var total_dseats = map.tds;
      var total_rseats = map.trs;
      var total_seats = document.createElement("total_seats");
      total_seats.innerHTML = "<code> Democratic seats won: " + total_dseats + ", Republican seats won: " + total_rseats + "</code>";
      stats.appendChild(total_seats);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var total_dvotes = map.tdv;
      var total_rvotes = map.trv;
      var total_votes = document.createElement("total_votes");
      total_votes.innerHTML = "<code> Total Democratic votes: " + total_dvotes + ", Total Republican votes: " + total_rvotes + "</code";
      stats.appendChild(total_votes);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      var districts = document.createElement("districts");
      districts.innerHTML = "<code> District votes: </code>";
      stats.appendChild(districts);

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

      for (var key in map.d) {
        if (map.d.hasOwnProperty(key)) {
          var d_votes = map.d[key];
          var r_votes = map.r[key];
          var dist = document.createElement("dist");
          if (d_votes >= r_votes) {
            dist.innerHTML = "<code> District " + key + ": Democratic votes: <span style='color:#008000'>" + d_votes +
                "</span>, Republican votes: <span style='color:#FF0000'>" + r_votes + "</span></code> </br>";
          } else {
            dist.innerHTML = "<code> District " + key + ": Democratic votes: <span style='color:#FF0000'>" + d_votes +
                "</span>, Republican votes: <span style='color:#008000'>" + r_votes + "</span></code> </br>";
          }
          stats.appendChild(dist);
        }
      }

      var line_br = document.createElement("br");
      line_br.innerHTML = "</br>"
      stats.appendChild(line_br);

  }

  handle_click() {
    var competitiveness = document.getElementById("competitiveness").value;
    var compactness = document.getElementById("compactness").value;
    var fairness = document.getElementById("fairness").value;
    var stateVal = document.getElementById("state").value;
    var fairness_type = document.getElementById("fairness_type").value;
    if (fairness != 0) {
      if (fairness_type == "Favor Democrats") {
        fairness = parseInt(fairness, 10) + 5;
      }
      if (fairness_type == "Favor Republicans") {
        fairness = parseInt(fairness, 10) + 10;
      }
    }
    //var url = 'https://test-gerry.herokuapp.com/test?competitiveness=' + competitiveness + '&compactness=' + compactness + '&fairness=' + fairness + '&state=' + stateVal
    var url = 'http://localhost:3001/test?competitiveness=' + competitiveness + '&compactness=' + compactness + '&fairness=' + fairness + '&state=' + stateVal
    //console.log(url)
    axios.get(url)
      .then(response => {
        //console.log(response.data == 'No Map!')
        if (response.data != 'No Map!') {
          var map = fairness + competitiveness + compactness
          this.setState({image: '', graph1: '', graph2: '', stats : true})
          this.post_stats(response.data.stats[map])
          this.setState({image: response.data.img, graph1: response.data.graph1, graph2: response.data.graph2, stats : true})
        } else {
          this.setState({image: 'data:image/jpeg;base64,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', graph1: '', graph2: '', stats : false})
        }
      })
  }

  render() {
    var src = this.state.image
    var graph1 = this.state.graph1
    var graph2 = this.state.graph2
    var stats = this.state.stats
    return (
      <div className="App">
        <header className="App-header">
        </header>
        <div className="Toggle-Boxes">
         <code>Fairness: </code>
          <select id="fairness" >
            <option>0</option>
            <option>1</option>
            <option>2</option>
            <option selected="selected">3</option>
            <option>4</option>
            <option>5</option>
          </select>
          <code> Fairness type: </code>
          <select id="fairness_type">
            <option selected="selected">Favor neither</option>
            <option>Favor Democrats</option>
            <option>Favor Republicans</option>
          </select>
          <code> Competitiveness: </code>
          <select id="competitiveness">
            <option>0</option>
            <option>1</option>
            <option>2</option>
            <option selected="selected">3</option>
            <option>4</option>
            <option>5</option>
          </select>
          <code> Compactness: </code>
          <select id="compactness">
            <option>0</option>
            <option>1</option>
            <option>2</option>
            <option selected="selected">3</option>
            <option>4</option>
            <option>5</option>
          </select>
          <code> State: </code>
          <select id="state">
            <option>NH</option>
            <option>TX</option>
          </select>
        </div>
        <button className='button' onClick={this.handle_click}>Redistrict</button>
        <div>
          <img src={src}/>
          { stats ?  <div className="stats"><div><code>Redistricting results: </code></div></div> : null }
          <img src={graph1}/>
          <img src={graph2}/>
        </div>
      </div>

    );
  }
}

export default App;
