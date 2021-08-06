const MongoClient = require('mongodb').MongoClient;
const url = "mongodb+srv://dataInput:lOIIVKEKLoTtOdQH@cluster0.tadma.mongodb.net/SuperScrapper?retryWrites=true&w=majority";



function notify(){
    var site = document.getElementById("site").value;
    var domain = document.getElementById("url").value;
    var apir = document.getElementById("apir").value;
    
    var output = document.getElementById('data')
    output.innerHTML = site + "<br />" + url + "<br />" + apir;
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
                        domain_file: `${site}`,
                        domain_name: `${domain}`,
                        start_url: `https://${domain}`,
                        parse_select: "traverse",
                        page_filters: {
                            [apir]: [
                            `${apir}`
                            ]
                        }
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
        contents.forEach(function (item, index) {
            /* Build array for each item
            0 = Fund Name
            1 = APIR
            2 = Fund Manager
            3 = URL
            */ 
            var line = item.split(",")
            var csvApir = line[1];
            var manager = line[2];
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
                    submitData(manager, csvApir, link);
                        
                }
                
            }
        })
        document.write(JSON.stringify(contents));
        };

        reader.readAsText(input);
    });
}

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
        }
    };
    console.log(info.domain.domain_file)
    MongoClient.connect(url, function(err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        var filter = {"_id": `${info._id}`}
        var options = { upsert: true };
        dbo.collection("site_traverse_data").updateOne(filter, {$set: {info}}, options, function(err, result) {
            if (err) throw err;
            console.log(result);
            console.log("Database updated!")
        });
    });
    console.log(info)
}
