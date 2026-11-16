"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const {ComputerClient,statusTone,progressSteps,progressText,navState} = require("../dashboard_app/static/computer.js");
function fixture() {
 const calls = [], replies = [];
 const local = {authenticated:true, reason:"fixture", request:async (path, options={}) => {
  calls.push({path,...options}); const reply = replies.shift(); if(reply instanceof Error) throw reply;
  assert.ok(reply, "unexpected fixture request"); return reply;
 }};
 let n=0; const client=new ComputerClient({local,makeId:()=>`fixture-${++n}`,clock:()=>100});
 const task=(state="created")=>({schema:"ghoti_computer_task/1",task_id:"owned-task",generation:"owned-generation",state,
  scope:{operation:"create_note",filename:"owned-file",text:"fixture"},permission:state==="awaiting_permission"?{request_id:"permission",expires_in_seconds:60}:null,
  connected:state==="running",observation:{live:state==="running",image_version:1},cancellation_confirmed:state==="stopped",result:{}});
 return {client,local,calls,replies,task};
}
test("start only creates a fixed scoped proposal; never auto approves",async()=>{
 const f=fixture(); f.client.health={can_start:true}; f.replies.push(f.task(),f.task("awaiting_permission"));
 assert.equal(await f.client.start("fixture",30),true);
 assert.deepEqual(f.calls[0].body,{request_id:"fixture-1",operation:"create_note",text:"fixture",wait_seconds:30});
 assert.equal(f.calls[1].path,"/api/runtime/computer/tasks/owned-task/permission");
 assert.equal(f.calls.length,2);assert.equal(f.client.task.state,"awaiting_permission");
});
test("unauthenticated clients cannot start or approve",async()=>{
 const f=fixture();f.local.authenticated=false;f.client.health={can_start:true};
 assert.equal(await f.client.start("fixture",0),false);assert.equal(await f.client.decide("allow_once"),false);assert.equal(f.calls.length,0);
});
test("late approval acknowledgement cannot overwrite acknowledged Stop",async()=>{
 const f=fixture();f.client.accept(f.task("awaiting_permission"));let resolve;
 f.local.request=async(path)=>path.endsWith("/approval")?new Promise(r=>{resolve=r;}):f.task("stopped");
 const approving=f.client.decide("allow_once");await f.client.stop();resolve({...f.task("running"),accepted:true});await approving;
 assert.equal(f.client.task.state,"stopped");assert.equal(f.client.task.cancellation_confirmed,true);
});
test("disconnect retires a held approval without reviving observations or replaying writes",async()=>{
 const f=fixture();f.client.accept(f.task("awaiting_permission"));let resolveApproval,resolveCancel;
 f.local.request=async(path,options={})=>{
  f.calls.push({path,...options});
  if(path.endsWith("/approval"))return new Promise(resolve=>{resolveApproval=resolve;});
  if(path.endsWith("/cancel"))return new Promise(resolve=>{resolveCancel=resolve;});
  return f.replies.shift();
 };
 const approving=f.client.decide("allow_once");
 const disconnecting=f.client.disconnected("fixture offline");
 assert.equal(f.client.busy,false,"disconnect releases busy before old requests settle");
 resolveApproval({...f.task("running"),accepted:true,observation:{live:true,accessibility_fresh:true,elements:[{name:"old"}]}});
 assert.equal(await approving,false,"pre-disconnect approval must be retired");
 assert.equal(f.client.connected,false);assert.equal(f.client.busy,false);
 assert.equal(f.client.task.state,"awaiting_permission");assert.equal(f.client.task.observation.live,false);
 assert.notEqual(f.client.task.observation.accessibility_fresh,true);
 await f.client.disconnected("second offline signal");
 assert.equal(f.calls.filter(c=>c.path.endsWith("/approval")).length,1);
 assert.equal(f.calls.filter(c=>c.path.endsWith("/cancel")).length,1);
 assert.equal(f.calls.find(c=>c.path.endsWith("/cancel")).path,"/api/runtime/computer/tasks/owned-task/cancel");
 resolveCancel(f.task("stopping"));await disconnecting;
 assert.equal(f.client.connected,false);assert.notEqual(f.client.task.cancellation_confirmed,true);
 f.replies.push(f.task("stopping"),f.task("stopped"));
 await f.client.refresh();assert.equal(f.client.task.state,"stopping");assert.equal(f.client.task.cancellation_confirmed,false);
 assert.match(f.client.reason,/Waiting for the executor/);
 await f.client.refresh();assert.equal(f.client.task.state,"stopped");assert.equal(f.client.task.cancellation_confirmed,true);
 assert.equal(f.calls.length,4,"only fresh authenticated polling follows the bounded cancellation");
});
test("a disconnect hides stale pixels and sends only one scoped safety stop",async()=>{
 const f=fixture();f.client.accept(f.task("running"));f.client.task.observation.accessibility_fresh=true;
 f.replies.push(new Error("fixture offline"),new Error("fixture offline"));
 await f.client.refresh();assert.equal(f.client.connected,false);assert.equal(f.client.task.observation.live,false);
 assert.equal(f.client.task.observation.accessibility_fresh,false);
 assert.equal(f.calls.filter(c=>c.path.endsWith("/cancel")).length,1);
});
test("a reload recovers only the authenticated owner's task without execution",async()=>{
 const f=fixture();f.replies.push({schema:"ghoti_computer/1",can_start:false,generation:"owned-generation",task:f.task("running")});
 await f.client.refresh();assert.equal(f.client.task.task_id,"owned-task");assert.equal(f.calls.length,1);assert.equal(f.calls[0].method,undefined);
});

test("ordinary note tasks propose only intended content and never approve",async()=>{
 for(const instruction of ['Create a note saying Check the release plan','Please write a temporary note: "Check the release plan"',"Make a note that says 'Check the release plan'"]){
  const f=fixture();f.client.health={can_start:true};f.replies.push(f.task(),f.task("awaiting_permission"));
  assert.equal(await f.client.start(instruction,0,"task"),true);
  assert.equal(f.calls[0].body.text,"Check the release plan");
  assert.equal(f.calls[0].body.operation,"create_note");assert.equal(f.calls.length,2);
  assert.equal(f.calls.some(c=>c.path.endsWith("/approval")),false);
 }
});
test("unsupported or ambiguous tasks never become literal notes",async()=>{
 for(const instruction of ['Open my email','Create a note','Create a note saying "hello" then open mail','Create a note saying "unfinished','Create a note saying ""']){
  const f=fixture();f.client.health={can_start:true};
  assert.equal(await f.client.start(instruction,0,"task"),false);assert.equal(f.calls.length,0);
  assert.ok(f.client.inputError);assert.equal(f.client.task,null);
 }
});
test("task syntax has a separate bound from the 500-character note",async()=>{
 const f=fixture();f.client.health={can_start:true};f.replies.push(f.task(),f.task("awaiting_permission"));
 assert.equal(await f.client.start('Create a note saying "'+"a".repeat(500)+'"',0,"task"),true);
 assert.equal(f.calls[0].body.text.length,500);
 for(const [input,mode] of [["a".repeat(501),"text"],['Create a note saying '+"a".repeat(501),"task"],["a".repeat(651),"task"],["","task"],["Create a note saying x\ny","task"],["hello","unknown"]]){
  const bad=fixture();bad.client.health={can_start:true};
  assert.equal(await bad.client.start(input,0,mode),false);assert.equal(bad.calls.length,0);assert.ok(bad.client.inputError);
 }
});
test("literal mode preserves text that looks like an instruction",async()=>{
 const f=fixture();f.client.health={can_start:true};f.replies.push(f.task(),f.task("awaiting_permission"));
 const value='Create a note saying Keep these exact words';
 assert.equal(await f.client.start(value,30,"text"),true);assert.equal(f.calls[0].body.text,value);
});
test("validation survives polling without hiding a real prior result or disconnecting",async()=>{
 const f=fixture();f.client.health={can_start:true};const previous={...f.task("succeeded"),result:{status:"SUCCESS",verified_text:"earlier"}};
 f.client.accept(previous);
 assert.equal(await f.client.start("Open email",0,"task"),false);const error=f.client.inputError;
 assert.ok(error);assert.equal(f.client.connected,true);assert.deepEqual(f.client.task.result,previous.result);assert.equal(f.calls.length,0);
 f.replies.push({schema:"ghoti_computer/1",can_start:true,task:previous});await f.client.refresh();
 assert.equal(f.client.inputError,error);assert.deepEqual(f.client.task.result,previous.result);
 f.client.clearInputError();assert.equal(f.client.inputError,"");
});
test("connection loss and unconfirmed Stop outrank a cached running task in the status tone",async()=>{
 const lost=fixture();lost.client.accept(lost.task("running"));assert.equal(statusTone(lost.client),"running");
 lost.replies.push(new Error("fixture offline"),new Error("fixture offline"));await lost.client.refresh();
 assert.equal(lost.client.task.state,"running");assert.match(lost.client.reason,/Connection lost/);
 assert.equal(statusTone(lost.client),"attention");
 const stop=fixture();stop.client.accept(stop.task("running"));stop.replies.push(new Error("fixture offline"));
 assert.equal(await stop.client.stop(),false);assert.match(stop.client.reason,/Stop is not confirmed; the task may still be acting/);
 assert.equal(statusTone(stop.client),"unconfirmed");
 const held=fixture();held.client.accept(held.task("awaiting_permission"));held.replies.push(new Error("fixture offline"));await held.client.disconnected("fixture offline");
 assert.equal(statusTone(held.client),"attention");
});
test("failed, expired, uncertain and unconfirmed outcomes never read as neutral or running",()=>{
 for(const [state,tone] of [["failed","failed"],["expired","attention"],["uncertain","attention"],["stopped","unconfirmed"]]){
  const f=fixture();f.client.accept({...f.task(state),cancellation_confirmed:false});assert.equal(f.client.connected,true);
  assert.equal(statusTone(f.client),tone,state);
 }
 const ok=fixture();ok.client.accept(ok.task("stopped"));assert.equal(statusTone(ok.client),"");
 const pending=fixture();pending.client.accept(pending.task("awaiting_permission"));assert.equal(statusTone(pending.client),"permission");
});
test("idle, verified success and unverified success have different status tones",()=>{
 const idle=fixture();idle.client.connected=true;idle.client.health={can_start:true};assert.equal(statusTone(idle.client),"idle");
 idle.client.health={can_start:false};assert.equal(statusTone(idle.client),"attention");
 const done=fixture();done.client.accept({...done.task("succeeded"),verification:"SUCCESS"});assert.equal(statusTone(done.client),"success");
 const unverified=fixture();unverified.client.accept(unverified.task("succeeded"));assert.equal(statusTone(unverified.client),"attention");
});
const stepStates=(state,extra={},connected=true)=>{const f=fixture();if(state){f.client.accept({...f.task(state),...extra});}f.client.connected=connected;return progressSteps(f.client).map(s=>s.state).join(" ");};
test("progressSteps maps every task state to four labelled steps",()=>{
 const f=fixture();assert.deepEqual(progressSteps(f.client).map(s=>s.label),["Proposed","Your approval","Running","Verified result"]);
 for(const [state,extra,want] of [
  [null,{},"todo todo todo todo"],["created",{},"current todo todo todo"],["awaiting_permission",{},"done current todo todo"],
  ["running",{},"done done current todo"],["stopping",{},"done done current todo"],
  ["succeeded",{verification:"SUCCESS"},"done done done done"],["succeeded",{verification:"UNVERIFIED"},"done done done problem"],["succeeded",{},"done done done problem"],
  ["expired",{},"done problem todo todo"],["stopped",{cancellation_confirmed:true},"done done done todo"],["stopped",{cancellation_confirmed:false},"done done problem todo"],
  ["failed",{},"done done problem todo"],["uncertain",{},"done done problem todo"]])assert.equal(stepStates(state,extra),want,`${state} ${JSON.stringify(extra)}`);
});
test("progressSteps turns the current step into a problem when disconnected",()=>{
 for(const [state,want] of [["created","problem todo todo todo"],["awaiting_permission","done problem todo todo"],["running","done done problem todo"],["stopping","done done problem todo"]])assert.equal(stepStates(state,{},false),want,state);
 assert.equal(stepStates("succeeded",{verification:"SUCCESS"},false),"done done done done");
 assert.equal(stepStates(null,{},false),"todo todo todo todo");
});
test("progressText distinguishes approval, failure and unverified success",()=>{
 const text=(state,extra={},connected=true)=>{const f=fixture();if(state)f.client.accept({...f.task(state),...extra});f.client.connected=connected;return progressText(f.client);};
 assert.match(text(null),/^No task yet/);
 assert.match(text("awaiting_permission"),/Waiting for your approval\. Nothing has run\./);
 assert.match(text("failed"),/^Failed\./);
 assert.match(text("succeeded",{verification:"SUCCESS"}),/verified by readback/);
 assert.match(text("succeeded",{verification:"UNVERIFIED"}),/not verified/);
 assert.equal(text("running",{phase:"typing"}),"Running the approved task · typing.");
 assert.equal(text("running"),"Running the approved task.");
 assert.match(text("stopped",{cancellation_confirmed:true}),/Queued input was revoked/);
 assert.match(text("stopped",{cancellation_confirmed:false}),/not confirmed/);
 assert.match(text("running",{},false),/Connection lost; this may be out of date\.$/);
 assert.doesNotMatch(text(null,{},false),/Connection lost/);
 assert.equal(new Set(["created","awaiting_permission","running","stopping","succeeded","failed","expired","stopped","uncertain"].map(s=>text(s))).size,9);
});
test("navState flags approval, running, lost connection and stays empty when idle",()=>{
 const nav=(state,extra={},connected=true)=>{const f=fixture();if(state)f.client.accept({...f.task(state),...extra});f.client.connected=connected;return navState(f.client);};
 assert.deepEqual(nav("awaiting_permission"),{text:"Needs approval",tone:"permission"});
 assert.deepEqual(nav("running"),{text:"Running",tone:"running"});
 assert.deepEqual(nav("created"),{text:"Proposed",tone:"permission"});
 assert.deepEqual(nav("stopping"),{text:"Stopping",tone:"running"});
 assert.deepEqual(nav("running",{},false),{text:"Connection lost",tone:"attention"});
 assert.deepEqual(nav("awaiting_permission",{},false),{text:"Connection lost",tone:"attention"});
 assert.deepEqual(nav("failed"),{text:"Needs review",tone:"failed"});
 assert.deepEqual(nav("uncertain"),{text:"Needs review",tone:"attention"});
 assert.deepEqual(nav("succeeded",{verification:"SUCCESS"}),{text:"",tone:""});
 for(const state of [null,"expired","stopped"])assert.deepEqual(nav(state),{text:"",tone:""},String(state));
});
