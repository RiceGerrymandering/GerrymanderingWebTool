
// import express JS module into app 
// and creates its variable. 
var express = require('express'); 
var app = express(); 
var fs = require('fs');
  
// Creates a server which runs on port 3000 and  
// can be accessed through localhost:3000 
app.listen(3001, function() { 
    console.log('server running on port 3001'); 
} ) 
  
// Function callName() is executed whenever  
// url is of the form localhost:3000/name 
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
      
    // E.g : http://localhost:3000/name?firstname=Mike&lastname=Will 
    // so, first name = Mike and last name = Will 
    var process = spawn('python',["./test.py", 
                            req.query.competitiveness, 
                            req.query.compactness,
                            req.query.fairness] ); 
  
    // Takes stdout data from script which executed 
    // with arguments and send this data to res object 
    process.stdout.on('data', function(data) { 
        console.log(data)
        fs.readFile('out.txt', 'utf8', function(err, contents) {
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
            res.send(contents.toString());
        });
        //res.send(data.toString()); 
    } ) 
} 