var MongoClient = require('mongodb').MongoClient;
var url = "mongodb+srv://extractor:I62EK5HE5yBL59Yz@cluster0.tadma.mongodb.net/SuperScrapper?retryWrites=true&w=majority";

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
    console.log("mong1");
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
        });
      });

    console.log("mong2");
}

