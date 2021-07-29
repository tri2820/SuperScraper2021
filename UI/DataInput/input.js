import { MongoClient } from 'mongodb'
const uri = "mongodb+srv://<dataInput>:<EfzSbrRahyKau9BD>@cluster0.tadma.mongodb.net/myFirstDatabase?retryWrites=true&w=majority";
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

function notify(){
    var site = document.getElementById("site").value;
    var url = document.getElementById("url").value;
    var apir = document.getElementById("apir").value;
    
    var output = document.getElementById('data')
    output.innerHTML = site + "<br />" + url + "<br />" + apir;
}

function mong(){
    console.log("mong1");
    
    client.connect(err => {
        const collection = client.db("superScrapper").collection("site_traverse_data");
        // perform actions on the collection object
        var cursor = collection.find({});
        cursor.nextObject(function(err, item) {
            console.log(item);
        });
        client.close();
    });

    console.log("mong2");
}
