import { type Dispatch, type FormEvent, type SetStateAction, useEffect, useMemo, useState } from 'react';
import { NavLink, Route, Routes, useLocation, useNavigate, useParams } from 'react-router-dom';

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

const navBase =
  'rounded-full border px-4 py-2 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500';
const navActive = 'border-transparent bg-accent text-white';
const navInactive = 'border-slate-300 bg-white text-ink hover:-translate-y-0.5';
const navDisabled = 'border-slate-200 bg-slate-100 text-slate-400 cursor-not-allowed';

interface InputPageProps {
  form: typeof defaultForm;
  setForm: Dispatch<SetStateAction<typeof defaultForm>>;
  loading: boolean;
  error: string;
  onSubmit: (event: FormEvent) => Promise<void>;
}

function InputPage({ form, setForm, loading, error, onSubmit }: InputPageProps) {
  return (
    <section className="grid gap-6">
      <div className="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-soft">
        <h2 className="text-xl">あなたの情報を入力</h2>
        <p className="mt-2 text-sm text-muted">必須：年齢、年収、世帯、職業 / 任意：扶養人数、市区町村</p>
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
            市区町村（任意）
            <select
              value={form.municipality}
              onChange={(event) => setForm({ ...form, municipality: event.target.value })}
              className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-base text-ink"
            >
              <option value="">選択してください</option>
              <option value="港区">港区</option>
            </select>
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
    </section>
  );
}

interface ListPageProps {
  results: Recommendation[];
  topReason: Array<Reason | null>;
  municipality: string;
  hasSearched: boolean;
}

function ListPage({ results, topReason, municipality, hasSearched }: ListPageProps) {
  const navigate = useNavigate();

  return (
    <section className="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-ink transition hover:-translate-y-0.5"
            onClick={() => navigate('/')}
          >
            戻る
          </button>
          <h2 className="text-xl">あなたに近い補助金一覧</h2>
        </div>
        {municipality && <span className="text-sm text-muted">対象市区町村： {municipality}</span>}
      </div>

      {!hasSearched && (
        <div className="mt-5 rounded-xl border border-dashed border-slate-300 p-6 text-sm text-muted">
          <p>まだ診断が完了していません。個人情報入力から診断を開始してください。</p>
          <button
            type="button"
            className="mt-4 rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white"
            onClick={() => navigate('/')}
          >
            個人情報入力へ
          </button>
        </div>
      )}

      {hasSearched && (
        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {results.length === 0 && (
            <div className="rounded-xl border border-dashed border-slate-300 p-6 text-sm text-muted">
              条件に近い補助金が見つかりませんでした。
            </div>
          )}
          {results.map((item, index) => (
            <button
              key={item.program_id}
              onClick={() => navigate(`/programs/${item.program_id}`)}
              className="rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-1 hover:shadow-soft"
            >
              <div
                className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${levelStyles[item.level]}`}
              >
                {levelLabel[item.level]}
              </div>
              <h3 className="mt-3 text-lg font-semibold">{item.program_name}</h3>
              <p className="mt-2 text-sm text-ink">{topReason[index]?.text ?? ''}</p>
              <p className="mt-3 text-xs text-muted">期限: {item.deadline?.date ?? '未設定'}</p>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

interface DetailPageProps {
  results: Recommendation[];
  hasSearched: boolean;
}

function DetailPage({ results, hasSearched }: DetailPageProps) {
  const navigate = useNavigate();
  const { programId } = useParams();
  const selected = useMemo(
    () => results.find((item) => item.program_id === programId) ?? null,
    [results, programId]
  );
  const [detail, setDetail] = useState<ProgramDetail | null>(null);
  const [detailStatus, setDetailStatus] = useState<'idle' | 'loading' | 'error'>('idle');

  useEffect(() => {
    if (!programId) return;

    const fetchDetail = async () => {
      setDetail(null);
      setDetailStatus('loading');
      try {
        const res = await fetch(`/api/programs/${programId}`);
        if (res.ok) {
          setDetail((await res.json()) as ProgramDetail);
          setDetailStatus('idle');
          return;
        }
        setDetailStatus('error');
      } catch (err) {
        console.error(err);
        setDetailStatus('error');
      }
    };

    fetchDetail();
  }, [programId]);

  const displayName = selected?.program_name ?? detail?.program_name ?? '補助金詳細';
  const deadlineText = selected?.deadline?.date ?? detail?.deadline ?? '未設定';
  const evidence = selected?.evidence ?? detail?.evidence ?? [];

  return (
    <section className="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-soft">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-ink transition hover:-translate-y-0.5"
          onClick={() => navigate('/programs')}
        >
          戻る
        </button>
        <h2 className="text-xl">補助金詳細</h2>
      </div>

      {!programId && (
        <div className="mt-5 rounded-xl border border-dashed border-slate-300 p-6 text-sm text-muted">
          <p>補助金が指定されていません。補助金一覧から選択してください。</p>
          <button
            type="button"
            className="mt-4 rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white"
            onClick={() => navigate('/programs')}
          >
            一覧へ戻る
          </button>
        </div>
      )}

      {programId && !selected && !detail && detailStatus !== 'loading' && (
        <div className="mt-5 rounded-xl border border-dashed border-slate-300 p-6 text-sm text-muted">
          <p>詳細を表示できませんでした。補助金一覧から選択し直してください。</p>
          <button
            type="button"
            className="mt-4 rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white"
            onClick={() => navigate('/programs')}
          >
            一覧へ戻る
          </button>
        </div>
      )}

      {programId && (selected || detail) && (
        <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <div>
            {selected && (
              <div
                className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${levelStyles[selected.level]}`}
              >
                {levelLabel[selected.level]}
              </div>
            )}
            <h3 className="mt-3 text-2xl">{displayName}</h3>
            {detail?.summary && <p className="mt-2 text-sm text-muted">{detail.summary}</p>}
            {detail?.eligibility?.notes && (
              <p className="mt-2 text-sm text-muted">
                <span className="font-semibold text-ink">備考:</span> {detail.eligibility.notes}
              </p>
            )}

            {selected && (
              <>
                <div className="mt-6">
                  <h4 className="font-semibold">理由</h4>
                  <ul className="mt-2 list-disc space-y-2 pl-5 text-sm text-muted">
                    {selected.reasons.map((reason, idx) => (
                      <li key={idx}>{reason.text}</li>
                    ))}
                  </ul>
                </div>

                <div className="mt-6">
                  <h4 className="font-semibold">最初にやること</h4>
                  <ul className="mt-2 list-disc space-y-2 pl-5 text-sm text-muted">
                    {selected.todo.map((item, idx) => (
                      <li key={idx}>{item.text}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}

            {!selected && hasSearched && (
              <p className="mt-6 text-sm text-amber-700">
                理由やTODOは補助金一覧から選んだ補助金で表示されます。
              </p>
            )}
          </div>

          <div>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <h4 className="font-semibold">期限</h4>
              <p className="mt-2 text-sm text-muted">{deadlineText}</p>
            </div>

            <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <h4 className="font-semibold">根拠</h4>
              <div className="mt-3 space-y-3 text-xs text-muted">
                {evidence.length === 0 && (
                  <p className="rounded-xl bg-white p-3 text-sm text-muted">根拠資料が未登録です。</p>
                )}
                {evidence.map((item, idx) => (
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

      {detailStatus === 'loading' && (
        <p className="mt-5 text-sm text-muted">詳細を読み込み中です...</p>
      )}

      {detailStatus === 'error' && (
        <p className="mt-5 text-sm text-rose-600">詳細の取得に失敗しました。</p>
      )}
    </section>
  );
}

export default function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState(defaultForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<Recommendation[]>([]);
  const [municipality, setMunicipality] = useState('');
  const [hasSearched, setHasSearched] = useState(false);

  const onSubmit = async (event: FormEvent) => {
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
      setHasSearched(true);
      navigate('/programs');
    } catch (err) {
      setError('診断に失敗しました。入力内容を確認してください。');
    } finally {
      setLoading(false);
    }
  };

  const topReason = useMemo(() => {
    return results.map((item) => item.reasons.find((r) => r.text) ?? null);
  }, [results]);

  const detailPath = useMemo(() => {
    if (location.pathname.startsWith('/programs/') && location.pathname.split('/')[2]) {
      return location.pathname;
    }
    return '';
  }, [location.pathname]);

  return (
    <div className="min-h-screen text-ink">
      <div className="pointer-events-none fixed -left-24 -top-24 h-72 w-72 rounded-full bg-[radial-gradient(circle_at_top,_#0f766e,_transparent_60%)] opacity-40 blur-md" />
      <div className="pointer-events-none fixed -bottom-32 right-0 h-80 w-80 rounded-full bg-[radial-gradient(circle_at_top,_#f59e0b,_transparent_60%)] opacity-40 blur-md" />

      <header className="relative z-10 px-[8vw] pt-12">
        <h1 className="text-3xl font-extrabold text-emerald-900 md:text-4xl">AI補助金ナビ</h1>
        <p className="mt-3 max-w-2xl text-base text-muted">
          <span className="font-bold text-ink">補助金受給の可能性を即座に判定し、AIが確かな根拠を提示します。</span>
        </p>
      </header>

      <nav className="relative z-10 mt-6 flex flex-wrap gap-3 px-[8vw]">
        <NavLink to="/" className={({ isActive }) => `${navBase} ${isActive ? navActive : navInactive}`}
        >
          個人情報入力
        </NavLink>
        <NavLink
          to="/programs"
          end
          className={({ isActive }) => `${navBase} ${isActive ? navActive : navInactive}`}
        >
          補助金一覧
        </NavLink>
        {detailPath ? (
          <NavLink
            to={detailPath}
            className={({ isActive }) => `${navBase} ${isActive ? navActive : navInactive}`}
          >
            補助金詳細
          </NavLink>
        ) : (
          <span className={`${navBase} ${navDisabled}`} aria-disabled="true">
            補助金詳細
          </span>
        )}
      </nav>

      <main className="relative z-10 px-[8vw] pb-16 pt-6">
        <Routes>
          <Route
            path="/"
            element={<InputPage form={form} setForm={setForm} loading={loading} error={error} onSubmit={onSubmit} />}
          />
          <Route
            path="/programs"
            element={
              <ListPage
                results={results}
                topReason={topReason}
                municipality={municipality}
                hasSearched={hasSearched}
              />
            }
          />
          <Route path="/programs/:programId" element={<DetailPage results={results} hasSearched={hasSearched} />} />
          <Route
            path="*"
            element={
              <section className="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-soft">
                <h2 className="text-xl">ページが見つかりません</h2>
                <p className="mt-2 text-sm text-muted">入力ページに戻って診断を開始してください。</p>
                <button
                  type="button"
                  className="mt-4 rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white"
                  onClick={() => navigate('/')}
                >
                  個人情報入力へ
                </button>
              </section>
            }
          />
        </Routes>
      </main>

      <footer className="px-[8vw] pb-10 text-xs text-muted">
        判定は入力情報に基づくルールベースです。根拠は登録済み資料の抜粋を表示しています。
      </footer>
    </div>
  );
}
