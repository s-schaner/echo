async function updateStatusLights(){
  try{
    const res = await fetch('/status');
    const data = await res.json();
    const container = document.getElementById('status-lights');
    if(container){
      container.innerHTML = '';
      for(const [name, ok] of Object.entries(data)){
        const dot = document.createElement('div');
        dot.className = 'status-dot' + (ok ? ' green' : '');
        container.appendChild(dot);
      }
    }
    for(const [name, ok] of Object.entries(data)){
      const fieldDot = document.getElementById('form-status-' + name);
      if(fieldDot){
        fieldDot.className = 'status-dot' + (ok ? ' green' : '');
      }
    }
  }catch(e){
    console.error(e);
  }
}
updateStatusLights();
setInterval(updateStatusLights, 10000);

