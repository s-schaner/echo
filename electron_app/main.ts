import { app, BrowserWindow } from 'electron';
import path from 'path';
import { AuroraLLMNode, AuroraExecNode, SymbolicNode, saveFlow } from './AuroraShellModule';

function createWindow() {
  const win = new BrowserWindow({ width: 800, height: 600, webPreferences: { nodeIntegration: true } });
  win.loadFile(path.join(__dirname, 'index.html'));
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// Example flow setup
const flow = {
  nodes: [
    new AuroraLLMNode('llm', 'http://localhost:1234/v1/chat/completions'),
    new SymbolicNode('sym', 'πSD'),
    new AuroraExecNode('exec')
  ]
};

saveFlow(flow, 'example.aurorascript');
