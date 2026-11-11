from __future__ import annotations
import time,httpx
async def http_health(url:str,timeout:float=3.0)->dict:
    start=time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout) as c: r=await c.get(url)
        return {"ok":200<=r.status_code<500,"status_code":r.status_code,"latency_ms":round((time.perf_counter()-start)*1000,1),"body":r.text[:500]}
    except Exception as exc: return {"ok":False,"error":str(exc),"latency_ms":round((time.perf_counter()-start)*1000,1)}
def system_resources()->dict:
    try:
        import psutil
        from pathlib import Path
        vm=psutil.virtual_memory(); du=psutil.disk_usage(str(Path.cwd().anchor or "/"))
        return {"cpu_percent":psutil.cpu_percent(interval=.1),"ram_percent":vm.percent,"ram_available_gb":round(vm.available/1024**3,2),"disk_percent":du.percent,"disk_free_gb":round(du.free/1024**3,2)}
    except Exception as exc: return {"error":str(exc)}
