# Maintaining the homepage

The site still builds with Jekyll and GitHub Pages. The responsive layout uses plain CSS and a small JavaScript file; it does not need a Node build step.

## Content

- `_pages/about.md`: biography, news, awards, talks, and section order. Keep the existing section IDs so incoming links continue to work.
- `_data/publications.yml`: publication titles, authors, venue, citation IDs, and working paper/project links. Entries are displayed in file order, newest first. Keep unknown links absent instead of adding an empty URL.
- `_data/experience.yml`: education, employment, and internships, including dates and logos.
- `_config.yml`: affiliation, contact details, canonical URL, and search description.
- `_data/navigation.yml`: section labels and navigation links.

Older news is inside a native `details` element. It remains readable without JavaScript.

## Images

Each paper has 480px and 960px WebP previews. `srcset` lets the browser choose a size, and below-the-fold images load lazily. The thumbnail links to the unchanged original figure for detailed reading.

After adding a paper's original image and its output paths to the publication data, regenerate previews:

```sh
python -m pip install Pillow PyYAML
python scripts/optimize_images.py
```

Keep `image_width` and `image_height` equal to the original image dimensions. Logo sources are recorded in `docs/logo-sources.md`.

## Layout and behavior

- `_sass/_homepage.scss`: typography, main grid, navigation, profile, publications, experience rows, keyboard focus, reduced motion, and print styles.
- `_sass/_visitor-map.scss`: compact visitor-map layout, with totals beside the heading. At 768px and above, the map and compact country list share a row; on smaller screens, the countries form a two-column list below the map. The map panel stretches to match the ranking panel so a tall sidebar cannot leave an unused gap below it.
- `assets/js/site.js`: menu state, Escape/outside-click dismissal, and the current-section indicator. No JavaScript is required to reach the navigation links.
- Citation and visitor-data includes use `fetch`, timeouts, and fallback URLs. Localhost previews do not send GoatCounter pageviews.
- `assets/js/metrics.js`: GitHub star/fork counts and Bilibili video views, displayed as native text with small inline SVG icons. Public Shields JSON endpoints provide the data; no badge images, tokens, or icon library are loaded. Successful counts are cached in the browser for six hours, duplicate repository requests are shared, and requests time out after ten seconds. A failed refresh keeps the last successful count with its retrieval time in the link tooltip; without a saved count, the link shows an unavailable message rather than zero.
- Publication links pointing to `https://github.com/owner/repo` automatically get star/fork links. The video link in `_pages/about.md` uses `video-link.html` with a Bilibili `bvid`.

The count styling draws on [Primer's CounterLabel](https://primer.style/product/components/counter-label/) and [icon accessibility guidance](https://primer.style/octicons/usage-guidelines/): use a small icon beside a readable text label, and hide decorative SVGs from screen readers. The simple SVG paths are local; no external icon assets are required. [Shields dynamic JSON documentation](https://shields.io/badges/dynamic-json-badge) describes the video count's JSONPath query.

The main layout changes at 1024px; paper cards stack below 704px; compact profile spacing applies below 480px. Content is limited to a 1200px container on large monitors. Short desktop windows allow the profile to scroll normally.

## Preview and verification

With the repository's Ruby dependencies installed:

```sh
bundle exec jekyll build
bundle exec jekyll serve
```

Check narrow phones (320–430px), tablet widths (768–1024px), desktops (1280–1920px), and an ultrawide viewport. Confirm that there is no horizontal page scrolling, figures stay inside their cards, the mobile menu works with the keyboard, and anchor headings appear below the sticky navigation. Check browser zoom, reduced motion, and printing as well.

Older theme files and the previous JavaScript bundle remain in the repository for reference, but the homepage no longer loads them.
