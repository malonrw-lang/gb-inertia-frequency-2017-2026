// In-browser pipeline: NESO 1-s frequency -> UTC half-hour summaries + loss events.
// Follows PREREGISTRATION_grid_inertia.md. Injected into a neso.energy tab.
(function(){
if (window.GP && window.GP.version === 4) return 'already loaded';
const OLD = window.GP || {};
if (OLD.queue) OLD.queue.length = 0;   // stop old workers picking up new months
const GP = window.GP = {version:4, bins:{}, events:{}, qc:{}, status:{}, log:[], idb:OLD.idb};
for (const k of Object.keys(OLD.qc||{})) { GP.bins[k]=OLD.bins[k]; GP.events[k]=OLD.events[k]; GP.qc[k]=OLD.qc[k]; GP.status[k]='done'; }

function parseTs(s){
  // old: "2017-07-01 01:00:00 +0100" ; new: "2026-10-01 00:00:01" or "2026-10-01" (GMT)
  if (s.length === 10) return Date.UTC(+s.slice(0,4), +s.slice(5,7)-1, +s.slice(8,10)) / 1000;
  const y=+s.slice(0,4), mo=+s.slice(5,7)-1, d=+s.slice(8,10), h=+s.slice(11,13), mi=+s.slice(14,16), se=+s.slice(17,19);
  let t = Date.UTC(y,mo,d,h,mi,se)/1000;
  if (s.length > 20) { // offset like +0100
    const sign = s[20] === '-' ? -1 : 1; const oh=+s.slice(21,23), om=+s.slice(23,25);
    t -= sign*(oh*3600+om*60);
  }
  return t;
}

async function fetchRange(url, a, b, tries){
  for (let i=0;i<tries;i++){
    const ac = new AbortController(); const to = setTimeout(()=>ac.abort(), 90000);
    try {
      const r = await fetch(url, {headers:{Range:`bytes=${a}-${b}`}, signal:ac.signal, cache:'no-store'});
      if (r.status !== 206 && r.status !== 200) throw new Error('HTTP '+r.status);
      const buf = new Uint8Array(await r.arrayBuffer()); clearTimeout(to);
      if (r.status === 200) return {whole:buf};
      return {buf, total:+(r.headers.get('content-range')||'/0').split('/')[1]};
    } catch(e){ clearTimeout(to); if (i===tries-1) throw e; await new Promise(r=>setTimeout(r, 2000*(i+1))); }
  }
}
GP.CH = 8e6; GP.PAR = 3;
async function getBytes(url){
  const first = await fetchRange(url, 0, GP.CH-1, 5);
  if (first.whole) return first.whole;
  const total = first.total; const out = new Uint8Array(total); out.set(first.buf, 0);
  const starts = []; for (let a=first.buf.length; a<total; a+=GP.CH) starts.push(a);
  let idx = 0;
  const worker = async()=>{ while(idx<starts.length){ const a=starts[idx++]; const b=Math.min(a+GP.CH, total)-1; const r=await fetchRange(url,a,b,5); if(r.buf.length!==b-a+1) throw new Error('short chunk'); out.set(r.buf, a); } };
  await Promise.all(Array.from({length:GP.PAR}, worker));
  return out;
}
async function getText(f){
  const buf = await getBytes(f.url);
  if (f.ext === 'csv') return new TextDecoder().decode(buf);
  const dv = new DataView(buf.buffer);
  if (dv.getUint32(0,true) !== 0x04034b50) throw new Error('not zip');
  const method = dv.getUint16(8,true), csize = dv.getUint32(18,true), nlen = dv.getUint16(26,true), elen = dv.getUint16(28,true);
  const start = 30+nlen+elen;
  const data = buf.subarray(start, start+csize);
  if (method === 0) return new TextDecoder().decode(data);
  const ds = new DecompressionStream('deflate-raw');
  const stream = new Blob([data]).stream().pipeThrough(ds).pipeThrough(new TextDecoderStream());
  const reader = stream.getReader(); const parts=[];
  while(true){ const {done,value}=await reader.read(); if(done)break; parts.push(value); }
  return parts.join('');
}

function analyse(text, key){
  const lines = text.split('\n');
  const N = lines.length;
  const T = new Float64Array(N), F = new Float32Array(N);
  let n=0, bad=0;
  for (let i=1;i<N;i++){
    let L = lines[i]; if (!L) continue; if (L.charCodeAt(L.length-1)===13) L=L.slice(0,-1); if(!L) continue;
    const c = L.indexOf(','); if (c<0){bad++;continue;}
    const t = parseTs(L.slice(0,c)); const f = +L.slice(c+1);
    if (!isFinite(t) || !isFinite(f) || f<45 || f>55){bad++;continue;}
    T[n]=t; F[n]=f; n++;
  }
  // order check
  let nonmono=0, dup=0, gaps=0, missing=0;
  for (let i=1;i<n;i++){ const d=T[i]-T[i-1]; if(d<0)nonmono++; else if(d===0)dup++; else if(d>1){gaps++; missing+=d-1;} }
  // bins
  const b0 = Math.floor(T[0]/1800), b1 = Math.floor(T[n-1]/1800);
  const nb = b1-b0+1;
  const cnt=new Int32Array(nb), sum=new Float64Array(nb), mn=new Float32Array(nb).fill(99), mx=new Float32Array(nb).fill(0), out=new Int32Array(nb);
  for (let i=0;i<n;i++){ const b=Math.floor(T[i]/1800)-b0; if(b<0||b>=nb)continue; cnt[b]++; sum[b]+=F[i]; if(F[i]<mn[b])mn[b]=F[i]; if(F[i]>mx[b])mx[b]=F[i]; if(F[i]<49.8||F[i]>50.2)out[b]++; }
  const mean=new Float64Array(nb); for(let b=0;b<nb;b++) mean[b]= cnt[b]? sum[b]/cnt[b] : NaN;
  const ss=new Float64Array(nb), cross=new Float64Array(nb), npair=new Int32Array(nb);
  const H = new Int32Array(nb*1001);
  for (let i=0;i<n;i++){
    const b=Math.floor(T[i]/1800)-b0; if(b<0||b>=nb)continue; const dv=F[i]-mean[b]; ss[b]+=dv*dv;
    if (i>0 && T[i]-T[i-1]===1 && Math.floor(T[i-1]/1800)-b0===b){
      cross[b]+=dv*(F[i-1]-mean[b]); npair[b]++;
      let a=Math.round(Math.abs(F[i]-F[i-1])*1000); if(a>1000)a=1000; H[b*1001+a]++;
    }
  }
  const rows=[];
  for (let b=0;b<nb;b++){
    if(!cnt[b]) continue;
    const base=b*1001, np=npair[b];
    let p99=NaN,p999=NaN,amax=0,n20=0,n50=0;
    if (np>0){ let acc=0; const t99=Math.ceil(0.99*np), t999=Math.ceil(0.999*np);
      for(let a=0;a<=1000;a++){ const h=H[base+a]; if(!h)continue; const prev=acc; acc+=h; if(isNaN(p99)&&acc>=t99)p99=a; if(isNaN(p999)&&acc>=t999)p999=a; amax=a; if(a>=20)n20+=h; if(a>=50)n50+=h; } }
    const sd = cnt[b]>1? Math.sqrt(ss[b]/(cnt[b]-1)) : NaN;
    const r1 = ss[b]>0? cross[b]/ss[b] : NaN;
    rows.push([(b0+b)*1800, cnt[b], np, mean[b].toFixed(5), sd.toFixed(6), mn[b].toFixed(3), mx[b].toFixed(3), p99, p999, amax, n20, n50, out[b], isFinite(r1)?r1.toFixed(5):'' ].join(','));
  }
  // loss events (pre-registered definition)
  const ev=[]; let lastEv=-1e12;
  for (let i=10;i<n-60;i++){
    if (T[i]-T[i-1]!==1) continue;
    const dfx = F[i]-F[i-1];
    if (dfx > -0.020) continue;
    if (T[i]-lastEv < 120) continue;
    if (T[i]-T[i-10]!==10) continue;
    let pm=0; for(let k=i-10;k<i;k++) pm+=F[k]; pm/=10;
    let min30=99; for(let k=i;k<n && T[k]-T[i]<=30;k++) if(F[k]<min30)min30=F[k];
    if (min30 > pm-0.100) continue;
    let rmax=0; for(let k=i;k<n && T[k]-T[i]<=5;k++){ if(k>0 && T[k]-T[k-1]===1){ const fall=F[k-1]-F[k]; if(fall>rmax)rmax=fall; } }
    let min60=99, tmin=0; for(let k=i;k<n && T[k]-T[i]<=60;k++) if(F[k]<min60){min60=F[k]; tmin=T[k]-T[i];}
    ev.push([T[i], (rmax*1000).toFixed(0), ((pm-min60)*1000).toFixed(0), pm.toFixed(3), tmin].join(','));
    lastEv = T[i];
  }
  return {rows, ev, qc:{key, rows:n, bad, nonmono, dup, gaps, missing, first:T[0], last:T[n-1], bins:rows.length, events:ev.length}};
}

GP.processMonth = async function(f){
  const key = f.y+'-'+String(f.m).padStart(2,'0');
  GP.status[key]='fetching'; const t0=performance.now();
  try{
    const text = await getText(f);
    GP.status[key]='parsing';
    const res = analyse(text, key);
    GP.bins[key]=res.rows; GP.events[key]=res.ev; res.qc.sec=((performance.now()-t0)/1000).toFixed(0); res.qc.file=f.file; GP.qc[key]=res.qc;
    GP.status[key]='done';
    if (GP.idb) await new Promise(res=>{const tx=GP.idb.transaction('m','readwrite'); tx.objectStore('m').put({bins:GP.bins[key],events:GP.events[key],qc:GP.qc[key]}, key); tx.oncomplete=()=>res(1); tx.onerror=()=>res(0);});
  }catch(e){ GP.status[key]='error: '+e; GP.log.push(key+' '+e); }
};

GP.run = async function(list, conc){
  GP.queue = list.slice(); const workers=[];
  for(let w=0;w<conc;w++) workers.push((async()=>{ while(GP.queue.length){ const f=GP.queue.shift(); await GP.processMonth(f); } })());
  GP.running=true; await Promise.all(workers); GP.running=false;
};

GP.summary = function(){
  const s={}; for(const [k,v] of Object.entries(GP.status)){ s[v.startsWith('error')?'error':v]=(s[v.startsWith('error')?'error':v]||0)+1; }
  return {counts:s, queue:GP.queue?GP.queue.length:0, running:GP.running, errors:GP.log.slice(-5)};
};

GP.download = function(name, text){
  const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([text],{type:'text/csv'})); a.download=name; document.body.appendChild(a); a.click(); a.remove();
};
GP.exportAll = function(prefix){
  const keys=Object.keys(GP.bins).sort();
  const bins=['bin_utc,n,npair,mean,sd,min,max,p99_mHz,p999_mHz,max_mHz,n_ge20,n_ge50,n_outband,r1'].concat(...keys.map(k=>GP.bins[k])).join('\n');
  const ev=['t_utc,rocof_mHz,depth_mHz,pre_mean,t_to_min_s'].concat(...keys.map(k=>GP.events[k])).join('\n');
  const qk=Object.keys(GP.qc).sort(); const qc=['month,file,rows,bad,nonmono,dup,gaps,missing,first,last,bins,events,sec'].concat(qk.map(k=>{const q=GP.qc[k]; return [k,q.file,q.rows,q.bad,q.nonmono,q.dup,q.gaps,q.missing,q.first,q.last,q.bins,q.events,q.sec].join(',');})).join('\n');
  GP.download(prefix+'_bins.csv', bins); GP.download(prefix+'_events.csv', ev); GP.download(prefix+'_qc.csv', qc);
  return {bins:bins.length, ev:ev.length, qc:qc.length};
};
return 'loaded';
})();
