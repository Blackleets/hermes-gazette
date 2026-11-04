(function () {
  "use strict";
  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { useState, useEffect } = React;
  const h = React.createElement;

  function Story(item) {
    return h("article", { className: "gazette-story", key: item.link },
      h("h4", null, h("a", { href: item.link, target: "_blank", rel: "noreferrer" }, item.title)),
      h("p", { className: "gazette-byline" }, item.source + " · " + (item.published || "").slice(0, 10)),
      item.summary ? h("p", null, item.summary) : null
    );
  }

  function GazettePage() {
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(function () {
      SDK.fetchJSON("/api/plugins/hermes-gazette/latest")
        .then(function (res) { setData(res.edition); })
        .catch(function (err) { setError("No edition yet — ask your agent: /gazette"); });
    }, []);

    if (error) return h("div", { className: "gazette-page" },
      h("h1", null, "📰 The Hermes Gazette"), h("p", null, error));
    if (!data) return h("div", { className: "gazette-page" }, h("p", null, "Loading the latest edition…"));

    const sections = Object.keys(data.sections || {}).map(function (name) {
      return h("section", { key: name },
        h("h3", { className: "gazette-section" }, name),
        h("div", { className: "gazette-grid" }, data.sections[name].map(Story))
      );
    });

    return h("div", { className: "gazette-page" },
      data.is_sample ? h("div", { className: "gazette-sample" }, "SAMPLE EDITION — DEMO DATA, NOT REAL NEWS") : null,
      h("header", { className: "gazette-masthead" },
        h("h1", null, "📰 " + data.title),
        h("p", null, data.subtitle + " — " + data.date + " · " + data.story_count + " stories")),
      sections,
      h("footer", { className: "gazette-foot" }, "Every story links to its source. No story prints without a verified date.")
    );
  }

  window.__HERMES_PLUGINS__.register("hermes-gazette", GazettePage);
})();
