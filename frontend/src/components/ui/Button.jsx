export function Button({
  variant = 'primary',
  block = false,
  loading = false,
  disabled = false,
  className,
  children,
  ...rest
}) {
  const cls = ['btn', `btn--${variant}`, block && 'btn--block', className].filter(Boolean).join(' ')
  return (
    <button {...rest} className={cls} disabled={disabled || loading} aria-busy={loading || undefined}>
      {loading && <span className="btn__spinner" aria-hidden="true" />}
      <span>{children}</span>
    </button>
  )
}
