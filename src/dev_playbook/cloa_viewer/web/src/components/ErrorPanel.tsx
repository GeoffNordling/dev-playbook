// Failure on screen. A view file that failed its schema, a kind with no
// renderer, and a generator that failed all land here: the thing that broke,
// named, in the place the working panel would have been.

export interface ErrorPanelProps {
  /** What failed: a view file's path, or the record that carries the error. */
  path: string;
  error: string;
}

export function ErrorPanel({ path, error }: ErrorPanelProps) {
  return (
    <div className="error">
      <h3 className="error-path">{path}</h3>
      <pre className="error-text">{error}</pre>
    </div>
  );
}
