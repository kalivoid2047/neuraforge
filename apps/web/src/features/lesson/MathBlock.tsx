import katex from "katex";

/** Server-rendered KaTeX (ADR-0011: no client math JS on the critical path). */
export function MathBlock({
  tex,
  display = true,
}: {
  tex: string;
  display?: boolean;
}) {
  const html = katex.renderToString(tex, {
    displayMode: display,
    throwOnError: false,
    output: "htmlAndMathml", // MathML branch = screen-reader path (UIUX §10.5)
  });
  return (
    <span
      className={display ? "block" : "inline"}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
