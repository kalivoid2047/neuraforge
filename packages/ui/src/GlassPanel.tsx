import * as React from "react";

export function GlassPanel({
  className = "",
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`rounded-[20px] border border-white/10 bg-glass backdrop-blur-2xl ${className}`}
      {...props}
    />
  );
}
