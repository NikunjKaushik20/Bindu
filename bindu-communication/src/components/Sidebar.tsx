import { useEffect, useState } from "react";
import { NavLink } from "react-router";
import { PlusIcon, GlobeIcon } from "@phosphor-icons/react";
import { scopes } from "~/data/mock";
import { useUI } from "~/state";
import { shortDid } from "~/lib/format";
import { AddAgentModal } from "./AddAgentModal";
import clsx from "clsx";

interface EcosystemAgent {
	id: string;
	url?: string;
	did?: { id?: string } | null;
	agentCard?: { name?: string } | null;
	source: "webhook" | "manual";
}

function useEcosystem() {
	const [list, setList] = useState<EcosystemAgent[]>([]);
	const [tick, setTick] = useState(0);
	useEffect(() => {
		let cancelled = false;
		const refresh = () =>
			fetch("/api/ecosystem")
				.then((r) => (r.ok ? r.json() : []))
				.then((j) => {
					if (!cancelled) setList(j as EcosystemAgent[]);
				})
				.catch(() => {});
		refresh();
		const t = setInterval(refresh, 5000);
		return () => {
			cancelled = true;
			clearInterval(t);
		};
	}, [tick]);
	return { list, reload: () => setTick((n) => n + 1) };
}

export function Sidebar() {
	const scopeFilter = useUI((s) => s.scopeFilter);
	const setScope = useUI((s) => s.setScope);
	const agents = useUI((s) => s.agents);
	const openRegister = useUI((s) => s.openRegister);
	const [showAdd, setShowAdd] = useState(false);
	const { list: ecosystem, reload: reloadEcosystem } = useEcosystem();

	return (
		<aside className="flex w-[280px] shrink-0 flex-col border-r border-[--color-border-soft] bg-[--color-sidebar]">
			{/* Brand */}
			<div className="flex items-center gap-2.5 border-b border-[--color-border-soft] px-4 py-4">
				<img
					src="/bindu.png"
					alt="Bindu"
					className="h-8 w-8 shrink-0 select-none"
					draggable={false}
				/>
				<div>
					<div className="text-[10px] uppercase tracking-[0.2em] text-fg-dim">
						Bindu
					</div>
					<div className="text-[14px] font-medium text-fg">Communications</div>
				</div>
			</div>

			{/* Register agent */}
			<div className="px-3 pt-4">
				<button
					type="button"
					onClick={openRegister}
					className="group flex w-full items-center gap-2 rounded-md bg-[--color-cobalt] px-3 py-2 text-left text-[12px] font-medium text-white shadow-sm transition hover:bg-[--color-cobalt-strong]"
				>
					<PlusIcon size={14} weight="bold" />
					<span>Register agent</span>
					<span className="ml-auto rounded bg-white/15 px-1 text-[10px] text-white/80">
						⌘N
					</span>
				</button>
			</div>

			{/* Agents (running/recent — Step 1 will fold these into the ecosystem) */}
			<nav className="px-3 pt-4">
				<div className="px-2 pb-2 text-[10px] uppercase tracking-[0.15em] text-fg-dim">
					Agents
				</div>
				{agents.map((a) => (
					<NavLink
						key={a.id}
						to={`/agents/${a.id}`}
						className={({ isActive }) =>
							clsx(
								"group flex w-full items-center justify-between rounded-md px-2 py-2 text-left transition",
								isActive
									? "bg-[--color-cobalt-soft] text-fg"
									: "text-fg-muted hover:bg-[--color-row-hover]",
							)
						}
					>
						<div className="flex min-w-0 items-center gap-2.5">
							{a.role === "gateway" ? (
								<span
									className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[--color-cobalt] text-[10px] font-semibold text-white"
									title="Gateway"
								>
									GW
								</span>
							) : (
								<img
									src="/bindu.png"
									alt=""
									className="h-7 w-7 shrink-0 select-none"
									draggable={false}
									title="Agent (bindu)"
								/>
							)}
							<div className="min-w-0">
								<div className="truncate text-[13px] text-fg">{a.name}</div>
								<div className="truncate text-[10px] text-fg-dim">
									{shortDid(a.did)}
								</div>
							</div>
						</div>
						{a.needsAttention > 0 ? (
							<span className="ml-2 rounded-full bg-[--color-sunflower] px-1.5 text-[10px] font-semibold text-yellow-900">
								{a.needsAttention}
							</span>
						) : a.unread > 0 ? (
							<span className="ml-2 rounded-full bg-slate-200 px-1.5 text-[10px] text-slate-700">
								{a.unread}
							</span>
						) : null}
					</NavLink>
				))}
			</nav>

			{/* Ecosystem — known agents (webhook-seen + manually added) */}
			<div className="mt-6 px-3">
				<div className="flex items-center justify-between px-2 pb-2">
					<div className="flex items-center gap-1.5 text-[10px] uppercase tracking-[0.15em] text-fg-dim">
						<GlobeIcon size={11} weight="bold" />
						Ecosystem
					</div>
					<button
						type="button"
						onClick={() => setShowAdd(true)}
						title="Add agent by URL"
						className="rounded p-0.5 text-fg-dim transition hover:bg-slate-100 hover:text-[--color-cobalt]"
					>
						<PlusIcon size={12} weight="bold" />
					</button>
				</div>
				{ecosystem.length === 0 ? (
					<div className="px-2 py-1 text-[10px] text-fg-dim">
						No agents yet. Click + to add by URL.
					</div>
				) : (
					ecosystem.map((a) => {
						const name = a.agentCard?.name ?? a.id;
						const didId = a.did?.id ?? `did:bindu:?:${a.id}`;
						return (
							<div
								key={a.id}
								className="flex w-full items-center gap-2.5 rounded-md px-2 py-1.5 text-left"
								title={didId}
							>
								<span
									className={clsx(
										"flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[9px] font-semibold",
										a.source === "manual"
											? "bg-[--color-cobalt-soft] text-[--color-cobalt-strong]"
											: "bg-yellow-100 text-yellow-800",
									)}
								>
									{a.source === "manual" ? "+" : "●"}
								</span>
								<div className="min-w-0 flex-1">
									<div className="truncate text-[12px] text-fg">{name}</div>
									<div className="truncate text-[10px] text-fg-dim">
										{shortDid(didId)}
									</div>
								</div>
							</div>
						);
					})
				)}
			</div>

			{/* Scopes */}
			<div className="mt-6 px-3">
				<div className="px-2 pb-2 text-[10px] uppercase tracking-[0.15em] text-fg-dim">
					Scopes
				</div>
				{scopes.map((s) => (
					<button
						key={s.id}
						type="button"
						onClick={() => setScope(s.id)}
						className={clsx(
							"flex w-full items-center justify-between rounded-md px-2 py-1.5 text-left text-[12px] transition",
							scopeFilter === s.id
								? "bg-[--color-cobalt-soft] text-fg"
								: "text-fg-muted hover:bg-[--color-row-hover]",
						)}
					>
						<span>#{s.name}</span>
						<span className="text-[10px] text-fg-dim">{s.count}</span>
					</button>
				))}
			</div>

			{/* You */}
			<div className="mt-auto border-t border-[--color-border-soft] px-4 py-3">
				<div className="text-[10px] text-fg-dim">
					You: <span className="text-fg-muted">raahul@getbindu</span>
				</div>
				<div className="mt-0.5 text-[10px] text-fg-dim">
					did:bindu:raahul:0001
				</div>
			</div>

			<AddAgentModal
				open={showAdd}
				onClose={() => setShowAdd(false)}
				onAdded={() => reloadEcosystem()}
			/>
		</aside>
	);
}
