const { app, BrowserWindow } = require('electron')
const path = require('path')
var fs = require('fs');

var dropdowns = {};
//dropdown["telsta"] = "AASAS"
//dropdown["telsta"] = "AASAS"
//dropdown["telsta"] = "AASAS"

// Creating Desktop Window and loading index.html 
function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })
  win.openDevTools();
  win.loadFile('index.html')

  win.webContents.once('dom-ready', () => {
    var fileData = path.join(__dirname, 'performance.csv');
    fs.readFile(fileData, 'utf8', function (err, filedata) {
      if (err) return console.log(err);
      var data = filedata.split("\n");
      var keepRowHeader = data[0].split(",");
      data.splice(0, 1);
      for (var b = 0; b < data.length; b++) {
        var colData = data[b].split(",");
        var parts = colData[0].split(" ");
        if (parts[0] === "") {
          continue;
        }

        if (!(parts[0] in dropdowns)) {
          dropdowns[parts[0]] = [];
        }

        var itemName = colData[0].substring(parts[0].length + 1);
        var itemValues = [];
        var singleArrayCombinedValues = [];
        for (let index = 0; index < colData.length; index++) {
          var arrMonthValue = []; // ["Jan", 1.5]...
          if (index > 0) {
            arrMonthValue.push(keepRowHeader[index]);
            arrMonthValue.push(isNaN(parseFloat(colData[index])) ? 0 : parseFloat(colData[index]));
            singleArrayCombinedValues.push(arrMonthValue);
          }
        }
        itemValues.push(itemName);
        itemValues.push(singleArrayCombinedValues);
        dropdowns[parts[0]].push(itemValues);

        //dropdowns: Keys = hesta / aware / telstra
        // dropdowns["hesta"] = ["Conserva", "FSDDS", "SDSDS"]

        // dropdowns["hesta"] = [{ "Conservative" : [1, 2, 3, 4, 5] },  { "Super" : [1, 2, 3, 4, 5] },  ]

        // dropdowns["hesta"] = [{ "Conservative" : [["Jan", 1] , ["Feb", 2], ["Mar", 3], ["Apr", 4], ["Mey", 5]] },
      }
      //Append to html button
      //Hesta

      //var dropdowns2 = `+JSON.stringify(dropdowns['hesta'])+`
        //let nodes = dropdowns2.map(dropdown => {


      let code = `var parent = document.getElementById("dropdownID");
        var dropdowns2 = `+JSON.stringify(dropdowns['hesta'])+`
        let nodes = dropdowns2.map((dropdown, idx) => {
          let a = document.createElement('A');
          let key2 = dropdown[0];
          a.textContent = dropdown[0];
          a.dataset.key1 = 'hesta'
          a.dataset.key2 = idx;
          return a;
        });
        parent.append(...nodes);`
        win.webContents.executeJavaScript(code);

        //Aware
      let code2 = `var parent2 = document.getElementById("dropdownID2");
        var dropdowns3 = `+JSON.stringify(dropdowns['aware'])+`
        let nodes2 = dropdowns3.map(dropdown, idx => {
          let a = document.createElement('A');
          a.textContent = dropdown[1];
          a.dataset.key1 = 'aware'
          a.dataset.key2 = idx;
          return a;
        });
        parent2.append(...nodes2);`
        win.webContents.executeJavaScript(code2);

        //telsta
        let code3 = `var parent3 = document.getElementById("dropdownID3");
        var dropdowns4 = `+JSON.stringify(dropdowns['telstra'])+`
        let nodes3 = dropdowns4.map(dropdown => {
        let a = document.createElement('A');
        a.textContent = dropdown;
        return a;
        });
        parent3.append(...nodes3);`
        win.webContents.executeJavaScript(code3);
        

        let navBarClickHandler = `
          let dropdowns = `+JSON.stringify(dropdowns)+`;
          document.querySelectorAll("#dropdownID a").forEach(menu => 
            menu.addEventListener("click", function(){
              let key1 = this.dataset.key1;
              let key2 = this.dataset.key2;
              let columnHeader = [["month", "value"]];
              let data = columnHeader.concat(dropdowns[key1][key2][1]);
              var ChartData = google.visualization.arrayToDataTable(data);
    
              //Title for the chart
              var options = {
                title: 'Monthly Super Performance',
                curveType: 'function',
                legend: { position: 'bottom' }
              };
    
              var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));
    
              chart.draw(ChartData, options);
            })   
          ); 
        `;

        win.webContents.executeJavaScript(navBarClickHandler);
      // var iframe = document.createElement('iframe');
      // iframe.addAtributes("class", ".drpbns");
      // iframe.id = 'iframe';
      // iframe.style.display = 'none';
      // document.body.appendChild(iframe);
      // iframe.src = 'testing1.txt';
    });
  });
}
// Enabling browsing via desktop window 
app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})
// Intergrating python script with electron JS 
require('child_process').execFile("Users/priyankaram/super-scrapper/Extractor/extractor.py", [3000], (error, stdout, stderr) => {

  if (error) {

    console.log(error);

  }
  // console.log(stdout);
})
// Intergrating python script with electron JS 
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

