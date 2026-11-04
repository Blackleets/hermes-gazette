// Hermes Gazette — Desktop plugin (Hermes Desktop Plugin SDK, @hermes/plugin-sdk).
// One ESM file, no build step. Adds a full Gazette page + sidebar entry to the
// native Hermes Desktop app. Data comes from the shared backend namespace
// (/api/plugins/hermes-gazette/) provided by dashboard/plugin_api.py — the
// same saved edition the dashboard tab and mobile delivery read.
//
// NOTE: this file is loaded uncompiled by Hermes Desktop, so UI is built
// with jsx() calls, never JSX syntax (per the Desktop Plugin SDK docs).

import { host, jsx, ROUTES_AREA, SIDEBAR_NAV_AREA } from '@hermes/plugin-sdk'
import { useEffect, useState } from 'react'

function GazettePage() {
  const [edition, setEdition] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    host
      .fetchJSON('/api/plugins/hermes-gazette/latest')
      .then((res) => { if (alive) setEdition(res.edition) })
      .catch(() => { if (alive) setError('No edition yet — ask your agent: /gazette') })
    return () => { alive = false }
  }, [])

  if (error) return jsx('div', { style: { padding: 24 } },
    jsx('h1', null, '📰 The Hermes Gazette'),
    jsx('p', null, error))
  if (!edition) return jsx('div', { style: { padding: 24 } },
    jsx('p', null, 'Loading the latest edition…'))

  const sections = Object.entries(edition.sections || {}).map(([name, items]) =>
    jsx('section', { key: name },
      jsx('h3', null, name),
      ...items.map((item) =>
        jsx('article', { key: item.link, style: { marginBottom: 16 } },
          jsx('h4', null, jsx('a', { href: item.link, target: '_blank', rel: 'noreferrer' }, item.title)),
          jsx('p', { style: { opacity: 0.65, fontSize: 12 } },
            `${item.source} · ${(item.published || '').slice(0, 10)}`),
          item.summary ? jsx('p', null, item.summary) : null))))

  return jsx('div', { style: { padding: 24, maxWidth: 880, margin: '0 auto', fontFamily: 'Georgia, serif' } },
    edition.is_sample
      ? jsx('div', { style: { background: '#8a1f1f', color: '#fff', padding: 8, textAlign: 'center' } },
          'SAMPLE EDITION — DEMO DATA, NOT REAL NEWS')
      : null,
    jsx('h1', { style: { textAlign: 'center' } }, `📰 ${edition.title}`),
    jsx('p', { style: { textAlign: 'center', opacity: 0.7 } },
      `${edition.subtitle} — ${edition.date} · ${edition.story_count} stories`),
    ...sections)
}

export default {
  id: 'hermes-gazette',
  name: 'Hermes Gazette',
  defaultEnabled: true,
  register(ctx) {
    ctx.register({
      id: 'gazette-page',
      area: ROUTES_AREA,
      title: 'Gazette',
      data: { path: '/gazette' },
      render: () => jsx(GazettePage, {}),
    })
    ctx.register({
      id: 'gazette-nav',
      area: SIDEBAR_NAV_AREA,
      title: 'Gazette',
      data: { path: '/gazette', label: 'Gazette', codicon: 'library' },
      render: () => null,
    })
  },
}
