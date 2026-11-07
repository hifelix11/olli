type Props = { title: string; categories: string; values: string };

/** Dieselben Daten wie das Säulendiagramm, als Tabelle. */
export function Table({ title, categories, values }: Props) {
  const cats = categories.split(" ").filter(Boolean);
  const vals = values.split(" ").filter(Boolean);
  return (
    <table className="picture data-table" aria-label={`Tabelle: ${title}`}>
      <caption>{title}</caption>
      <tbody>
        {cats.map((cat, i) => (
          <tr key={cat}>
            <th scope="row">{cat}</th>
            <td>{vals[i]}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
