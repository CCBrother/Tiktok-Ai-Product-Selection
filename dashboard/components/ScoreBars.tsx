type ScoreItem = {
  label: string;
  value: number;
};

export function ScoreBars({ items }: { items: ScoreItem[] }) {
  return (
    <div className="score-bars">
      {items.map((item) => (
        <div className="score-bar" key={item.label}>
          <div className="score-bar-top">
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </div>
          <div className="score-track">
            <div className="score-fill" style={{ width: `${Math.max(0, Math.min(100, item.value))}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
