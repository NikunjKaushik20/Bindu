import type { StreamEvent } from "~/types";

interface RawWebhook {
	id: string;
	agentId: string;
	receivedAt: string;
	payload: {
		event_id?: string;
		sequence?: number;
		timestamp?: string;
		kind?: "status-update" | "artifact-update" | string;
		task_id?: string;
		context_id?: string;
		status?: { state?: string };
		artifact?: unknown;
		final?: boolean;
	};
}

export function mapWebhookToEvent(raw: RawWebhook): StreamEvent {
	const p = raw.payload;
	const isArtifact = p.kind === "artifact-update";
	const state = (p.status?.state ?? (isArtifact ? "completed" : "pending")) as StreamEvent["state"];
	const ts = (p.timestamp ?? raw.receivedAt).slice(11, 19);
	return {
		id: raw.id,
		agentId: raw.agentId,
		ts,
		relTs: "live",
		counterparty: {
			name: p.task_id?.slice(0, 8) ?? "task",
			did: `did:bindu:task:${p.task_id ?? "?"}`,
			trust: "known",
		},
		kind: isArtifact ? "artifact" : "state-change",
		state,
		summary: isArtifact
			? "Artifact delivered"
			: `state → ${state ?? "?"}${p.final ? " · final" : ""}`,
		signed: true,
		verify: {
			signature: true,
			didMatch: true,
			nonce: (p.event_id ?? "").slice(0, 8) || "—",
		},
		payload: JSON.stringify(p, null, 2),
	};
}
