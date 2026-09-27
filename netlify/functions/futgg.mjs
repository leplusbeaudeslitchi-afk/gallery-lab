export default async (request) => {
  const u=new URL(request.url), path=u.searchParams.get("path");
  if(!path || !/^\/api\/fut\//.test(path)) return new Response("bad path",{status:400});
  const r=await fetch("https://www.fut.gg"+path,{headers:{"accept":"application/json","user-agent":"GalleryLab/1.0"}});
  return new Response(await r.arrayBuffer(),{status:r.status,headers:{"content-type":r.headers.get("content-type")||"application/json","cache-control":"public,max-age=600","access-control-allow-origin":"*"}});
};