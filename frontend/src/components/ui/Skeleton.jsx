export function Skeleton({ style, className }) {
  return <div className={['skeleton', className].filter(Boolean).join(' ')} style={style} aria-hidden="true" />
}

export function SkeletonText({ lines = 1 }) {
  return (
    <span aria-hidden="true">
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton key={i} style={{ display: 'block', height: 14, width: `${90 - i * 12}%`, marginBottom: 8 }} />
      ))}
    </span>
  )
}
