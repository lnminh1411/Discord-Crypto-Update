import threading
import asyncio
import json
from okx.websocket.WsPublicAsync import WsPublicAsync
import datetime

def convert_time(ts):
    if not ts:
        return "N/A"
    try:
        dt = datetime.datetime.fromtimestamp(int(ts) / 1000, tz=datetime.timezone.utc)
        return dt.strftime("%H:%M:%S | %d/%m/%Y")
    except:
        return "N/A"

# WebSocket Status Monitor
class StatusMonitor:
    SERVICE_MAP = {
        "0": "WebSocket",
        "5": "Trading service",
        "6": "Block trading",
        "7": "Trading bot",
        "8": "Trading service (batches of accounts)",
        "9": "Trading service (batches of products)",
        "10": "Spread trading",
        "11": "Copy trading",
        "99": "Others"
    }
    
    MAINT_MAP = {
        "1": "Scheduled maintenance",
        "2": "Unscheduled maintenance",
        "3": "System disruption"
    }

    def __init__(self, callback, debug=False):
        self.callback = callback
        self.debug = debug
        self.active_events = {}
        self.ws = None
        self.loop = None
        self.thread = None
        self.stop_event = threading.Event()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
            
        self.thread = threading.Thread(target=self._run_ws, daemon=True)
        self.thread.start()
        if self.debug:
            print("Status monitor started")

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        if self.debug:
            print("Status monitor stopped")

    def _run_ws(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._websocket_handler())

    async def _websocket_handler(self):
        try:
            self.ws = WsPublicAsync(url="wss://wspap.okx.com:8443/ws/v5/public", debug=self.debug)
            await self.ws.start()
            
            # Subscribe to status channel
            await self.ws.subscribe([{"channel": "status"}], self._handle_message)
            
            # Keep connection alive
            while not self.stop_event.is_set():
                await asyncio.sleep(0.5)
        except Exception as e:
            if self.debug:
                print(f"WebSocket error: {e}")
        finally:
            if self.ws:
                await self.ws.close()

    def _handle_message(self, message):
        try:
            msg = json.loads(message)
            
            # Handle status updates
            if "arg" in msg and msg["arg"].get("channel") == "status" and "data" in msg:
                events = msg["data"]
                if not isinstance(events, list):
                    events = [events]
                    
                new_events = []
                for event in events:
                    # Only process production events
                    if event.get("env") != "1":
                        continue
                        
                    # Generate unique event ID
                    event_id = f"{event.get('begin')}-{event.get('title')}"
                    
                    # Skip duplicates and completed/canceled events
                    if event_id in self.active_events:
                        continue
                        
                    if event.get("state") in ["completed", "canceled"]:
                        continue
                        
                    # Process event
                    processed = self._process_event(event)
                    new_events.append(processed)
                    self.active_events[event_id] = processed
                    
                # Trigger callback with new events
                if new_events and self.callback:
                    self.callback(new_events)
                    
            # Handle subscription confirmation
            elif msg.get("event") == "subscribe" and msg["arg"].get("channel") == "status":
                if self.debug:
                    print("Successfully subscribed to status channel")
                    
            # Handle errors
            elif msg.get("event") == "error":
                print(f"WebSocket error: {msg.get('msg')} (code: {msg.get('code')})")
                
        except Exception as e:
            if self.debug:
                print(f"Message handling error: {e}")

    def _process_event(self, event):
        return {
            "title": event.get("title", ""),
            "begin": convert_time(event.get("begin")),
            "end": convert_time(event.get("end")),
            "serviceType": self.SERVICE_MAP.get(event.get("serviceType", ""), "Unknown"),
            "href": event.get("href", ""),
            "mainType": self.MAINT_MAP.get(event.get("mainType", ""), "Unknown"),
            "state": event.get("state", ""),
            "preOpenBegin": convert_time(event.get("preOpenBegin")),
            "raw": event
        }