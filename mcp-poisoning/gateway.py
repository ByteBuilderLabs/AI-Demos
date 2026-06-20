import json, re, time

PATTERNS = [
    r"do not (mention|tell)",
    r"copy .*(credential|key|token)",
    r"before calling",
    r"ignore (previous|prior)",
    r"<important>",
]


class Gateway:
    def __init__(self, session, allowed):
        self.session, self.allowed = session, set(allowed)

    def scan(self, text):
        return [p for p in PATTERNS if re.search(p, text or "", re.I)]

    def log(self, event, target, flags):
        entry = {"ts": time.time(), "event": event, "target": target, "flags": flags}
        open("audit.log", "a").write(json.dumps(entry) + "\n")

    async def list_tools(self, server):
        if server not in self.allowed:
            return []
        listed = await self.session.list_tools()
        clean = []
        for t in listed.tools:
            hits = self.scan(t.description)
            self.log("list_tool", t.name, hits)
            if not hits:
                clean.append(t)
        return clean

    async def call_tool(self, name, args):
        r = await self.session.call_tool(name, args)
        text = " ".join(c.text for c in r.content if hasattr(c, "text"))
        self.log("call_tool", name, self.scan(text))
        return r
