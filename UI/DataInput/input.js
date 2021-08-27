const MongoClient = require('mongodb').MongoClient;
const url = "mongodb+srv://dataInput:lOIIVKEKLoTtOdQH@cluster0.tadma.mongodb.net/SuperScrapper?retryWrites=true&w=majority";



function notify(){
    var site = document.getElementById("site").value;
    var domain = document.getElementById("url").value;
    var apir = document.getElementById("apir").value;
    
    var output = document.getElementById('data')
    output.innerHTML = site + "<br />" + url + "<br />" + apir;
}


function setup(){
    const myForm = document.getElementById("myForm");
    const csvFile = document.getElementById("csvFile");

    myForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var input = csvFile.files[0];
        var reader = new FileReader();

        reader.onload = function (e) {
        var text = e.target.result;
        /*Build array of items split on newlines
        IMPORTANT: CURRENTLY JUST USES EXCELS \r\n
        SHOULD BE MADE MORE FLEXIBLE*/
        var contents = text.split("\r\n")
        var info = []
        contents.forEach(function (item, index) {
            /* Build array for each item
            0 = Fund Name
            1 = APIR
            2 = Fund Manager
            3 = URL
            */ 
            var line = item.split(",")
            var csvApir = line[1];
            var manager = line[2]
            var link = line[3];

            
            /*Yeah checking if the type is explicitly equivalent to the string string is good and normal
            What a great language*/
            if(typeof csvApir === 'string'){
                if(csvApir.length > 4){
                    /*Clean out link stuff*/
                    link = link.replace("https://", "")
                    link = link.replace("http://", "")

                    /*remove spaces from name*/
                    manager = manager.replaceAll(" ", "")
                    // Build object up
                    var newData = {}
                    //submitData(manager, csvApir, link);
                    newData.manager = manager.toLowerCase();;
                    //Get APIR in an array, so it can be pushed onto a list in the next function
                    newData.apir = csvApir.split(" ");
                    newData.link = link.split(" ");

                    //console.log(newData)
                    info.push(newData);
                        
                }
                
            }
        })
        //console.log(info)
        process(info);
        document.write(JSON.stringify(contents));
        };
       

        reader.readAsText(input);
    });
}

//Function to create local cache, mapping APIR codes to fund managers
function process(entry){
    //cache object
    var cache = {}
    //Build cache
    //for each entry in the new data
    entry.forEach(function(info){
        //check if the manager is already in the cache ... otherwise add it in
        if(info["manager"] in cache){
            //Confirm the APIR is NOT already in the cache before adding
            if(cache[info["manager"]].includes(info["apir"][0])){
                //console.log("Skipping...")
                
            }else{
                cache[info["manager"]].push(info["apir"][0])
                //cache[info["manager]"]
            }
        }else{
            //console.log("New")
            //console.log(info["manager"])
            cache[info["manager"]]= info.link;
            cache[info["manager"]].push(info.apir[0]);
        }
    });

    for(entry in cache){
        checkMongo(entry, cache[entry])
    }
}

//function that builds & returns the correct format for a MongoDB object with the input data
function buildMongo(name, data){
    console.log("Build Mongo Function")
    console.log(data)
    var template = {
        _id: `${name}_site_traversal`,
        file_extraction_rules: {
            deny_extensions: [
                "7z",
                "7zip",
                "bz2",
                "rar",
                "tar",
                "tar.gz",
                "xz",
                "zip",
                "mng",
                "pct",
                "bmp",
                "gif",
                "jpg",
                "jpeg",
                "png",
                "pst",
                "psp",
                "tif",
                "tiff",
                "ai",
                "drw",
                "dxf",
                "eps",
                "ps",
                "svg",
                "cdr",
                "ico",
                "mp3",
                "wma",
                "ogg",
                "wav",
                "ra",
                "aac",
                "mid",
                "au",
                "aiff",
                "3gp",
                "asf",
                "asx",
                "avi",
                "mov",
                "mp4",
                "mpg",
                "qt",
                "rm",
                "swf",
                "wmv",
                "m4a",
                "m4v",
                "flv",
                "webm",
                "xls",
                "xlsx",
                "ppt",
                "pptx",
                "pps",
                "doc",
                "docx",
                "odt",
                "ods",
                "odg",
                "odp",
                "css",
                "exe",
                "bin",
                "rss",
                "dmg",
                "iso",
                "apk"
            ],
            allow: [],
            content_types: [
                "application/pdf"
                ],
            restrict_text: [
                ".+disclosure.statement.+",
                ".+product.disclosure.statement.+",
                ".+pds.+",
                ".+PDS.+"
            ],
            filters: [
                ".+product.disclosure.statement.+",
                ".+pds.+",
                ".+PDS.+"
            ]
        },
        domain: {
            domain_file: `${name}`,
            domain_name: `${data[0]}`,
            start_url: `https://${data[0]}`,
            parse_select: "traverse",
            page_filters: {
            }
        }
    };

    for(let i = 1; i < data.length; i++){
        console.log(data[i])
        var newFilter = {
            [data[i]] : [
                `${data[i]}`
            ]
        }
        Object.assign(template.domain.page_filters, newFilter);

    }
    console.log("Build Mongo: Built Template")
    console.log(template)
    return(template)
}

//Passes and handles mongo information
function checkMongo(name, data){
    var manId = name + "_site_traversal"
    //Check if the fund manager exists
    MongoClient.connect(url, function(err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        var filter = {_id: manId}
        dbo.collection("site_traverse_data").findOne(filter, function(err, result) {
          if (err) throw err;
          if(typeof result === "object"){
              console.log(manId + " found")
              mongoProcess(manId, name, data)
          }else{
              console.log(manId + " not found")
              console.log("Inserting new document")
              mongoInsert(buildMongo(name, data))
          };
          db.close();
        });
      });
}

//Function that gets remote data and processes it
function mongoProcess(manId, name, data){
    var existing = [];
    MongoClient.connect(url, function(err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        dbo.collection("site_traverse_data").find({_id: manId}, { projection: { domain: 1 } }).toArray(function(err, result) {
            if (err) throw err;
            existing = result[0];
            for(i in result[0].domain.page_filters){
                console.log("Mongo Processing Function loop")
                console.log(result[0])
                data.push(result[0].domain.page_filters[i][0])
            }
            db.close();
            mongoUpdate(buildMongo(name, data))
        });
      });
}

function mongoUpdate(data){
    console.log(data)
    MongoClient.connect(url, function(err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        var myquery = {_id: `${data._id}` };
        dbo.collection("site_traverse_data").replaceOne(myquery, data, function(err, res) {
          if (err) throw err;
          console.log("1 document updated");
          db.close();
        });
      });
}

function mongoInsert(data){
    console.log(data)
    MongoClient.connect(url, function(err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        dbo.collection("site_traverse_data").insertOne(data, function(err, res) {
          if (err) throw err;
          console.log("1 document updated");
          db.close();
        });
      });
}
//<!---------- OLD FUNCTIONS BELOW -----------------------!>

function submitData(manager, csvApir, link){
    console.log(`submitting data for ${csvApir}`)
    getMongoData(manager, csvApir, link)
};

function getMongoData(manager, csvApir, link){
    var info = {
        _id: `${manager}_site_traversal`,
        file_extraction_rules: {
            deny_extensions: [
                "7z",
                "7zip",
                "bz2",
                "rar",
                "tar",
                "tar.gz",
                "xz",
                "zip",
                "mng",
                "pct",
                "bmp",
                "gif",
                "jpg",
                "jpeg",
                "png",
                "pst",
                "psp",
                "tif",
                "tiff",
                "ai",
                "drw",
                "dxf",
                "eps",
                "ps",
                "svg",
                "cdr",
                "ico",
                "mp3",
                "wma",
                "ogg",
                "wav",
                "ra",
                "aac",
                "mid",
                "au",
                "aiff",
                "3gp",
                "asf",
                "asx",
                "avi",
                "mov",
                "mp4",
                "mpg",
                "qt",
                "rm",
                "swf",
                "wmv",
                "m4a",
                "m4v",
                "flv",
                "webm",
                "xls",
                "xlsx",
                "ppt",
                "pptx",
                "pps",
                "doc",
                "docx",
                "odt",
                "ods",
                "odg",
                "odp",
                "css",
                "exe",
                "bin",
                "rss",
                "dmg",
                "iso",
                "apk"
            ],
            allow: [],
            content_types: [
                "application/pdf"
                ],
            restrict_text: [
                ".+disclosure.statement.+",
                ".+product.disclosure.statement.+",
                ".+pds.+",
                ".+PDS.+"
            ],
            filters: [
                ".+product.disclosure.statement.+",
                ".+pds.+",
                ".+PDS.+"
            ]
        },
        domain: {
            domain_file: `${manager}`,
            domain_name: `${link}`,
            start_url: `https://${link}`,
            parse_select: "traverse",
            page_filters: {
                [csvApir]: [
                `${csvApir}`
                ]
            }
        },
        filtered_file_urls: {
     
        },
        schedule_data: {
            last_traversed: 0,
            should_traverse: "True",
        }
    };
    console.log(info.domain.domain_file)
    MongoClient.connect(url, function(err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        var filter = {"_id": `${info._id}`}
        var options = { upsert: true };
        console.log("Counting ...")
        var count = dbo.collection("site_traverse_data").findOne(filter).then(console.log(response))
        // dbo.collection("site_traverse_data").updateOne(filter, {$set: {info}}, options, function(err, result) {
        //     if (err) throw err;
        //     console.log(result);
        //     console.log("Database updated!")
        // });
    });
    console.log(info)


    /*
    1. Check if _id gets a match
    yes? get domain{pagefilters} -> append APIR: "APIR" -> Update _id
    no? go new

    */
}

function mong(){
    var site = document.getElementById("site").value.toLowerCase().replace(" ", "");
    var domain = document.getElementById("url").value.toLowerCase();
    var apir = document.getElementById("apir").value.toUpperCase();
    console.log("inserting into database ...");
    var newObj = {
        _id: `${site}_site_traversal`,
        file_extraction_rules: {
            deny_extensions: [
                "7z",
                "7zip",
                "bz2",
                "rar",
                "tar",
                "tar.gz",
                "xz",
                "zip",
                "mng",
                "pct",
                "bmp",
                "gif",
                "jpg",
                "jpeg",
                "png",
                "pst",
                "psp",
                "tif",
                "tiff",
                "ai",
                "drw",
                "dxf",
                "eps",
                "ps",
                "svg",
                "cdr",
                "ico",
                "mp3",
                "wma",
                "ogg",
                "wav",
                "ra",
                "aac",
                "mid",
                "au",
                "aiff",
                "3gp",
                "asf",
                "asx",
                "avi",
                "mov",
                "mp4",
                "mpg",
                "qt",
                "rm",
                "swf",
                "wmv",
                "m4a",
                "m4v",
                "flv",
                "webm",
                "xls",
                "xlsx",
                "ppt",
                "pptx",
                "pps",
                "doc",
                "docx",
                "odt",
                "ods",
                "odg",
                "odp",
                "css",
                "exe",
                "bin",
                "rss",
                "dmg",
                "iso",
                "apk"
            ],
            allow: [
            ],
            content_types: [
                "application/pdf"
            ],
        },
        file_filters: {
            PDS: {
                restrict_text: [
                '.+product.disclosure.statement.+',
                '.+pds.+',
                '.+PDS.+',
                ],
                filters: [
                    '.+product.disclosure.statement.+',
                    '.+pds.+',
                    '.+PDS.+',
                ]
            }
        },
        "traversal_filters": {
        },
        domain: {
            domain_file: `${site}`,
            domain_name: `${domain}`,
            start_url: `https://${domain}`,
            parse_select: "traverse",
            page_filters: {
                [apir]: [
                `${apir}`
                ]
            }
        },
        filtered_file_urls: {
     
        },
        schedule_data: {
            last_traversed: 0,
            should_traverse: "True",
        }
    };

    console.log(newObj);
    MongoClient.connect(url, function(err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        dbo.collection("site_traverse_data").insertOne(newObj, function(err, result) {
          if (err) throw err;
          console.log(result);
          console.log("Database updated!")
          document.location.href="https://cloud.mongodb.com/v2/60653aa7a8fb40147a2882e8#metrics/replicaSet/60653ba8dad21c1b3cb5d799/explorer/SuperScrapper";

        });
      });

}
