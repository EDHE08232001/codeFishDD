import React from 'react';

export default function Codfish({className='',species='cod'}){
  if(species!=='cod')return <svg className={`codfish ${className}`} width="160" height="96" viewBox="0 0 160 96" shapeRendering="crispEdges" aria-hidden="true">
    {species==='clown'&&<><path d="M12 28h16v12h16V28h16V20h56v8h16v12h12v24h-12v12h-16v8H60v-8H44V64H28v12H12z" fill="#193755"/><path d="M20 36h8v12h24V32h16V28h44v8h16v12h8v12h-8v12h-16v4H68v-8H52V56H28v12h-8z" fill="#ff9646"/><path d="M60 28h12v48H60zM92 28h12v48H92zM28 40h8v24h-8z" fill="#fff2c8"/><rect x="112" y="40" width="12" height="16" fill="#153451"/></>}
    {species==='tang'&&<><path d="M12 32h16v12h16V28h16V16h56v12h16v12h12v24h-12v12h-16v8H60V72H44V56H28v12H12z" fill="#162f59"/><path d="M48 36h20V24h40v12h16v12h12v12h-12v8h-16v8H68V64H48z" fill="#439cff"/><path d="M20 40h12v8h16v8H32v4H20zM68 16h40v8H68z" fill="#ffe363"/><path d="M64 40h40v8H80v16H64z" fill="#214da1"/><rect x="112" y="40" width="12" height="12" fill="#effeff"/><rect x="116" y="44" width="8" height="8" fill="#142944"/></>}
    {species==='puffer'&&<><path d="M52 8h12v12h12V8h12v12h16V8h12v20h12v12h16v12h-12v16h12v12h-28v8H64v-8H48V68H24V56H12V40h24V28h16z" fill="#173c50"/><path d="M56 28h56v12h12v28h-12v12H64V68H48V40h8zM20 44h20v8H20z" fill="#ffe36e"/><path d="M56 60h64v8h-8v12H64V68h-8z" fill="#fff2c3"/><rect x="96" y="36" width="12" height="16" fill="#193451"/>{[56,72,88].map(x=><rect key={x} x={x} y="44" width="4" height="4" fill="#c89c37"/>)}</>}
    {species==='angel'&&<><path d="M76 4h16v12h16v16h16v12h20v16h-20v12h-16v12H92v8H76V76H56V64H32v12H16V28h16v12h24V28h20z" fill="#163954"/><path d="M80 16h8v16h16v12h20v16h-20v12H88v12h-8V68H64V56H32v8h-8V40h8v8h32V36h16z" fill="#e89dff"/><path d="M80 32h8v40h-8zM100 44h8v20h-8z" fill="#ffe39a"/><rect x="112" y="44" width="8" height="12" fill="#1a3658"/></>}
    {species==='butterfly'&&<><path d="M12 28h16v12h20V28h16V16h40v12h16v12h16v28h-16v12h-16v8H64V76H48V60H28v12H12z" fill="#193955"/><path d="M20 36h8v12h28V36h16V24h24v12h16v12h16v16h-16v8H96v8H72V68H56V52H28v12h-8z" fill="#ffcd42"/><path d="M68 28h12v48H68zM92 36h8v36h-8z" fill="#fff7d7"/><rect x="112" y="44" width="8" height="12" fill="#173451"/></>}
    <rect x="142" y="12" width="8" height="8" fill="none" stroke="#86f1eb" strokeWidth="2"/>
  </svg>;
  return <svg className={`codfish ${className}`} width="160" height="96" viewBox="0 0 160 96" shapeRendering="crispEdges" aria-hidden="true">
    <path d="M8 28h12v12h12V28h16V16h32V8h32v8h20v12h12v40h-12v12h-20v8H64v-8H48V68H32V56H20v12H8z" fill="#083145"/>
    <path d="M16 36h8v12h16V36h16V24h64v8h16v32h-16v12H64V68H48V56H24v4h-8z" fill="#82e5cf"/>
    <path d="M56 24h64v8H56zM48 36h32v8H48z" fill="#c6f7da"/>
    <path d="M64 68h56v8H64zM80 76h16v8H80z" fill="#38a6ab"/>
    <path d="M72 16h24v8H72zM64 56h16v16H64z" fill="#b6a1f4"/>
    <rect x="104" y="32" width="16" height="20" fill="#effbff"/><rect x="112" y="36" width="8" height="12" fill="#102c46"/>
    <rect x="124" y="56" width="12" height="4" fill="#1d6675"/><rect x="112" y="64" width="4" height="12" fill="#c6f7da"/>
    <rect x="52" y="40" width="4" height="4" fill="#399ca2"/><rect x="68" y="32" width="4" height="4" fill="#399ca2"/><rect x="84" y="40" width="4" height="4" fill="#399ca2"/>
    <rect x="142" y="12" width="8" height="8" fill="none" stroke="#82dce4" strokeWidth="2"/>
  </svg>;
}
