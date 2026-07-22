import * as React from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";

const styles: Record<Variant, string> = {
  primary:
    "bg-brand text-white hover:bg-brand/90 active:bg-brand/80 shadow-sm",
  secondary:
    "bg-raised text-ink border border-line hover:border-brand/60 hover:text-ink",
  ghost: "text-ink-2 hover:text-ink hover:bg-raised",
  danger: "bg-danger/10 text-danger border border-danger/30 hover:bg-danger/20",
};

export function Button({
  variant = "primary",
  size = "md",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: "sm" | "md" | "lg";
}) {
  const sizes = {
    sm: "h-8 px-3 text-sm rounded-lg",
    md: "h-10 px-4 text-sm rounded-xl",
    lg: "h-12 px-6 text-base rounded-xl",
  };
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 font-medium transition-colors duration-150 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand disabled:opacity-50 disabled:pointer-events-none ${sizes[size]} ${styles[variant]} ${className}`}
      {...props}
    />
  );
}
