const { app, BrowserWindow } = require("electron");
const { spawn } = require("child_process");

let flaskProcess;

function createWindow() {

    const win = new BrowserWindow({
        width: 1600,
        height: 1000,
        webPreferences: {
            nodeIntegration: false
        }
    });

    win.loadURL("http://127.0.0.1:10000");
}

app.whenReady().then(() => {

    flaskProcess = spawn(
        "python",
        ["../app.py"],
        {
            shell: true
        }
    );

    setTimeout(() => {
        createWindow();
    }, 3000);

});

app.on("window-all-closed", () => {

    if (flaskProcess) {
        flaskProcess.kill();
    }

    app.quit();
});