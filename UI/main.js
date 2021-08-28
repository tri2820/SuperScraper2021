const { app, BrowserWindow } = require('electron')
const path = require('path')
var fs = require('fs');

var dropdowns = {};
//dropdown["telsta"] = "AASAS"
//dropdown["telsta"] = "AASAS"
//dropdown["telsta"] = "AASAS"

// ^^^

// <li>Telstra</li>
// <ul>dsfds</ul>


//create function thenj call in index.html

// Creating Desktop Window and loading index.html 
function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })

  win.loadFile('index.html')

  win.webContents.once('dom-ready', () => {
    var fileData = path.join(__dirname, 'performance.csv');
    fs.readFile(fileData, 'utf8', function (err, filedata) {
      if (err) return console.log(err);
      var data = filedata.split("\n");
      data.splice(0, 1);
      for (var b = 0; b < data.length; b++) {
        var colData = data[b].split(",");
        var parts = colData[0].split(" ");
        if (parts[0] === "") {
          continue;
        }
        if (!(parts[0] in dropdowns)) {
          dropdowns[parts[0]] = [];
          //
          /*let code = `var parent = document.getElementById("dropdownid");
          let a = document.createElement("a").setAttribute("href", index.html);
          console.log(parent);
          a.innerHTML = "Test"
          parent.append(a);`*/

          /*
          let code = `var parent = document.getElementById("dropdownID");
            let a = document.createElement("A");
            a.href= "tes.html";
            a.innerHTML = "`+ colData[0].substring(parts[0].length + 1) + `";
            parent.append(a);`
          win.webContents.executeJavaScript(code);
          //win.webContents.executeJavaScript("alert(parent.length)");
          */
        }
        dropdowns[parts[0]].push(colData[0].substring(parts[0].length + 1));
      }
      //Append to html button
      //Hesta
      console.log(dropdowns["aware"].toString());

      let code = `var parent = document.getElementById("dropdownID");
        var dropdowns2 = `+JSON.stringify(dropdowns['hesta'])+`
        let nodes = dropdowns2.map(dropdown => {
        let a = document.createElement('A');
        a.textContent = dropdown;
        return a;
        });
        parent.append(...nodes);`
        win.webContents.executeJavaScript(code);

        //Aware
        let code2 = `var parent2 = document.getElementById("dropdownID2");
        var dropdowns3 = `+JSON.stringify(dropdowns['aware'])+`
        let nodes2 = dropdowns3.map(dropdown => {
        let a = document.createElement('A');
        a.textContent = dropdown;
        return a;
        });
        parent2.append(...nodes2);`
        win.webContents.executeJavaScript(code2);


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
  console.log(stdout);
})
// Intergrating python script with electron JS 
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

