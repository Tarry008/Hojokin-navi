const views = {
  input: document.getElementById('view-input'),
  list: document.getElementById('view-list'),
  detail: document.getElementById('view-detail'),
};
const tabs = Array.from(document.querySelectorAll('.tab'));
const resultsEl = document.getElementById('results');
const detailEl = document.getElementById('detail');
const municipalityLabel = document.getElementById('municipality-label');

const state = {
  results: [],
  municipality: '',
  selected: null,
};

function showView(viewName) {
  Object.entries(views).forEach(([name, el]) => {
    el.classList.toggle('active', name === viewName);
  });
  tabs.forEach((tab) => {
    tab.classList.toggle('active', tab.dataset.view === viewName);
  });
}

tabs.forEach((tab) => {
  tab.addEventListener('click', () => showView(tab.dataset.view));
});

function badgeClass(level) {
  return level || 'unknown';
}

function renderResults() {
  resultsEl.innerHTML = '';
  if (!state.results.length) {
    resultsEl.innerHTML = '<p>条件に近い補助金が見つかりませんでした。</p>';
    return;
  }
  state.results.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.innerHTML = `
      <div class="badge ${badgeClass(item.level)}">${item.level}</div>
      <h3>${item.program_name}</h3>
      <p>信頼度: ${(item.confidence * 100).toFixed(0)}%</p>
      <p>${item.reasons[0]?.text || ''}</p>
      <p>期限: ${item.deadline?.date || '未設定'}</p>
    `;
    card.addEventListener('click', () => selectProgram(item.program_id));
    resultsEl.appendChild(card);
  });
}

async function selectProgram(programId) {
  const selected = state.results.find((item) => item.program_id === programId);
  let detail = null;
  try {
    const res = await fetch(`/api/programs/${programId}`);
    if (res.ok) detail = await res.json();
  } catch (err) {
    console.error(err);
  }

  detailEl.innerHTML = renderDetail(selected, detail);
  showView('detail');
}

function renderDetail(result, detail) {
  if (!result) return '<p>詳細情報がありません。</p>';
  const reasons = result.reasons
    .map((r) => `<li>${r.text}</li>`)
    .join('');
  const todo = result.todo
    .map((t) => `<li>${t.text}</li>`)
    .join('');
  const evidence = result.evidence
    .map((e) => `
      <div class="evidence">
        <p><strong>p.${e.page}</strong> ${e.snippet}</p>
        <p>${e.source_url}</p>
      </div>
    `)
    .join('');

  const summary = detail?.summary ? `<p>${detail.summary}</p>` : '';
  const notes = detail?.eligibility?.notes
    ? `<p><strong>備考:</strong> ${detail.eligibility.notes}</p>`
    : '';

  return `
    <div class="detail-grid">
      <div>
        <h2>${result.program_name}</h2>
        <div class="badge ${badgeClass(result.level)}">${result.level}</div>
        ${summary}
        ${notes}
        <div class="detail-section">
          <h3>理由</h3>
          <ul>${reasons}</ul>
        </div>
        <div class="detail-section">
          <h3>最初にやること</h3>
          <ul>${todo}</ul>
        </div>
      </div>
      <div>
        <div class="detail-section">
          <h3>期限</h3>
          <p>${result.deadline?.date || '未設定'}</p>
        </div>
        <div class="detail-section">
          <h3>根拠</h3>
          ${evidence}
        </div>
      </div>
    </div>
  `;
}

async function postJson(url, payload) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }
  return res.json();
}

const form = document.getElementById('profile-form');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = new FormData(form);
  const payload = {
    age: Number(data.get('age')),
    income_yen: Number(data.get('income_yen')),
    household: Number(data.get('household')),
    occupation: String(data.get('occupation') || ''),
  };

  const dependents = data.get('dependents');
  if (dependents !== null && dependents !== '') {
    payload.dependents = Number(dependents);
  }
  const municipality = data.get('municipality');
  if (municipality) payload.municipality = String(municipality);

  try {
    const response = await postJson('/api/recommendations', payload);
    state.results = response.results || [];
    state.municipality = response.municipality || '';
    municipalityLabel.textContent = state.municipality ? `対象自治体: ${state.municipality}` : '';
    renderResults();
    showView('list');
  } catch (err) {
    alert('診断に失敗しました。入力内容を確認してください。');
    console.error(err);
  }
});
