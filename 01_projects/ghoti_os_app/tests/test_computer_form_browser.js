"use strict";
// Real browser, production form/client; isolated service fixture, never native CUA.
const test=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {chromium}=require(process.env.GHOTI_BROWSER_TEST_MODULE||"playwright");
const assets=path.resolve(__dirname,"../dashboard_app/static");
test("Computer form parses tasks, preserves consent, errors and real-result presentation",async()=>{
 const browser=await chromium.launch({channel:"msedge",headless:true});
 try{
  const context=await browser.newContext();await context.route("**/*",route=>route.abort());
  const page=await context.newPage(),errors=[];page.on("pageerror",error=>errors.push(error.message));
  const html=fs.readFileSync(path.join(assets,"index.html"),"utf8");
  const section=html.slice(html.indexOf('<section id="daily-panel-computer"'),html.indexOf('<section id="daily-panel-tools"'));
  // A routed loopback document supplies the real secure-context UUID API.
  // No listener, installed profile, real session, or HTTP backend is involved.
  const fixtureURL="http://127.0.0.1:18766/computer-test-fixture";
  await page.route(fixtureURL,route=>route.fulfill({contentType:"text/html; charset=utf-8",body:section.replace(' hidden>','>')}));
  await page.goto(fixtureURL);
  assert.equal(page.url(),fixtureURL);
  assert.equal(await page.evaluate(()=>isSecureContext&&typeof crypto.randomUUID==="function"),true);
  for(const css of ["daily.css","computer.css"])await page.addStyleTag({path:path.join(assets,css)});
  await page.evaluate(()=>{
   window.fixture={calls:[],task:null};
   window.GhotiLocal={authenticated:true,ready:Promise.resolve(),request:async(url,options={})=>{
    const f=window.fixture;f.calls.push({url,method:options.method,body:options.body});
    if(!options.method)return url==="/api/runtime/computer"?{schema:"ghoti_computer/1",can_start:true,task:f.task}:f.task;
    if(url==="/api/runtime/computer/tasks")f.task={schema:"ghoti_computer_task/1",task_id:"fixture-note",generation:"fixture-generation",state:"created",scope:options.body,observation:{},result:{}};
    else if(url.endsWith("/permission"))f.task={...f.task,state:"awaiting_permission",permission:{request_id:"fixture-only",expires_in_seconds:60}};
    else throw Error("Unexpected write in no-native-execution fixture");
    return f.task;
   }};
  });
  await page.addScriptTag({path:path.join(assets,"computer.js")});
  await page.waitForFunction(()=>!document.getElementById("computer-start").disabled);
  await page.locator("#computer-start").click();
  await page.waitForFunction(()=>!document.getElementById("computer-input-error").hidden);
  assert.match(await page.locator("#computer-input-error").innerText(),/Enter a task/);
  assert.equal(await page.evaluate(()=>fixture.calls.filter(c=>c.method).length),0);
  await page.locator("#computer-text").fill("Open email");await page.locator("#computer-start").click();
  assert.match(await page.locator("#computer-input-error").innerText(),/not submitted/);
  await page.evaluate(()=>GhotiComputer.refresh());
  assert.equal(await page.locator("#computer-input-error").isVisible(),true);
  assert.equal(await page.evaluate(()=>fixture.calls.filter(c=>c.method).length),0);
  await page.locator("#computer-input-mode").selectOption("text");
  assert.equal(await page.locator("#computer-input-error").isVisible(),false);
  assert.equal(await page.locator("#computer-text").getAttribute("maxlength"),"500");
  await page.locator("#computer-input-mode").selectOption("task");
  assert.equal(await page.locator("#computer-text").getAttribute("maxlength"),"650");
  await page.locator("#computer-text").fill('Create a note saying "Check the release plan"');
  await page.locator("#computer-start").click();
  await page.waitForFunction(()=>GhotiComputer.task?.state==="awaiting_permission",undefined,{timeout:3000}).catch(async()=>{
   throw Error(JSON.stringify(await page.evaluate(()=>({reason:GhotiComputer.reason,error:GhotiComputer.inputError,secure:isSecureContext,randomUUID:typeof crypto.randomUUID,calls:fixture.calls}))));
  });
  assert.equal(await page.locator("#computer-approval").isVisible(),true);
  assert.equal(await page.evaluate(()=>GhotiComputer.task.scope.text),"Check the release plan");
  assert.equal(await page.evaluate(()=>fixture.calls.filter(c=>c.method).length),2);
  assert.equal(await page.evaluate(()=>fixture.calls.some(c=>c.url.endsWith("/approval"))),false);
  // Fixture state updates exercise existing presentation, never claim real execution.
  await page.evaluate(()=>{fixture.task={...fixture.task,state:"running",phase:"verify",last_action:"readback",verification:"VERIFYING"};return GhotiComputer.refresh();});
  assert.match(await page.locator("#computer-progress").innerText(),/Running.*verify/);
  await page.evaluate(()=>{fixture.task={...fixture.task,state:"succeeded",phase:"complete",verification:"VERIFIED",result:{status:"SUCCESS",verified_text:"Check the release plan",fixture:true}};return GhotiComputer.refresh();});
  assert.match(await page.locator("#computer-result").textContent(),/Check the release plan/);
  for(const width of [320,768,1024,1440]){
   await page.setViewportSize({width,height:1100});
   assert.ok(await page.locator("#computer-form").evaluate(e=>e.getBoundingClientRect().width<=innerWidth),`form fits ${width}`);
  }
  assert.deepEqual(errors,[]);
  if(process.env.GHOTI_BROWSER_TEST_SCREENSHOT)await page.screenshot({path:process.env.GHOTI_BROWSER_TEST_SCREENSHOT,fullPage:true});
 }finally{await browser.close();}
});
