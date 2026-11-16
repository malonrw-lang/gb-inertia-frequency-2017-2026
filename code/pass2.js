(async function(){
if (window.P2) return 'already';
const P2 = window.P2 = {status:{}, log:[], queue:[], CH:8e6, PAR:3};
P2.idb = await new Promise((res,rej)=>{const r=indexedDB.open('gridGP2',1); r.onupgradeneeded=()=>r.result.createObjectStore('m'); r.onsuccess=()=>res(r.result); r.onerror=()=>rej(r.error);});
function parseTs(s){
  if (s.length === 10) return Date.UTC(+s.slice(0,4), +s.slice(5,7)-1, +s.slice(8,10)) / 1000;
  let t = Date.UTC(+s.slice(0,4), +s.slice(5,7)-1, +s.slice(8,10), +s.slice(11,13), +s.slice(14,16), +s.slice(17,19))/1000;
  if (s.length > 20) { const sign = s[20] === '-' ? -1 : 1; t -= sign*((+s.slice(21,23))*3600+(+s.slice(23,25))*60); }
  return t;
}
async function fetchRange(url, a, b, tries){
  for (let i=0;i<tries;i++){
    const ac = new AbortController(); const to = setTimeout(()=>ac.abort(), 120000);
    try { const r = await fetch(url, {headers:{Range:`bytes=${a}-${b}`}, signal:ac.signal, cache:'no-store'});
      if (r.status !== 206 && r.status !== 200) throw new Error('HTTP '+r.status);
      const buf = new Uint8Array(await r.arrayBuffer()); clearTimeout(to);
      if (r.status === 200) return {whole:buf};
      return {buf, total:+(r.headers.get('content-range')||'/0').split('/')[1]};
    } catch(e){ clearTimeout(to); if (i===tries-1) throw e; await new Promise(r=>setTimeout(r, 3000*(i+1))); }
  }
}
async function getBytes(url){
  const first = await fetchRange(url, 0, P2.CH-1, 6); if (first.whole) return first.whole;
  const total = first.total, out = new Uint8Array(total); out.set(first.buf, 0);
  const starts=[]; for (let a=first.buf.length; a<total; a+=P2.CH) starts.push(a); let idx=0;
  const w = async()=>{ while(idx<starts.length){ const a=starts[idx++]; const b=Math.min(a+P2.CH,total)-1; const r=await fetchRange(url,a,b,6); if(r.buf.length!==b-a+1) throw new Error('short'); out.set(r.buf,a);} };
  await Promise.all(Array.from({length:P2.PAR}, w)); return out;
}
async function getText(f){
  const buf = await getBytes(f.url);
  if (f.ext === 'csv') return new TextDecoder().decode(buf);
  const dv = new DataView(buf.buffer);
  const method = dv.getUint16(8,true), csize = dv.getUint32(18,true), nlen = dv.getUint16(26,true), elen = dv.getUint16(28,true);
  const data = buf.subarray(30+nlen+elen, 30+nlen+elen+csize);
  if (method === 0) return new TextDecoder().decode(data);
  const reader = new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw')).pipeThrough(new TextDecoderStream()).getReader(); const parts=[];
  while(true){ const {done,value}=await reader.read(); if(done)break; parts.push(value); } return parts.join('');
}
// DC service curve: 0 within 0.015 Hz; linear to 5% at 0.2 Hz; linear 5%->100% from 0.2 to 0.5 Hz; 100% beyond
function g(d){ d=Math.abs(d); if (d<=0.015) return 0; if (d<=0.2) return 0.05*(d-0.015)/0.185; if (d<=0.5) return 0.05+0.95*(d-0.2)/0.3; return 1; }
function analyse(text){
  const L = text.split('\n'); const acc = new Map();
  for (let i=1;i<L.length;i++){
    let s=L[i]; if(!s) continue; if (s.charCodeAt(s.length-1)===13) s=s.slice(0,-1); const c=s.indexOf(','); if(c<0) continue;
    const t=parseTs(s.slice(0,c)), f=+s.slice(c+1); if(!isFinite(t)||!isFinite(f)||f<45||f>55) continue;
    const b=Math.floor(t/1800)*1800; let r=acc.get(b); if(!r){r=[0,0,0]; acc.set(b,r);} r[0]++; r[1]+=g(f-50); if (Math.abs(f-50)>0.1) r[2]++;
  }
  return [...acc.entries()].sort((a,b)=>a[0]-b[0]).map(([b,r])=>[b,r[0],r[1].toFixed(3),r[2]].join(','));
}
P2.processMonth = async function(f){
  const key=f.y+'-'+String(f.m).padStart(2,'0'); P2.status[key]='fetching';
  try { const text=await getText(f); P2.status[key]='parsing'; const rows=analyse(text);
    await new Promise(res=>{const tx=P2.idb.transaction('m','readwrite'); tx.objectStore('m').put(rows,key); tx.oncomplete=()=>res(1); tx.onerror=()=>res(0);});
    P2.status[key]='done';
  } catch(e){ P2.status[key]='error: '+e; P2.log.push(key+' '+e); P2.queue.push(f); }
};
P2.summary = ()=>{ const s={}; for(const v of Object.values(P2.status)){ const k=v.startsWith('error')?'error':v; s[k]=(s[k]||0)+1;} return {counts:s, queue:P2.queue.length, running:P2.running, errors:P2.log.slice(-3)}; };
P2.queue = window._files.filter(f=>{const m=f.y*12+f.m; return m>=2017*12+7 && m<=2026*12+7;}).sort((a,b)=>(a.y*12+a.m)-(b.y*12+b.m));
P2.running = true;
P2.done = Promise.all([0,1].map(async()=>{ while(P2.queue.length){ const f=P2.queue.shift(); if (P2.status[f.y+'-'+String(f.m).padStart(2,'0')]==='done') continue; await P2.processMonth(f);} })).then(()=>{P2.running=false;});
return 'started '+P2.queue.length;
})()
