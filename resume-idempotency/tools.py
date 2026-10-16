import json, sqlite3, time, uuid

db = sqlite3.connect("shop.db", timeout=30)
db.execute(
    "CREATE TABLE IF NOT EXISTS charges (charge_id, run_id, customer_id, amount_cents, ts)"
)
TOOLS = [
    {
        "name": "charge_customer",
        "description": "Charge a customer's card. Moves real money.",
        "input_schema": {
            "type": "object",
            "required": ["customer_id", "order_id", "amount_cents"],
            "properties": {
                "customer_id": {"type": "string"},
                "order_id": {"type": "string"},
                "amount_cents": {"type": "integer"},
            },},}]

db.execute("CREATE TABLE IF NOT EXISTS dedupe (key TEXT PRIMARY KEY, result TEXT)")

def charge_customer(run_id, arm, customer_id, order_id, amount_cents):
    key = f"{run_id}:{order_id}"  # same logical operation, same key, every single time
    with db:
        row = db.execute("SELECT result FROM dedupe WHERE key = ?", (key,)).fetchone()
        if arm == "idempotent" and row:
            return json.loads(row[0])  # already happened: hand back the original outcome
        charge_id = f"ch_{uuid.uuid4().hex[:8]}"
        db.execute("INSERT INTO charges VALUES (?, ?, ?, ?, ?)", (charge_id, run_id, customer_id, amount_cents, time.strftime("%H:%M:%S")))
        result = {"charge_id": charge_id, "amount_cents": amount_cents}
        if arm == "idempotent":
            db.execute("INSERT INTO dedupe VALUES (?, ?)", (key, json.dumps(result)))
    time.sleep(2)  # the network round trip: the charge landed, the response hasn't
    return result