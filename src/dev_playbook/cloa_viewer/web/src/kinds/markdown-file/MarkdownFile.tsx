// Everything about one markdown file: the frontmatter facts, the headings, the
// links either way, and the source as the reader sees it. It is the detail
// panel behind a CLOA panel, and the default panel for a file with no CLOA
// kind, so it is the only place the raw document appears on screen.

import MarkdownIt from "markdown-it";
import { useMemo, type MouseEvent, type ReactNode } from "react";

import type { Viewer } from "../../store";
import type { RendererProps } from "../index";

/** One heading, with the anchor slug GitHub gives it. */
export interface Heading {
  level: number;
  text: string;
  slug: string;
}

// How a link out resolved, as the generator scored it. Only "broken" is red:
// "decision-record" — a stale link out of an immutable Decision Record — and
// "citation" both take the neutral .badge style, because neither is a defect.
export type LinkStatus =
  | "external"
  | "citation"
  | "ok"
  | "decision-record"
  | "broken";

/** One link the file makes: as written, how it resolved, and what it names. */
export interface Link {
  target: string;
  status: LinkStatus;
  identity: string | null;
}

/** The markdown-file payload, as its schema fixes it. */
export interface MarkdownFilePayload {
  type: string | null;
  title: string | null;
  description: string | null;
  headings: Heading[];
  links_out: Link[];
  links_in: string[];
  source: string;
}

const HEADING_INDENT_PX = 12;

// html: false. The source is a file from the checkout and the page shows what
// its markdown says, never markup the file happens to carry.
const MARKDOWN = new MarkdownIt({ html: false, linkify: false });

export function MarkdownFile({ view, viewer }: RendererProps) {
  // The view validated against markdown-file.schema.json before it reached the
  // store, so the payload is this shape and the page does not check again.
  const payload = view.payload as unknown as MarkdownFilePayload;
  const source = useMemo(() => split(payload.source), [payload.source]);
  const rendered = useMemo(() => MARKDOWN.render(source.body), [source.body]);
  const byTarget = useMemo(
    () => new Map(payload.links_out.map((link) => [link.target, link])),
    [payload.links_out],
  );
  return (
    <div className="file">
      <div className="file-facts">
        <Fact name="type" value={payload.type ?? "—"} />
        <Fact name="headings" value={String(payload.headings.length)} />
      </div>
      <Section title="Headings">
        {payload.headings.map((heading) => (
          <li
            key={heading.slug}
            className="file-heading"
            style={{ paddingLeft: `${(heading.level - 1) * HEADING_INDENT_PX}px` }}
          >
            {heading.text}
          </li>
        ))}
      </Section>
      <Section title="Links out">
        {payload.links_out.map((link, index) => (
          <li key={`${String(index)} ${link.target}`} className="file-link">
            <span className={`badge badge-${link.status}`}>{link.status}</span>
            <Target viewer={viewer} identity={link.identity} label={link.target} />
          </li>
        ))}
      </Section>
      <Section title="Links in">
        {payload.links_in.map((identity) => (
          <li key={identity} className="file-link">
            <Target viewer={viewer} identity={identity} label={identity} />
          </li>
        ))}
      </Section>
      <div className="file-source">
        {source.frontmatter === null ? null : (
          <pre className="file-frontmatter">{source.frontmatter}</pre>
        )}
        <div
          onClick={(event) => {
            followLink(event, viewer, byTarget);
          }}
          // The markdown is rendered with html: false, so this is markdown-it's
          // own output and nothing the source file wrote.
          dangerouslySetInnerHTML={{ __html: rendered }}
        />
      </div>
    </div>
  );
}

/** A file's source in the two languages it is written in. */
interface Source {
  frontmatter: string | null;
  body: string;
}

/**
 * The frontmatter block and the markdown body, told apart.
 *
 * The payload carries the file as written, and markdown-it reads a frontmatter
 * block as a setext heading — the closing fence underlines the last key — so
 * rendering the whole source puts the YAML on screen as one enormous title.
 * The block is YAML, so the page shows it as YAML.
 */
function split(source: string): Source {
  if (!source.startsWith("---\n")) {
    return { frontmatter: null, body: source };
  }
  const close = source.indexOf("\n---\n", "---".length);
  if (close === -1) {
    return { frontmatter: null, body: source };
  }
  return {
    frontmatter: source.slice("---\n".length, close + 1),
    body: source.slice(close + "\n---\n".length),
  };
}

function Fact({ name, value }: { name: string; value: string }) {
  return (
    <span className={`file-fact file-fact-${name}`}>
      <span className="file-fact-name">{name}</span>
      <span className="file-fact-value">{value}</span>
    </span>
  );
}

/** One list, or nothing at all when the file has none of that thing. */
function Section({
  title,
  children,
}: {
  title: string;
  children: ReactNode[];
}) {
  if (children.length === 0) {
    return null;
  }
  return (
    <section className="file-section">
      <h4 className="file-section-title">{title}</h4>
      <ul className="file-list">{children}</ul>
    </section>
  );
}

/**
 * One file named by a link, as a button when the page holds its view file.
 *
 * The identity comes from the generator, so the page opens the target without
 * resolving a path itself. An identity with no view file is left as text: the
 * status badge beside it already says why.
 */
function Target({
  viewer,
  identity,
  label,
}: {
  viewer: Viewer;
  identity: string | null;
  label: string;
}) {
  const path = identity === null ? null : viewPath(identity);
  if (path === null || !viewer.views.has(path)) {
    return <span className="file-target">{label}</span>;
  }
  return (
    <button
      type="button"
      className="file-target file-target-open"
      onClick={() => {
        viewer.openPanel(path);
      }}
    >
      {label}
    </button>
  );
}

/**
 * A click inside the rendered source, kept on the page.
 *
 * A relative link in the source would otherwise navigate the browser off the
 * viewer. The link's target is looked up among the links the generator already
 * scored, so this resolves nothing: a target the page can open opens as a
 * panel, an external one opens in its own tab, and anything else does nothing.
 */
function followLink(
  event: MouseEvent<HTMLDivElement>,
  viewer: Viewer,
  byTarget: ReadonlyMap<string, Link>,
): void {
  const anchor = (event.target as HTMLElement).closest("a");
  if (anchor === null) {
    return;
  }
  event.preventDefault();
  const link = byTarget.get(anchor.getAttribute("href") ?? "");
  if (link === undefined) {
    return;
  }
  if (link.status === "external") {
    window.open(link.target, "_blank", "noreferrer");
    return;
  }
  if (link.identity === null) {
    return;
  }
  const path = viewPath(link.identity);
  if (viewer.views.has(path)) {
    viewer.openPanel(path);
  }
}

/** The path the contract fixes for one file's markdown-file view. */
function viewPath(identity: string): string {
  return `markdown-file/${identity}.json`;
}
