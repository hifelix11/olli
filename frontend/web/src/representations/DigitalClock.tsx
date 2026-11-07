/** Digitaluhr, zwölf Stunden: 3:30, 11:00. */
export function DigitalClock({ hour, minute }: { hour: number; minute: number }) {
  return (
    <div className="picture digital-clock" role="img" aria-label="Digitaluhr">
      {hour}:{String(minute).padStart(2, "0")}
    </div>
  );
}
