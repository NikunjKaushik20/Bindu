import { Hono } from "hono";
import { serve } from "@hono/node-server";

interface LiveEvent {
	id: string;
	agentId: string;
	receivedAt: string;
	payload: Record<string, unknown>;
}

const events: LiveEvent[] = [];
const subscribers = new Set<(e: LiveEvent) => void>();

const app = new Hono();

app.post("/webhooks/bindu/:agentId", async (c) => {
	const agentId = c.req.param("agentId");
	const payload = (await c.req.json()) as Record<string, unknown>;
	const ev: LiveEvent = {
		id: String(payload.event_id ?? crypto.randomUUID()),
		agentId,
		receivedAt: new Date().toISOString(),
		payload,
	};
	events.push(ev);
	if (events.length > 1000) events.shift();
	for (const cb of subscribers) cb(ev);
	console.log(`[webhook] ${agentId} ${payload.kind ?? "?"} ${payload.task_id ?? ""}`);
	return c.json({ ok: true });
});

app.get("/api/events/stream", (c) => {
	const agentFilter = c.req.query("agentId");
	const stream = new ReadableStream({
		start(controller) {
			const enc = new TextEncoder();
			const send = (e: LiveEvent) => {
				if (agentFilter && e.agentId !== agentFilter) return;
				controller.enqueue(enc.encode(`data: ${JSON.stringify(e)}\n\n`));
			};
			for (const e of events.slice(-50)) send(e);
			subscribers.add(send);
			c.req.raw.signal.addEventListener("abort", () => {
				subscribers.delete(send);
				controller.close();
			});
		},
	});
	return new Response(stream, {
		headers: {
			"content-type": "text/event-stream",
			"cache-control": "no-cache",
			connection: "keep-alive",
		},
	});
});

app.get("/api/agents", (c) =>
	c.json(Array.from(new Set(events.map((e) => e.agentId)))),
);

serve({ fetch: app.fetch, port: 3787 }, (info) => {
	console.log(`[bindu-communication] api on http://127.0.0.1:${info.port}`);
});
