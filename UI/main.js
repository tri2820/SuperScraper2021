const { app, BrowserWindow } = require('electron')
const path = require('path')


// Creating Desktop Window and loading index.html 
function createWindow () {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false
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
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

function extract(){
  console.log("Extracting...")
}