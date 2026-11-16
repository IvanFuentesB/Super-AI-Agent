"use strict";
// Fixed local UI adapter. It owns no executor, permission service or native input.
(function(root){
 const states=new Set(["created","awaiting_permission","running","stopping","stopped","expired","succeeded","failed","uncertain"]);
 const active=task=>task&&["created","awaiting_permission","running","stopping"].includes(task.state);
 const validId=value=>typeof value==="string"&&/^[A-Za-z0-9_-]{1,128}$/.test(value);
 // A bounded UX grammar, not a planner or an authorization mechanism.
 function noteInput(value,mode){
  if(!["text","task"].includes(mode))throw Error("Choose Task instruction or Literal note text.");
  if(typeof value!=="string"||!value.trim())throw Error("Enter a task or note text first.");
  if(/[\x00-\x1f\x7f\u2028\u2029]/.test(value))throw Error("Use a single line without control characters.");
  if(value.length>(mode==="task"?650:500))throw Error(mode==="task"?"Keep the task instruction within 650 characters.":"Keep note text within 500 characters.");
  if(mode==="task"){
   const match=/^(?:please\s+)?(?:create|write|make)\s+(?:(?:a|one)\s+)?(?:(?:new|temporary)\s+)?note(?:\s+(?:saying|that says|with (?:the )?text)\s+|\s*:\s*)(.+)$/i.exec(value.trim());
   if(!match)throw Error('Only a temporary note is supported. Try: Create a note saying "Check the release plan". Other tasks were not submitted.');
   value=match[1].trim();
   const closing={"\"":"\"","'":"'","“":"”","‘":"’"}[value[0]];
   if(closing){
    if(value.length<2||!value.endsWith(closing)||value.slice(1,-1).includes(closing))throw Error("Use one matching quote pair around note text, with nothing after it; or choose Literal note text.");
    value=value.slice(1,-1);
   }
  }
  if(!value.trim()||value.length>500)throw Error("Note content must contain 1–500 characters.");
  return value;
 }
 // One reading of a task's state for the status line, progress line, steps and navigation badge.
 const verified=task=>task?.state==="succeeded"&&task.verification==="SUCCESS";
 // A Stop is unresolved from the moment it is pressed until the executor reports stopped with cancellation_confirmed:true.
 // The intent is bound to the task it was raised for; a delivered request, a failed request and a running poll all leave it standing.
 const sameTask=(intent,task)=>Boolean(intent&&task&&intent.task_id===task.task_id&&intent.generation===task.generation);
 const stopUnresolved=client=>Boolean(sameTask(client.stopIntent,client.task)||(client.task?.state==="stopped"&&client.task.cancellation_confirmed!==true));
 // Free text from the executor is never evidence; it is shown only as labelled reported detail.
 const reported=task=>{const text=task.reason||task.result?.reason;return typeof text==="string"&&text?` Reported: ${text}`:"";};
 function stateText(task){
  return {
   created:"Proposal created. Requesting the approval prompt…",
   awaiting_permission:"Waiting for your approval. Nothing has run.",
   running:`Running the approved task${task.phase?` · ${task.phase}`:""}.`,
   stopping:"Stopping. Waiting for the executor to settle.",
   succeeded:verified(task)?"Finished and verified by readback.":"Finished, but the result was not verified. Review the details.",
   failed:"Failed. Nothing is retried automatically; review the details.",
   expired:"Approval expired. Nothing ran.",
   stopped:task.cancellation_confirmed===true?"Stopped. Queued input was revoked; earlier completed actions remain.":"Stop is not confirmed. The task may still be acting.",
   uncertain:"Outcome uncertain. Nothing is replayed; inspect the partial result."
  }[task.state]||"";
 }
 class ComputerClient {
  constructor({local,onChange=()=>{},makeId=()=>crypto.randomUUID(),clock=()=>performance.now()/1000}={}) {
   Object.assign(this,{local,onChange,makeId,clock,task:null,health:null,connected:false,busy:false,polling:false,stopIntent:null,epoch:0,received:0,safetyStopSent:false,inputError:"",reason:"Checking local control…"});
  }
  changed(){this.onChange(this);}
  clearInputError(){this.inputError="";this.changed();}
  accept(task,{replace=false}={}){
   if(task?.schema!=="ghoti_computer_task/1"||!validId(task.task_id)||!validId(task.generation)||!states.has(task.state)||!task.scope||!task.observation)throw Error("Unrecognized computer state; controls locked");
   if(this.task&&!replace&&(task.task_id!==this.task.task_id||task.generation!==this.task.generation||JSON.stringify(task.scope)!==JSON.stringify(this.task.scope)))throw Error("Task identity or approved scope changed");
   // Only stopped with cancellation_confirmed:true for the same task settles a Stop; omitted fields, other tasks and running polls do not.
   if(sameTask(this.stopIntent,task)&&task.state==="stopped"&&task.cancellation_confirmed===true)this.stopIntent=null;
   this.task=task;this.connected=true;this.received=this.clock();
   const intent=sameTask(this.stopIntent,task)?this.stopIntent:null;
   if(intent&&active(task)&&task.state!=="stopping")this.reason=intent.pending?"Stop requested; not yet acknowledged.":`Stop was not acknowledged and the task is still reported as ${task.state==="running"?"running":"active"}. Press Stop control again if you still want it stopped.`;
   else this.reason=(intent&&!active(task)&&task.state!=="stopped"?"Stop was never confirmed. ":"")+(task.state==="succeeded"?(verified(task)?stateText(task):`${stateText(task).replace(" Review the details.","")}${reported(task)}`):task.reason||(task.state==="awaiting_permission"?"Review the exact scope, then approve or reject.":task.state==="expired"?"Approval expired. Nothing was executed; create a new task deliberately.":task.state==="stopping"?"Stop requested. Waiting for the executor to become quiescent.":task.state==="stopped"?(task.cancellation_confirmed===true?"Stopped: queued input revoked and executor settled. Earlier completed actions remain.":"Stop is not confirmed. The task may still be acting."):task.state==="uncertain"?"Outcome uncertain. No automatic replay; inspect the partial result.":task.result?.reason||stateText(task)));
   this.changed();
  }
  async post(taskId,action,body){return this.local.request(`/api/runtime/computer/tasks/${taskId}/${action}`,{method:"POST",body});}
  async start(text,waitSeconds,inputMode="text"){
   if(!this.local.authenticated||this.busy||active(this.task)||this.task?.state==="uncertain"||!this.health?.can_start)return false;
   try{ text=noteInput(text,inputMode);if(![0,30].includes(waitSeconds))throw Error("Choose one of the supported wait times."); }
   catch(error){this.inputError=error.message;this.changed();return false;}
   this.inputError="";
   const epoch=++this.epoch;this.busy=true;this.safetyStopSent=false;this.reason="Creating a bounded proposal; no native input yet.";this.changed();
   try{
    const task=await this.local.request("/api/runtime/computer/tasks",{method:"POST",body:{request_id:this.makeId(),operation:"create_note",text,wait_seconds:waitSeconds}});
    if(epoch!==this.epoch)return false;
    this.accept(task,{replace:true});
    const pending=await this.post(task.task_id,"permission",{request_id:this.makeId()});
    if(epoch!==this.epoch)return false;this.accept(pending);return true;
   }catch(error){if(epoch===this.epoch)await this.disconnected(error.message);return false;}
   finally{if(epoch===this.epoch)this.busy=false;this.changed();}
  }
  async decide(choice){
   if(!this.local.authenticated||this.busy||this.task?.state!=="awaiting_permission"||!this.task.permission||!["allow_once","deny"].includes(choice)||this.clock()-this.received>10)return false;
   const task=this.task,epoch=++this.epoch;this.busy=true;this.reason="Sending your explicit decision once…";this.changed();
   try{const response=await this.post(task.task_id,"approval",{request_id:task.permission.request_id,choice});
    if(epoch!==this.epoch)return false;this.accept(response);return response.accepted===true;
   }catch(error){if(epoch===this.epoch)await this.disconnected(error.message);return false;}
   finally{if(epoch===this.epoch)this.busy=false;this.changed();}
  }
  async stop({keepalive=false}={}){
   if(!this.local.authenticated||!this.task||!active(this.task))return false;
   const task=this.task,epoch=++this.epoch,intent={task_id:task.task_id,generation:task.generation,pending:true};
   this.busy=false;this.stopIntent=intent;this.reason="Stop requested; not yet acknowledged.";this.changed();
   try{const response=await this.local.request(`/api/runtime/computer/tasks/${task.task_id}/cancel`,{method:"POST",body:{request_id:this.makeId()},keepalive});
    if(epoch!==this.epoch)return false;this.accept(response);return response.cancellation_confirmed===true;
   }catch(error){if(epoch===this.epoch){this.connected=false;this.task.observation.live=false;this.reason=`${error.message}. Stop is not confirmed; the task may still be acting. Nothing will be replayed.`;this.changed();}return false;}
   finally{intent.pending=false;}
  }
  async disconnected(reason){
   this.epoch+=1;this.busy=false;
   this.connected=false;if(this.task?.observation){this.task.observation.live=false;this.task.observation.accessibility_fresh=false;}
   this.reason=`${reason}. Connection lost; observations are stale and actions are not retried.`;this.changed();
   if(active(this.task)&&!this.safetyStopSent){this.safetyStopSent=true;
    try{await this.post(this.task.task_id,"cancel",{request_id:this.makeId()});}catch(_){}
   }
  }
  async refresh(){
   if(this.polling||this.busy)return;this.polling=true;const epoch=this.epoch;
   try{
    if(!this.local.authenticated){this.reason=this.local.reason;this.connected=false;return;}
    const reply=await this.local.request(this.task&&active(this.task)?`/api/runtime/computer/tasks/${this.task.task_id}`:"/api/runtime/computer");
    if(epoch!==this.epoch)return;
    if(reply.schema==="ghoti_computer_task/1")this.accept(reply);
    else{
     if(reply.schema!=="ghoti_computer/1")throw Error("Unrecognized operator health");
     this.health=reply;this.connected=true;
     if(reply.task)this.accept(reply.task,{replace:!this.task});
     else this.reason=reply.can_start?"Ready for a scoped temporary-note task. No desktop session is active.":reply.recovery||reply.reason||"Operator unavailable; no task can start.";
    }
   }catch(error){if(epoch===this.epoch)await this.disconnected(error.message);}
   finally{this.polling=false;this.changed();}
  }
 }
 // Status tone only: connection loss and unsettled outcomes outrank a cached running task.
 function statusTone(client){
  const task=client.task;
  if(stopUnresolved(client))return "unconfirmed";
  if(!client.connected)return "attention";
  if(task?.state==="failed")return "failed";
  if(["expired","uncertain"].includes(task?.state))return "attention";
  if(task?.state==="awaiting_permission")return "permission";
  if(active(task))return "running";
  // Only a readback-verified finish reads as success; idle is its own neutral state.
  if(task?.state==="succeeded")return verified(task)?"success":"attention";
  if(task)return "";
  return client.health?.can_start?"idle":"attention";
 }
 // Plain-language progress. A result that was not verified, or a lost connection, never looks like success.
 const STEP_LABELS=["Proposed","Your approval","Running","Verified result"];
 function progressSteps(client){
  const task=client.task,s=["todo","todo","todo","todo"];
  switch(task?.state){
   case"created":s[0]="current";break;
   case"awaiting_permission":s[0]="done";s[1]="current";break;
   case"running":case"stopping":s[0]=s[1]="done";s[2]="current";break;
   case"succeeded":s[0]=s[1]=s[2]="done";s[3]=verified(task)?"done":"problem";break;
   case"expired":s[0]="done";s[1]="problem";break;
   case"stopped":s[0]=s[1]="done";s[2]=task.cancellation_confirmed===true?"done":"problem";break;
   case"failed":case"uncertain":s[0]=s[1]="done";s[2]="problem";break;
  }
  if(task&&!client.connected)for(let i=0;i<4;i++)if(s[i]==="current")s[i]="problem";
  return STEP_LABELS.map((label,i)=>({label,state:s[i]}));
 }
 function progressText(client){
  const task=client.task;
  if(!task)return "No task yet. Describe one above; nothing runs before you approve it.";
  const text=stateText(task);
  if(stopUnresolved(client)&&task.state!=="stopped")return `Stop was requested but not confirmed. The task may still be acting.${client.connected?"":" Connection lost; this may be out of date."}`;
  return client.connected?text:`${text} Connection lost; this may be out of date.`;
 }
 function navState(client){
  const state=client.task?.state;
  // An unacknowledged Stop outranks everything: from any other view it must not look settled or merely offline.
  if(stopUnresolved(client))return {text:"Stop unconfirmed",tone:"unconfirmed"};
  if(active(client.task)&&!client.connected)return {text:"Connection lost",tone:"attention"};
  if(state==="succeeded"&&!verified(client.task))return {text:"Not verified",tone:"attention"};
  return {awaiting_permission:{text:"Needs approval",tone:"permission"},created:{text:"Proposed",tone:"permission"},running:{text:"Running",tone:"running"},
   stopping:{text:"Stopping",tone:"running"},failed:{text:"Needs review",tone:"failed"},uncertain:{text:"Needs review",tone:"attention"}}[state]||{text:"",tone:""};
 }
 if(typeof module!=="undefined"&&module.exports)module.exports={ComputerClient,statusTone,progressSteps,progressText,navState};
 if(typeof window==="undefined")return;
 const $=id=>document.getElementById(id);
 const controller=new ComputerClient({local:root.GhotiLocal,onChange:render});root.GhotiComputer=controller;
 // render() runs on every poll and timer tick. Write only what changed, so the live regions
 // (#computer-status, #computer-progress) announce real transitions and nothing else.
 const put=(el,prop,value)=>{if(el[prop]!==value)el[prop]=value;};
 const tone=(el,value)=>{if(el.dataset.state!==value)el.dataset.state=value;};
 // Approval focus: taken once per permission request, never again on later polls.
 let focusedRequest=null,panelShown=false;
 function render(){
  const task=controller.task,pending=Boolean(task?.state==="awaiting_permission"&&task.permission);
  const approval=$("computer-approval"),progress=$("computer-progress"),inApproval=approval.contains(document.activeElement);
  const onButton=inApproval&&document.activeElement!==approval;
  put($("computer-status"),"textContent",controller.reason);
  tone($("computer-status"),statusTone(controller));
  put($("computer-input-error"),"textContent",controller.inputError);
  put($("computer-input-error"),"hidden",!controller.inputError);
  const invalid=String(Boolean(controller.inputError));
  if($("computer-text").getAttribute("aria-invalid")!==invalid)$("computer-text").setAttribute("aria-invalid",invalid);
  put($("computer-start"),"disabled",Boolean(!root.GhotiLocal.authenticated||controller.busy||active(task)||task?.state==="uncertain"||!controller.health?.can_start));
  put($("computer-stop"),"disabled",Boolean(!root.GhotiLocal.authenticated||!active(task)));
  put(approval,"hidden",!pending);
  const locked=controller.busy||!controller.connected||controller.clock()-controller.received>10;
  put($("computer-approve"),"disabled",locked);
  put($("computer-deny"),"disabled",locked);
  // Disabling a focused button drops focus to the page; keep it on the prompt instead.
  if(pending&&locked&&onButton)approval.focus();
  put($("computer-scope"),"textContent",task?JSON.stringify(task.scope,null,2):"Scope appears before permission is requested. Only a new temporary Notepad file is supported.");
  put(progress,"textContent",progressText(controller));tone(progress,statusTone(controller));
  if(pending){
   // Wait until the Computer view is open; the navigation badge says "Needs approval" meanwhile.
   const shown=!$("daily-panel-computer").hidden;
   if(shown&&focusedRequest!==task.permission.request_id){focusedRequest=task.permission.request_id;approval.focus();}
   // Back on this view with the same request still pending: focus stays where navigation put it; only scroll the card into view.
   else if(shown&&!panelShown)approval.scrollIntoView({block:"nearest"});
   panelShown=shown;
  }else if(focusedRequest!==null){
   // Resolved: if the user was inside the prompt, hand focus to the outcome line instead of dropping it.
   focusedRequest=null;panelShown=false;if(inApproval)progress.focus();
  }
  const steps=progressSteps(controller),list=$("computer-steps"),key=steps.map(s=>s.state).join();
  if(list&&list.dataset.key!==key){
   list.dataset.key=key;list.replaceChildren(...steps.map(step=>{const li=document.createElement("li");li.textContent=step.label;li.dataset.stepState=step.state;if(step.state==="current")li.setAttribute("aria-current","step");return li;}));
  }
  const nav=$("daily-nav-computer-state"),ns=navState(controller);
  if(nav&&(nav.textContent!==ns.text||nav.dataset.state!==ns.tone)){nav.textContent=ns.text;nav.dataset.state=ns.tone;}
  put($("computer-result"),"textContent",task?.result&&Object.keys(task.result).length?JSON.stringify(task.result,null,2):"No verified result yet.");
  const fresh=Boolean(controller.connected&&controller.clock()-controller.received<=3&&task?.observation?.live&&task.state==="running");
  const image=$("computer-image");put(image,"hidden",!fresh);
  if(fresh){const url=`/api/runtime/computer/tasks/${task.task_id}/image?v=${task.observation.image_version}&generation=${task.generation}`;if(image.getAttribute("src")!==url)image.setAttribute("src",url);}
  else if(image.getAttribute("src")!=null)image.removeAttribute("src");
  put($("computer-observation-status"),"textContent",fresh?"Fresh authorized window observation":task?.observation?.accessibility_fresh&&controller.connected&&controller.clock()-controller.received<=3?"Fresh accessibility observation; no live pixels available":"No live screen. Recorded or disconnected observations are not live.");
  put($("computer-accessibility"),"textContent",task?.observation?.elements?JSON.stringify(task.observation.elements,null,2):"No authorized accessibility observation.");
 }
 function inputModeChanged(){
  const taskMode=$("computer-input-mode").value==="task";
  $("computer-text-label").textContent=taskMode?"What should Ghoti do?":"Exact text for the temporary note";
  $("computer-text").maxLength=taskMode?650:500;
  $("computer-text").placeholder=taskMode?'Create a note saying "Call Sam"':"A short line to verify";
  controller.clearInputError();
 }
 $("computer-input-mode").addEventListener("change",inputModeChanged);
 // Clearing the alert first lets a repeated identical error be announced again.
 $("computer-form").addEventListener("submit",event=>{event.preventDefault();$("computer-input-error").textContent="";controller.start($("computer-text").value,Number($("computer-wait").value),$("computer-input-mode").value);});
 $("computer-approve").addEventListener("click",()=>controller.decide("allow_once"));
 $("computer-deny").addEventListener("click",()=>controller.decide("deny"));
 $("computer-stop").addEventListener("click",()=>controller.stop());
 $("computer-image").addEventListener("error",()=>{$("computer-image").hidden=true;$("computer-image").removeAttribute("src");$("computer-observation-status").textContent="Observation expired or unavailable; stale pixels hidden.";});
 window.addEventListener("pagehide",()=>controller.stop({keepalive:true}));
 window.addEventListener("offline",()=>controller.disconnected("Browser is offline"));
 async function poll(){await controller.refresh();setTimeout(poll,1000);}
 root.GhotiLocal.ready.then(poll);setInterval(render,500);render();
})(globalThis);
