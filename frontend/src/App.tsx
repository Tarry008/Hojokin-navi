import { useMemo, useState } from 'react';

type Level = 'high' | 'medium' | 'low' | 'unknown';

interface Evidence {
  page: number;
  source_url: string;
  snippet: string;
}

interface Reason {
  text: string;
  evidence_ref: number;
}

interface TodoItem {
  text: string;
  evidence_ref: number;
}

interface Deadline {
  date: string | null;
  evidence_ref: number | null;
}

interface Recommendation {
  program_id: string;
  program_name: string;
  level: Level;
  confidence: number;
  reasons: Reason[];
  deadline: Deadline;
  todo: TodoItem[];
  evidence: Evidence[];
}

interface RecommendationResponse {
  municipality: string;
  results: Recommendation[];
  meta: { model: string; version: string };
}

interface ProgramDetail {
  program_id: string;
  program_name: string;
  municipality: string;
  summary: string;
  eligibility?: {
    notes?: string;
  };
  deadline?: string | null;
  todo_steps?: string[];
  gray_zone_guidance?: string[];
  evidence?: Evidence[];
}

const levelStyles: Record<Level, string> = {
  high: 'bg-emerald-100 text-emerald-800',
  medium: 'bg-amber-100 text-amber-800',
  low: 'bg-rose-100 text-rose-800',
  unknown: 'bg-slate-200 text-slate-700',
};

const levelLabel: Record<Level, string> = {
  high: 'High',
  medium: 'Medium',
  low: 'Low',
  unknown: 'Unknown',
};

const defaultForm = {
  age: 25,
  income_yen: 3200000,
  household: 2,
  occupation: '',
  dependents: '',
  municipality: '',
};

type View = 'input' | 'list' | 'detail';

async function postJson<T>(url: string, payload: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Request failed');
  }
  return res.json() as Promise<T>;
}

export default function App() {
  const [view, setView] = useState<View>('input');
  const [form, setForm] = useState(defaultForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<Recommendation[]>([]);
  const [municipality, setMunicipality] = useState('');
  const [selected, setSelected] = useState<Recommendation | null>(null);
  const [detail, setDetail] = useState<ProgramDetail | null>(null);

  const showDetail = async (program: Recommendation) => {
    setSelected(program);
    setView('detail');
    setDetail(null);
    try {
      const res = await fetch(`/api/programs/${program.program_id}`);
      if (res.ok) {
        setDetail((await res.json()) as ProgramDetail);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload: Record<string, unknown> = {
        age: Number(form.age),
        income_yen: Number(form.income_yen),
        household: Number(form.household),
        occupation: String(form.occupation || ''),
      };
      if (form.dependents !== '') payload.dependents = Number(form.dependents);
      if (form.municipality) payload.municipality = String(form.municipality);

      const response = await postJson<RecommendationResponse>('/api/recommendations', payload);
      setResults(response.results || []);
      setMunicipality(response.municipality || '');
      setView('list');
    } catch (err) {
      setError('診断に失敗しました。入力内容を確認してください。');
    } finally {
      setLoading(false);
    }
  };

  const topReason = useMemo(() => {
    return results.map((item) => item.reasons.find((r) => r.text) ?? null);
  }, [results]);

  return (
    <div className="min-h-screen text-ink">
      <div className="pointer-events-none fixed -left-24 -top-24 h-72 w-72 rounded-full bg-[radial-gradient(circle_at_top,_#0f766e,_transparent_60%)] opacity-40 blur-md" />
      <div className="pointer-events-none fixed -bottom-32 right-0 h-80 w-80 rounded-full bg-[radial-gradient(circle_at_top,_#f59e0b,_transparent_60%)] opacity-40 blur-md" />

      <header className="relative z-10 px-[8vw] pt-12">
        <p className="text-xs uppercase tracking-[0.3em] text-muted">RAG × Google Cloud</p>
        <h1 className="font-serif text-3xl md:text-4xl">自治体給付金・補助金 判定AI</h1>
        <p className="mt-3 max-w-2xl text-base text-muted">
          対象/対象外の断定ではなく、<span className="font-semibold text-accent">対象になるための道筋</span>まで提示します。
        </p>
        <div className="mt-6 inline-flex items-baseline gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4 shadow-soft">
          <span className="text-3xl font-bold text-accent2">70%</span>
          <span className="text-sm text-muted">の経営者が「どの補助金を使えばいいか不明」と回答</span>
        </div>
      </header>

      <nav className="relative z-10 mt-6 flex flex-wrap gap-3 px-[8vw]">
        {[
          { key: 'input', label: '個人情報入力' },
          { key: 'list', label: '補助金一覧' },
          { key: 'detail', label: '補助金詳細' },
        ].map((tab) => (
          <button
            key={tab.key}
            className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
              view === tab.key ? 'border-transparent bg-accent text-white' : 'border-slate-300 bg-white text-ink'
            }`}
            onClick={() => setView(tab.key as View)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="relative z-10 px-[8vw] pb-16 pt-6">
        {view === 'input' && (
          <section className="grid gap-6">
            <div className="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-soft">
              <h2 className="font-serif text-xl">あなたの情報を入力</h2>
              <p className="mt-2 text-sm text-muted">必須：年齢、年収、世帯、職業 / 任意：扶養人数</p>
              <form className="mt-5 grid gap-4 md:grid-cols-2" onSubmit={onSubmit}>
                <label className="flex flex-col gap-2 text-sm text-muted">
                  年齢
                  <input
                    type="number"
                    min={15}
                    max={100}
                    required
                    value={form.age}
                    onChange={(event) => setForm({ ...form, age: Number(event.target.value) })}
                    className="rounded-xl border border-slate-200 px-3 py-2 text-base text-ink"
                  />
                </label>
                <label className="flex flex-col gap-2 text-sm text-muted">
                  年収（円）
                  <input
                    type="number"
                    min={0}
                    step={10000}
                    required
                    value={form.income_yen}
                    onChange={(event) => setForm({ ...form, income_yen: Number(event.target.value) })}
                    className="rounded-xl border border-slate-200 px-3 py-2 text-base text-ink"
                  />
                </label>
                <label className="flex flex-col gap-2 text-sm text-muted">
                  世帯人数
                  <input
                    type="number"
                    min={1}
                    max={10}
                    required
                    value={form.household}
                    onChange={(event) => setForm({ ...form, household: Number(event.target.value) })}
                    className="rounded-xl border border-slate-200 px-3 py-2 text-base text-ink"
                  />
                </label>
                <label className="flex flex-col gap-2 text-sm text-muted">
                  職業
                  <input
                    type="text"
                    required
                    placeholder="例: 会社員 / 経営者"
                    value={form.occupation}
                    onChange={(event) => setForm({ ...form, occupation: event.target.value })}
                    className="rounded-xl border border-slate-200 px-3 py-2 text-base text-ink"
                  />
                </label>
                <label className="flex flex-col gap-2 text-sm text-muted">
                  扶養人数（任意）
                  <input
                    type="number"
                    min={0}
                    max={10}
                    value={form.dependents}
                    onChange={(event) => setForm({ ...form, dependents: event.target.value })}
                    className="rounded-xl border border-slate-200 px-3 py-2 text-base text-ink"
                  />
                </label>
                <label className="flex flex-col gap-2 text-sm text-muted">
                  自治体（任意）
                  <input
                    type="text"
                    placeholder="例: ○○市"
                    value={form.municipality}
                    onChange={(event) => setForm({ ...form, municipality: event.target.value })}
                    className="rounded-xl border border-slate-200 px-3 py-2 text-base text-ink"
                  />
                </label>
                <button
                  type="submit"
                  className="col-span-full mt-2 rounded-xl bg-accent px-5 py-3 text-base font-semibold text-white transition hover:-translate-y-0.5"
                  disabled={loading}
                >
                  {loading ? '診断中...' : '診断を開始'}
                </button>
                {error && <p className="col-span-full text-sm text-rose-600">{error}</p>}
              </form>
            </div>

            <div className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-6">
              <h3 className="font-serif text-lg">グレーゾーンへの案内</h3>
              <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-muted">
                <li>対象外と判断されても「どうすれば対象になるか」を優先的に提示します。</li>
                <li>期限・必要書類・最初のTODOをセットで提示します。</li>
              </ul>
            </div>
          </section>
        )}

        {view === 'list' && (
          <section className="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-soft">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="font-serif text-xl">あなたに近い補助金一覧</h2>
              {municipality && <span className="text-sm text-muted">対象自治体: {municipality}</span>}
            </div>
            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {results.length === 0 && (
                <div className="rounded-xl border border-dashed border-slate-300 p-6 text-sm text-muted">
                  条件に近い補助金が見つかりませんでした。
                </div>
              )}
              {results.map((item, index) => (
                <button
                  key={item.program_id}
                  onClick={() => showDetail(item)}
                  className="rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-1 hover:shadow-soft"
                >
                  <div className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${levelStyles[item.level]}`}>
                    {levelLabel[item.level]}
                  </div>
                  <h3 className="mt-3 text-lg font-semibold">{item.program_name}</h3>
                  <p className="mt-2 text-sm text-muted">信頼度: {(item.confidence * 100).toFixed(0)}%</p>
                  <p className="mt-2 text-sm text-ink">{topReason[index]?.text ?? ''}</p>
                  <p className="mt-3 text-xs text-muted">期限: {item.deadline?.date ?? '未設定'}</p>
                </button>
              ))}
            </div>
          </section>
        )}

        {view === 'detail' && (
          <section className="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-soft">
            {!selected && <p className="text-sm text-muted">補助金を選択してください。</p>}
            {selected && (
              <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
                <div>
                  <div className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${levelStyles[selected.level]}`}>
                    {levelLabel[selected.level]}
                  </div>
                  <h2 className="mt-3 font-serif text-2xl">{selected.program_name}</h2>
                  {detail?.summary && <p className="mt-2 text-sm text-muted">{detail.summary}</p>}
                  {detail?.eligibility?.notes && (
                    <p className="mt-2 text-sm text-muted">
                      <span className="font-semibold text-ink">備考:</span> {detail.eligibility.notes}
                    </p>
                  )}

                  <div className="mt-6">
                    <h3 className="font-semibold">理由</h3>
                    <ul className="mt-2 list-disc space-y-2 pl-5 text-sm text-muted">
                      {selected.reasons.map((reason, idx) => (
                        <li key={idx}>{reason.text}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="mt-6">
                    <h3 className="font-semibold">最初にやること</h3>
                    <ul className="mt-2 list-disc space-y-2 pl-5 text-sm text-muted">
                      {selected.todo.map((item, idx) => (
                        <li key={idx}>{item.text}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div>
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <h3 className="font-semibold">期限</h3>
                    <p className="mt-2 text-sm text-muted">{selected.deadline?.date ?? '未設定'}</p>
                  </div>

                  <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <h3 className="font-semibold">根拠</h3>
                    <div className="mt-3 space-y-3 text-xs text-muted">
                      {selected.evidence.map((item, idx) => (
                        <div key={idx} className="rounded-xl bg-white p-3">
                          <p className="font-semibold text-ink">p.{item.page}</p>
                          <p className="mt-1">{item.snippet}</p>
                          <p className="mt-1 break-all">{item.source_url}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </section>
        )}
      </main>

      <footer className="px-[8vw] pb-10 text-xs text-muted">
        データ保管: Cloud Storage / メタデータ: Firestore / 推論: Vertex AI (オプション)
      </footer>
    </div>
  );
}
