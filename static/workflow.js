function setStepStatus(name, status){
  const box = document.getElementById('box-'+name);
  if(box){
    box.classList.remove('pending','active','complete');
    if(status) box.classList.add(status);
  }
  const arrow = document.getElementById('arrow-'+name);
  if(arrow){
    arrow.classList.remove('pending','active','complete');
    if(status) arrow.classList.add(status);
  }
}

function resetWorkflow(){
  ['ui','planner','validator','executor','shell'].forEach(n => setStepStatus(n,''));
}
