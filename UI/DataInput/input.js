var MongoClient = require('mongodb').MongoClient;
var url = "mongodb+srv://extractor:I62EK5HE5yBL59Yz@cluster0.tadma.mongodb.net/SuperScrapper?retryWrites=true&w=majority";

function notify(){
    var site = document.getElementById("site").value;
    //var url = document.getElementById("url").value;
    var apir = document.getElementById("apir").value;
    
    var output = document.getElementById('data')
    output.innerHTML = site + "<br />" + url + "<br />" + apir;
}

function mong(){
    console.log("mong1");
    
    MongoClient.connect(url, function(err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        dbo.collection("offerings").find({fund_id:"hesta"}).toArray(function(err, result) {
          if (err) throw err;
          console.log(result);
        });
      });

    console.log("mong2");
}

