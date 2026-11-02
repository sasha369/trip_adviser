export function TextField({ id, label, error, hint, className, ...rest }) {
  return (
    <div className={['field', error && 'field--invalid', className].filter(Boolean).join(' ')}>
      <label className="field__label" htmlFor={id}>
        {label}
      </label>
      <input id={id} className="field__input" aria-invalid={error ? 'true' : undefined} {...rest} />
      {error && (
        <p id={`${id}-error`} className="field__error t-meta" role="alert">
          {error}
        </p>
      )}
      {hint && !error && <p className="t-meta">{hint}</p>}
    </div>
  )
}
