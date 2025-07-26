async function updateStatusLights(){
  try{
    const res = await fetch('/status');
    const data = await res.json();
    const container = document.getElementById('status-lights');
    if(container){
      container.innerHTML = '';
      for(const [name, ok] of Object.entries(data)){
        const a = document.createElement('a');
        a.href = '/?settings=' + name;
        a.onclick = function(e){
          if(typeof openSettings === 'function'){
            e.preventDefault();
            openSettings(name);
          }
        };
        const dot = document.createElement('div');
        dot.className = 'status-dot' + (ok ? ' green' : '');
        a.appendChild(dot);
        container.appendChild(a);
      }
    }
    for(const [name, ok] of Object.entries(data)){
      const node = document.getElementById('node-'+name);
      if(node){
        node.classList.toggle('green', ok);
        node.classList.toggle('red', !ok);
      }
    }
  }catch(e){
    console.error(e);
  }
}
updateStatusLights();
setInterval(updateStatusLights, 10000);

