const { app, BrowserWindow } = require('electron')
const path = require('path')

// Creating Desktop Window and loading index.html 
function createWindow () {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })

  win.loadFile('index.html')
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