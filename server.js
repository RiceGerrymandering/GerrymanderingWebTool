// import express JS module into app 
// and creates its variable. 
var express = require('express'); 
var app = express(); 
var fs = require('fs');
  
// Creates a server which runs on port 3000 and  
// can be accessed through localhost:3000 
app.listen(process.env.PORT || 3001, function() { 
    console.log('server running on port 3001'); 
} ) 
  
// url is of the form localhost:3000/test 
app.get('/test', test); 
  
function test(req, res) { 
    console.log("Got Request!")

    // Use child_process.spawn method from  
    // child_process module and assign it 
    // to variable spawn 
    var spawn = require("child_process").spawn; 
      
    // Parameters passed in spawn - 
    // 1. type_of_script 
    // 2. list containing Path of the script 
    //    and arguments for the script  

    var proc = spawn('python',["./rice/select_map.py", 
                            req.query.state,
                            req.query.fairness, 
                            req.query.competitiveness,
                            req.query.compactness] ); 
    console.log("Spawned Python!")
  
    // Takes stdout data from script which executed 
    // with arguments and send this data to res object 
    proc.on('exit', function (code, signal) { 
        console.log("Process Exited!")
        fs.readFile('rice/out.txt', 'utf8', function(err, contents) {
            console.log("Reading File!")
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
            res.send(contents.toString());
        });
    } ) 
} 