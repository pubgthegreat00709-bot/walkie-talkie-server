import socketio
from aiohttp import web
import os

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

active_talkers = {}
packet_counters = {}

print("=============================================", flush=True)
print("🚀 DIY WALKIE-TALKIE SERVER v3.0 IS AWAKE 🚀", flush=True)
print("=============================================", flush=True)

# ---> NEW: A Web Page to test if the server is actually alive! <---
async def index(request):
    return web.Response(text="<h1>Walkie-Talkie Server is LIVE!</h1><p>The post office is open and ready to route audio.</p>", content_type='text/html')
app.router.add_get('/', index)

@sio.event
async def connect(sid, environ):
    print(f"\n[+] NEW CONNECTION: User {sid} connected!", flush=True)

@sio.event
async def disconnect(sid):
    print(f"[-] DISCONNECT: User {sid} disconnected.", flush=True)

@sio.on('join_frequency')
async def handle_join(sid, frequency):
    freq_str = str(frequency)
    rooms = sio.rooms(sid)
    for room in rooms:
        if room != sid:
            sio.leave_room(sid, room)
    sio.enter_room(sid, freq_str)
    print(f"[ROOM] >>> User {sid} successfully locked into Frequency: {freq_str}", flush=True)

@sio.on('start_talking')
async def start_talking(sid, frequency):
    freq = str(frequency)
    active_talkers[freq] = active_talkers.get(freq, 0) + 1
    print(f"[MIC OPEN] {sid} is transmitting on {freq}", flush=True)

@sio.on('stop_talking')
async def stop_talking(sid, frequency):
    freq = str(frequency)
    active_talkers[freq] = max(0, active_talkers.get(freq, 1) - 1)
    print(f"[MIC CLOSED] {sid} stopped transmitting", flush=True)

@sio.on('voice_data')
async def handle_voice(sid, data):
    packet_counters[sid] = packet_counters.get(sid, 0) + 1
    # Only print every 20 packets so we don't spam the logs and crash Render
    if packet_counters[sid] % 20 == 0:
        print(f"[AUDIO TRACE] Relayed 20 audio packets from {sid}", flush=True)

    rooms = sio.rooms(sid)
    for freq in rooms:
        if freq != sid:
            await sio.emit('voice_receive', data, room=freq, skip_sid=sid)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting web server on port {port}...", flush=True)
    web.run_app(app, port=port)
