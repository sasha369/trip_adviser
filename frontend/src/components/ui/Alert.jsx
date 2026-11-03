export function Alert({ kind = 'error', title, children }) {
  return (
    <div
      className={`alert alert--${kind}`}
      role={kind === 'error' ? 'alert' : 'status'}
      {...(kind === 'error' ? { 'aria-live': 'assertive' } : { 'aria-live': 'polite' })}
    >
      <span className="alert__icon" aria-hidden="true">
        {kind === 'error' ? '⚠' : '✓'}
      </span>
      <div>
        {title && <p className="t-label">{title}</p>}
        {children && <p className="t-meta">{children}</p>}
      </div>
    </div>
  )
}
