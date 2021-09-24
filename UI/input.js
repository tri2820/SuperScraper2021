const MongoClient = require('mongodb').MongoClient;
const url = "mongodb+srv://dataInput:lOIIVKEKLoTtOdQH@cluster0.tadma.mongodb.net/SuperScrapper?retryWrites=true&w=majority";
const platform = require('process').platform;



function setup(){
    const myForm = document.getElementById("myForm");
    const csvFile = document.getElementById("csvFile");

    for(var i = 0; i < 60; i++){
        var men = document.getElementById('min');
        var option = document.createElement("option")
        option.text = i
        option.value = i
        men.add(option, i)
    }

    for (var i = 0; i < 24; i++) {
        var men = document.getElementById('hour');
        var option = document.createElement("option")
        option.text = i
        option.value = i
        men.add(option, i)
    }

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
                if (typeof csvApir === 'string') {
                    if (csvApir.length > 4) {
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
            alert("Database updated successfully!");
        };


        reader.readAsText(input);
    });
}

//Function to create local cache, mapping APIR codes to fund managers
function process(entry) {
    //cache object
    var cache = {}
    //Build cache
    //for each entry in the new data
    entry.forEach(function (info) {
        //check if the manager is already in the cache ... otherwise add it in
        if (info["manager"] in cache) {
            //Confirm the APIR is NOT already in the cache before adding
            if (cache[info["manager"]].includes(info["apir"][0])) {
                //console.log("Skipping...")

            } else {
                cache[info["manager"]].push(info["apir"][0])
                //cache[info["manager]"]
            }
        } else {
            //console.log("New")
            //console.log(info["manager"])
            cache[info["manager"]] = info.link;
            cache[info["manager"]].push(info.apir[0]);
        }
    });

    for (entry in cache) {
        checkMongo(entry, cache[entry])
    }
}

//function that builds & returns the correct format for a MongoDB object with the input data
function buildMongo(name, data) {
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
            },
            Investment: {
                restrict_text: [
                    '.+Investment.+',
                    '.+investment.+',
                ],
                filters: [
                    '.+product.disclosure.statement.+',
                    '.+pds.+',
                    '.+PDS.+',
                ]
            },
            FeesCosts: {
                restrict_text: [
                    '.+fees.costs.+',
                    '.+Fees.Costs.+',
                ],
                filters: [
                    '.+fees.costs.+',
                    '.+Fees.Costs.+',
                ]
            },
            Performance: {
                restrict_text: [
                    '.+performance.+',
                    '.+Performance.+',
                ],
                filters: [
                    '.+performance.+',
                    '.+Performance.+',
                ]
            },
            FactSheet: {
                restrict_text: [
                    '.+FactSheet.+',
                    '.+Fact Sheet.+',
                    '.+fact.sheet.+',
                ],
                'filters': [
                    '.+FactSheet.+',
                    '.+Fact Sheet.+',
                    '.+fact.sheet.+',
                ]
            },
        },
        traversal_filters: {
        },
        domain: {
            domain_file: `${name}`,
            domain_name: `${data[0]}`,
            start_url: `https://${data[0]}`,
            parse_select: "traverse",
            page_filters: {
            }
        },
        schedule_data: {
            last_traversed: 0,
            should_traverse: "True",
        }
    };

    for (let i = 1; i < data.length; i++) {
        console.log(data[i])
        var newFilter = {
            [data[i]]: [
                `${data[i]}`
            ]
        }
        Object.assign(template.domain.page_filters, newFilter);

    }
    console.log("Build Mongo: Built Template")
    console.log(template)
    return (template)
}

//Passes and handles mongo information
function checkMongo(name, data) {
    var manId = name + "_site_traversal"
    //Check if the fund manager exists
    MongoClient.connect(url, function (err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        var filter = { _id: manId }
        dbo.collection("site_traverse_data").findOne(filter, function (err, result) {
            if (err) throw err;
            if (typeof result === "object") {
                console.log(manId + " found")
                mongoProcess(manId, name, data)
            } else {
                console.log(manId + " not found")
                console.log("Inserting new document")
                mongoInsert(buildMongo(name, data))
            };
            db.close();
        });
    });
}

//Function that gets remote data and processes it
function mongoProcess(manId, name, data) {
    var existing = [];
    MongoClient.connect(url, function (err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        dbo.collection("site_traverse_data").find({ _id: manId }, { projection: { domain: 1 } }).toArray(function (err, result) {
            if (err) throw err;
            existing = result[0];
            for (i in result[0].domain.page_filters) {
                console.log("Mongo Processing Function loop")
                console.log(result[0])
                data.push(result[0].domain.page_filters[i][0])
            }
            db.close();
            mongoUpdate(buildMongo(name, data))
        });
    });
}

function mongoUpdate(data) {
    console.log(data)
    MongoClient.connect(url, function (err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        var myquery = { _id: `${data._id}` };
        dbo.collection("site_traverse_data").replaceOne(myquery, data, function (err, res) {
            if (err) throw err;
            console.log("1 document updated");
            db.close();
        });
    });
}

function mongoInsert(data) {
    console.log(data)
    MongoClient.connect(url, function (err, db) {
        if (err) throw err;
        var dbo = db.db("SuperScrapper");
        dbo.collection("site_traverse_data").insertOne(data, function (err, res) {
            if (err) throw err;
            console.log("1 document updated");
            db.close();
        });
    });
}

function schedule() {
    var day = document.getElementById("day").value
    var hour = document.getElementById("hour").value
    var min = document.getElementById("min").value
    var plist = `<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.scraper.super</string>
            <key>WorkingDirectory</key>
            <string>/Applications/SuperScraper/UI</string>
            <key>ProgramArguments</key>
            <array>
                <string>/usr/local/bin/python3.9</string>
                <string>../Extractor/extractor.py</string>
            </array>
            <key>StandardOutPath</key>
            <string>/Applications/SuperScraper/scraper.stdout</string>
            <key>StandardErrorPath</key>
            <string>/Applications/SuperScraper/scraper.stderr</string>
            <key>StartCalendarInterval</key>
            <dict>
                <key>Weekday</key>
                <integer>${day}</integer>
                <key>Hour</key>
                <integer>${hour}</integer>
                <key>Minute</key>
                <integer>${min}</integer>
            </dict>
        </dict>
    </plist>`
    var fs = require('fs')
    var user = require("os").userInfo().username
    var uid = require("os").userInfo().uid
    console.log(uid)
    var dir = `/Users/${user}/Library/LaunchAgents`
    console.log(dir)
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true })
    }
    fs.writeFile(dir + "/superScraper.plist", plist, function (err, file) {
        if (err) throw err;
        console.log('Saved!');
    })
    console.log(plist)
    var unload = `launchctl unload ${dir}/superScraper.plist`
    const { exec } = require("child_process");

    exec(unload, (error, stdout, stderr) => {
        if (error) {
            console.log(`error: ${error.message}`);
            return;
        }
        if (stderr) {
            console.log(`stderr: ${stderr}`);
            return;
        }
        console.log(`stdout: ${stdout}`);
    });
    var create = `launchctl bootstrap gui/${uid} ${dir}/superScraper.plist`

    exec(create, (error, stdout, stderr) => {
        if (error) {
            console.log(`error: ${error.message}`);
            return;
        }
        if (stderr) {
            console.log(`stderr: ${stderr}`);
            return;
        }
        console.log(`stdout: ${stdout}`);
    });
    var load = `launchctl load ${dir}/superScraper.plist`

    exec(load, (error, stdout, stderr) => {
        if (error) {
            console.log(`error: ${error.message}`);
            return;
        }
        if (stderr) {
            console.log(`stderr: ${stderr}`);
            return;
        }
        console.log(`stdout: ${stdout}`);
    });
}

fundManagers = []
function buildFundManagers() {
    const fs = require('fs')
    //var fundManagers = []
    var names = []
    fs.readFile('./fund_managers.csv', 'utf8', (err, jsonString) => {
        if (err) {
            console.log("File read failed:", err)
            return
        }
        //console.log('File data:', jsonString)
        var rows = jsonString.split("\r\n")
        var x = 0
        //console.log(rows)
        for (var i = 1; i < rows.length; i++) {
            var curRow = rows[i].split(",")
            //console.log(curRow)
            var man = curRow[0]
            var apir = curRow[1]
            var name = curRow[2]
            var perfFee = curRow[3]
            var manFee = curRow[4]
            var adminFee = curRow[5]
            var spread = curRow[6]
            var nav = curRow[7]
            var performance = curRow[8]
            var alloc = curRow[9]
            var range = curRow[10]
            var topHold = curRow[11]
            var botHold = curRow[12]
            var clsSize = curRow[13]
            var fundSize = curRow[14]
            var strat = curRow[15]
            //console.log(man, ": ", apir)
            newFund = [apir, name, perfFee, manFee, adminFee, spread, nav, performance, alloc, range, topHold, botHold, clsSize, fundSize, strat]
            //console.log(newFund)
            if (!(man in fundManagers)) {
                fundManagers[man] = []
                names.push(man)
                //var option = document.createElement("option")
                //option.text = man
                //menu.add(option, x)
                x++;
            }
            fundManagers[man].push(newFund)
        }


        names.sort()
        var menu = document.getElementById("fundManagers")
        for (i = 0; i < names.length; i++) {
            var option = document.createElement("option")
            option.text = names[i]
            option.value = names[i]
            menu.add(option, i)
        }




    }
    )
};

function updateManager() {
    var man = document.getElementById("fundManagers").value
    var funds = fundManagers[man]
    var table = document.getElementById("dataDisp")
    if (table.rows.length > 1) {
        console.log("Rows: " + table.rows.length)
        while (table.rows.length > 1) {
            table.deleteRow(1)
        }
    }
    for (var i = 0; i < funds.length; i++) {
        var tr = document.createElement("tr")
        for (var j = 0; j < funds[i].length; j++) {
            console.log(funds[i][j])
            var td = tr.insertCell()
            td.appendChild(document.createTextNode(funds[i][j]))
        }
        table.appendChild(tr)
    }
}


function getCmd() {
    //var platform = process.platform;
    if(platform === 'win32'){
        console.log("WINDOWS")
        return("..\\install\\python_install\\python")
    }else if (platform === 'darwin'){
        console.log("MAC")
        return("python3")
    }
}
function extract() {
    var cmd = getCmd()
    console.log("Extracting...")
    var python = require('child_process').spawn(cmd, ['../Extractor/extractor.py'])
    python.stdout.on('data', function (data) {
        console.log("Python response: ", data.toString('utf8'));
    });

    python.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    python.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
        alert("Extraction complete!")
    });
}

function scrape() {
    var cmd = getCmd()
    console.log("Scraping... This will take a while")
    var python = require('child_process').spawn(cmd, ['../run_scraper.py'])
    python.stdout.on('data', function (data) {
        console.log("Python response: ", data.toString('utf8'));
    });

    python.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });
}