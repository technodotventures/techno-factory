PRD sections — 'Pod Capabilities PRD' (verbatim)
§15.1 Capability cards
Cards show type, name, description, revision, source, freshness, component counts, risk summary, Library or Inbox status, deployment count, and update state. Type must be scannable without relying on colour alone.
§15.2 Review panel
The panel presents, in order:
• identity, source, author, version, package hash, and specification;
• plain-language summary of what changed;
• component additions, removals, changes, invalid items, and unsupported items;
• runtime review: executables, remote connections, headers, binaries, permissions, and credentials;
• file list and expandable diff;
• compatibility and deployment implications;
• approve, reject, export, or defer actions.
§15.3 Freshness language
The UI must avoid implying real-time behaviour when a source is cached or polling. Use explicit labels such as "Live webhook," "Checked 4 minutes ago," "Cached result, 2 days old," "Refresh failed," and "Never synced." A refresh icon without status is insufficient.
§15.4 Empty and failure states
Empty states explain the next productive action: scan connected agents, import a Skill or Plugin, connect a source, or create a Capability set. Failures preserve the last known good Library and offer retry or diagnostics without exposing secrets.
§9 Capability lifecycle
§9.1 Revision states
• Detected: source metadata or package has been observed.
• Draft: a complete candidate revision exists in Pod.
• Needs review: the revision differs from the approved canonical revision or has never been approved.
• Approved: the owner accepted the revision into the Library.
• Rejected: the owner declined the revision; the decision and reason remain auditable.
• Superseded: a later revision became canonical.
• Retired: the Capability is no longer offered for new deployments, while history remains.
§9.2 Deployment states
• Unassessed: no adapter evaluation has run.
• Unsupported: target agent cannot consume the aggregate or required component.
• Needs binding: required credential or account mapping is absent.
• Ready: compatible and fully bound.
• Materializing: adapter operation is in progress.
• Synchronized: Pod re-read the target and its observed package digest matches the approved revision.
• Update available: synchronized revision is older than the canonical revision.
• Drifted: files differ without a known canonical revision transition.
• Failed: the last bounded operation failed and exposes a retryable diagnostic.
• Removed: deployment was intentionally uninstalled or revoked.