import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const LOGIN = process.env.GITHUB_LOGIN || 'BlackFeather-git';
const TOKEN = process.env.GITHUB_TOKEN;
const OUT_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'assets');
const EXCLUDED_LANGS = new Set(
  (process.env.EXCLUDE_LANGS || '').split(',').map((s) => s.trim().toLowerCase()).filter(Boolean),
);
const MAX_LANGS = 6;

const theme = {
  bg: '#0a0c10',
  bar: '#12161f',
  border: '#242b35',
  text: '#e6edf3',
  muted: '#7d8590',
  faint: '#30363d',
  blue: '#38bdf8',
  green: '#22c55e',
  orange: '#f97316',
  pink: '#ec4899',
  purple: '#a855f7',
};
const FONT = `ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace`;

if (!TOKEN) {
  console.error('GITHUB_TOKEN is not set');
  process.exit(1);
}

const QUERY = `
query ($login: String!, $after: String) {
  user(login: $login) {
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount } }
      }
    }
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first: 10, orderBy: { field: SIZE, direction: DESC }) {
          edges { size node { name color } }
        }
      }
    }
  }
}`;

async function graphql(variables) {
  const res = await fetch('https://api.github.com/graphql', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      'Content-Type': 'application/json',
      'User-Agent': `${LOGIN}-profile-stats`,
    },
    body: JSON.stringify({ query: QUERY, variables }),
  });
  if (!res.ok) throw new Error(`GitHub API responded ${res.status}: ${await res.text()}`);
  const body = await res.json();
  if (body.errors?.length) throw new Error(body.errors.map((e) => e.message).join('; '));
  if (!body.data?.user) throw new Error(`User "${LOGIN}" not found`);
  return body.data.user;
}

async function collect() {
  let after = null;
  let user;
  let stars = 0;
  const langs = new Map();

  do {
    user = await graphql({ login: LOGIN, after });
    for (const repo of user.repositories.nodes) {
      stars += repo.stargazerCount;
      for (const { size, node } of repo.languages.edges) {
        if (EXCLUDED_LANGS.has(node.name.toLowerCase())) continue;
        const entry = langs.get(node.name) || { name: node.name, color: node.color || theme.muted, size: 0 };
        entry.size += size;
        langs.set(node.name, entry);
      }
    }
    after = user.repositories.pageInfo.endCursor;
  } while (user.repositories.pageInfo.hasNextPage);

  const contributions = user.contributionsCollection;
  return {
    stars,
    commits: contributions.totalCommitContributions + contributions.restrictedContributionsCount,
    pullRequests: user.pullRequests.totalCount,
    issues: user.issues.totalCount,
    repos: user.repositories.totalCount,
    followers: user.followers.totalCount,
    yearTotal: contributions.contributionCalendar.totalContributions,
    weeks: contributions.contributionCalendar.weeks.map((w) =>
      w.contributionDays.reduce((sum, d) => sum + d.contributionCount, 0),
    ),
    languages: [...langs.values()].sort((a, b) => b.size - a.size),
  };
}

const esc = (s) =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const compact = (n) =>
  n >= 10000 ? `${Math.round(n / 1000)}k` : n >= 1000 ? `${(n / 1000).toFixed(1).replace(/\.0$/, '')}k` : String(n);

function card({ width, height, command, label, body }) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(label)}">
  <title>${esc(label)}</title>
  <style>
    text { font-family: ${FONT}; font-size: 13px; }
    .muted { fill: ${theme.muted}; }
    .text { fill: ${theme.text}; }
    .small { font-size: 11px; }
  </style>
  <clipPath id="frame"><rect width="${width}" height="${height}" rx="10"/></clipPath>
  <g clip-path="url(#frame)">
    <rect width="${width}" height="${height}" fill="${theme.bg}"/>
    <rect width="${width}" height="36" fill="${theme.bar}"/>
    <circle cx="18" cy="18" r="5" fill="#ef4444"/>
    <circle cx="34" cy="18" r="5" fill="#eab308"/>
    <circle cx="50" cy="18" r="5" fill="#22c55e"/>
    <text x="68" y="22" class="muted small">${esc(command)}</text>
${body}
  </g>
  <rect width="${width}" height="${height}" rx="10" fill="none" stroke="${theme.border}" stroke-width="1"/>
</svg>`;
}

function statsCard(data) {
  const width = 410;
  const rows = [
    ['stars', data.stars],
    ['commits', data.commits],
    ['pull requests', data.pullRequests],
    ['issues', data.issues],
    ['repositories', data.repos],
    ['followers', data.followers],
  ];
  const rowHeight = 25;
  const top = 62;
  const height = top + (rows.length - 1) * rowHeight + 24;
  const body = rows
    .map(([name, value], i) => {
      const y = top + i * rowHeight;
      const valueText = compact(value);
      const from = 20 + name.length * 7.8 + 10;
      const to = width - 20 - valueText.length * 7.8 - 10;
      return `  <text x="20" y="${y}" class="muted">${esc(name)}</text>
  <line x1="${from.toFixed(1)}" y1="${y - 4}" x2="${to.toFixed(1)}" y2="${y - 4}" stroke="${theme.faint}" stroke-dasharray="1 5" stroke-linecap="round"/>
  <text x="${width - 20}" y="${y}" class="text" text-anchor="end" font-weight="600">${valueText}</text>`;
    })
    .join('\n');
  return card({ width, height, command: `gh stats --user ${LOGIN}`, label: `GitHub stats for ${LOGIN}`, body });
}

function languagesCard(data, height) {
  const width = 410;
  const total = data.languages.reduce((sum, l) => sum + l.size, 0);

  if (total === 0) {
    const body = `  <text x="20" y="70" class="muted">No public language data yet.</text>`;
    return card({ width, height, command: 'ls ./languages --sort=size', label: `Most used languages for ${LOGIN}`, body });
  }

  const top = data.languages.slice(0, MAX_LANGS);
  const rest = data.languages.slice(MAX_LANGS).reduce((sum, l) => sum + l.size, 0);
  const slices = rest > 0 ? [...top, { name: 'Other', color: theme.muted, size: rest }] : top;

  const barX = 20;
  const barY = 54;
  const barWidth = width - 40;
  const gap = 2;
  let x = barX;
  const segments = slices
    .map((l) => {
      const w = Math.max((l.size / total) * barWidth - gap, 1);
      const rect = `    <rect x="${x.toFixed(1)}" y="${barY}" width="${w.toFixed(1)}" height="8" fill="${l.color}"/>`;
      x += w + gap;
      return rect;
    })
    .join('\n');

  const colWidth = barWidth / 2;
  const legend = slices
    .map((l, i) => {
      const lx = barX + (i % 2) * colWidth;
      const ly = 94 + Math.floor(i / 2) * rowGap(slices.length, height);
      const pct = ((l.size / total) * 100).toFixed(1);
      return `  <circle cx="${lx + 5}" cy="${ly - 4.5}" r="5" fill="${l.color}"/>
  <text x="${lx + 18}" y="${ly}" class="text">${esc(l.name)}</text>
  <text x="${lx + colWidth - 16}" y="${ly}" class="muted" text-anchor="end">${pct}%</text>`;
    })
    .join('\n');

  const body = `  <clipPath id="bar"><rect x="${barX}" y="${barY}" width="${barWidth}" height="8" rx="4"/></clipPath>
  <g clip-path="url(#bar)">
${segments}
  </g>
${legend}`;
  return card({ width, height, command: 'ls ./languages --sort=size', label: `Most used languages for ${LOGIN}`, body });
}

function rowGap(count, height) {
  const rows = Math.ceil(count / 2);
  return rows > 1 ? Math.min((height - 94 - 22) / (rows - 1), 30) : 0;
}

function activityCard(data) {
  const width = 840;
  const height = 168;
  const weeks = data.weeks.slice(-53);
  const max = Math.max(...weeks, 1);
  const chartX = 20;
  const chartBottom = 140;
  const chartHeight = 72;
  const step = (width - 40) / weeks.length;
  const barWidth = Math.max(step - 4, 2);

  const bars = weeks
    .map((count, i) => {
      const h = count === 0 ? 2 : Math.max((count / max) * chartHeight, 4);
      const x = chartX + i * step + (step - barWidth) / 2;
      const fill = count === 0 ? theme.faint : theme.blue;
      return `  <rect x="${x.toFixed(1)}" y="${(chartBottom - h).toFixed(1)}" width="${barWidth.toFixed(1)}" height="${h.toFixed(1)}" rx="2" fill="${fill}"><title>${count} contributions</title></rect>`;
    })
    .join('\n');

  const body = `  <text x="${width - 20}" y="21.5" class="small" text-anchor="end"><tspan class="text" font-weight="600">${data.yearTotal.toLocaleString('en-US')}</tspan><tspan class="muted"> contributions in the past year</tspan></text>
${bars}
  <rect x="${chartX}" y="${chartBottom + 4}" width="${width - 40}" height="1" fill="${theme.border}"/>
  <text x="${chartX}" y="${chartBottom + 19}" class="muted small">52 weeks ago</text>
  <text x="${width - 20}" y="${chartBottom + 19}" class="muted small" text-anchor="end">this week</text>`;
  return card({
    width,
    height,
    command: 'git log --since="1 year ago" | weekly',
    label: `${data.yearTotal} contributions by ${LOGIN} in the past year`,
    body,
  });
}

const data = await collect();
const stats = statsCard(data);
const statsHeight = Number(stats.match(/height="(\d+)"/)[1]);

await mkdir(OUT_DIR, { recursive: true });
await writeFile(join(OUT_DIR, 'stats.svg'), stats);
await writeFile(join(OUT_DIR, 'languages.svg'), languagesCard(data, statsHeight));
await writeFile(join(OUT_DIR, 'activity.svg'), activityCard(data));

console.log(
  `Wrote stats for ${LOGIN}: ${data.stars} stars, ${data.commits} commits, ${data.repos} repos, ${data.languages.length} languages`,
);
