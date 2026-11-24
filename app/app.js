'use strict';
const $=id=>document.getElementById(id);let report=null;let mode='offline_rule_demo';
const fields=['sender','subject','body'];
async function bootstrap(){
 try{
   const st=await (await fetch('/api/status')).json();mode=st.mode;
   $('mode').textContent=mode==='solar_pro_4'?'● Solar Pro 4 실시간 분석':'● 로컬 예시 모드 · 규칙 기반';
   $('mode').className=mode==='solar_pro_4'?'mode':'mode demo';
   const cases=await (await fetch('/api/samples')).json();
   $('samples').replaceChildren();cases.forEach(x=>{
     let b=document.createElement('button');b.className='sample';b.type='button';
     let k=document.createElement('div');k.className='kind';k.textContent=x.id+' · '+x.kind;
     let title=document.createElement('strong');title.textContent=x.subject;
     b.append(k,title);b.addEventListener('click',()=>{fields.forEach(f=>$(f).value=x[f]);$('err').style.display='none';$('sender').focus();window.scrollTo({top:0,behavior:'smooth'});});
     $('samples').append(b);
   });
 }catch(e){$('mode').textContent='서버 연결 필요';}
}
function showResult(r){
 report=r;$('feedback-note').textContent='';$('empty').style.display='none';$('results').style.display='block';
 $('category').textContent=r.category;
 $('risk').textContent='위험 수준 · '+r.risk_level;
 const cls=r.risk_level==='높음'?'high':r.risk_level==='보통'?'mid':'';
 $('risk').className='risk '+cls;$('bar').className='bar '+cls;
 $('reason').textContent=r.reason;
 $('signals').replaceChildren();(r.signals||[]).forEach(item=>{const s=document.createElement('span');s.className='pill';s.textContent=item;$('signals').append(s);});
 $('actions').replaceChildren();(r.actions||[]).forEach((item,i)=>{const row=document.createElement('p');row.textContent=(i+1)+'. '+item;row.style.margin='4px 0';$('actions').append(row);});
 $('uncertainty').textContent=r.uncertainty;
 $('analysis-mode').textContent=r.mode==='solar_pro_4'?'분석 엔진: Upstage Solar Pro 4 API (별도 로컬 시연)':'분석 엔진: 규칙 기반 오프라인 예시 · Solar Pro 4 분석 아님';
}
$('analyze').addEventListener('click',async()=>{
 $('err').style.display='none';$('analyze').disabled=true;$('analyze').textContent='분석 중…';
 try{
   const body=Object.fromEntries(fields.map(f=>[f,$(f).value]));
   const response=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
   const result=await response.json();if(!response.ok)throw new Error(result.error||'분석 실패');showResult(result);
 }catch(e){$('err').textContent='오류: '+e.message;$('err').style.display='block';}
 finally{$('analyze').disabled=false;$('analyze').textContent='✦  위험 분석하기';}
});
$('clear').addEventListener('click',()=>{fields.forEach(f=>$(f).value='');$('results').style.display='none';$('empty').style.display='flex';$('err').style.display='none';report=null;});
$('export').addEventListener('click',()=>{if(!report)return;let blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'});let url=URL.createObjectURL(blob);let a=document.createElement('a');a.href=url;a.download='smartmail-analysis.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
bootstrap();

$('agree').addEventListener('click',()=>{$('feedback-note').textContent='현재 화면에 ‘적절함’으로 표시했습니다. 외부 전송이나 재학습은 하지 않습니다.';});
$('disagree').addEventListener('click',()=>{$('feedback-note').textContent='현재 화면에 ‘재검토 필요’로 표시했습니다. 담당자 확인 후 판단하세요. 외부 전송이나 재학습은 하지 않습니다.';});
