const dashboard = document.querySelector('.dashboard');
if(dashboard){
  let dragPane = null;
  dashboard.querySelectorAll('.pane').forEach(pane => {
    const header = pane.querySelector('h1,h2');
    if(header){
      header.draggable = true;
      header.style.cursor = 'move';
      header.addEventListener('dragstart', e => {
        dragPane = pane;
        e.dataTransfer.setData('text/plain','');
      });
    }
    pane.addEventListener('dragover', e => e.preventDefault());
    pane.addEventListener('drop', e => {
      e.preventDefault();
      if(!dragPane || dragPane === pane) return;
      const panes = Array.from(dashboard.querySelectorAll('.pane'));
      const srcIndex = panes.indexOf(dragPane);
      const tgtIndex = panes.indexOf(pane);
      if(srcIndex < tgtIndex){
        dashboard.insertBefore(dragPane, pane.nextSibling);
      }else{
        dashboard.insertBefore(dragPane, pane);
      }
      dragPane = null;
    });
  });
}
