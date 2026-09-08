// The page validates a view file before it renders it, against the same schema
// files the server validated against before it wrote it. A file that fails is
// an error panel naming the field, never a half-drawn panel.

import { Ajv2020 } from "ajv/dist/2020";
import type { ErrorObject, ValidateFunction } from "ajv/dist/2020";

import { fetchKinds, fetchSchema, type View } from "./api";

const ENVELOPE = "envelope";

const ajv = new Ajv2020({ allErrors: false });
const validators = new Map<string, ValidateFunction>();
let loading: Promise<void> | null = null;

/**
 * Fetch and compile the envelope schema and every registered kind's schema.
 *
 * Called once; a second call awaits the first. Every later validateView is
 * synchronous, so a view file reaches the screen without a round trip.
 */
export function loadSchemas(): Promise<void> {
  if (loading === null) {
    loading = compileAll();
  }
  return loading;
}

async function compileAll(): Promise<void> {
  const kinds = await fetchKinds();
  const names = [ENVELOPE, ...kinds.map((kind) => kind.name)];
  const schemas = await Promise.all(names.map((name) => fetchSchema(name)));
  names.forEach((name, index) => {
    validators.set(name, ajv.compile(schemas[index]));
  });
}

/** A view file that validated, or the field that rejected it. */
export type Validated = { ok: true; view: View } | { ok: false; error: string };

/**
 * Check one fetched view file against the envelope and then against its kind.
 *
 * loadSchemas must have finished; a call before that is a defect in the page,
 * not a bad view file, so it throws rather than answering with an error panel.
 */
export function validateView(json: unknown): Validated {
  const envelope = validators.get(ENVELOPE);
  if (envelope === undefined) {
    throw new Error("validateView before loadSchemas");
  }
  if (!envelope(json)) {
    return { ok: false, error: firstError(envelope, "") };
  }
  const view = json as View;
  const payload = validators.get(view.kind);
  if (payload === undefined) {
    // A refresh writes registered kinds only, so this is a view file left
    // behind by a kind that has since left the registry.
    return { ok: false, error: `/kind: no schema for ${view.kind}` };
  }
  if (!payload(view.payload)) {
    return { ok: false, error: firstError(payload, "/payload") };
  }
  return { ok: true, view };
}

/** The instance path and message of the first error, the only one Ajv kept. */
function firstError(validate: ValidateFunction, prefix: string): string {
  const errors: ErrorObject[] = validate.errors ?? [];
  const first = errors[0];
  if (first === undefined) {
    throw new Error("a failed validation reported no error");
  }
  const where = `${prefix}${first.instancePath}`;
  return `${where === "" ? "/" : where}: ${first.message ?? "invalid"}`;
}
