const examples = [
  {
    id: "hw2-student31-q4-2-2",
    homework: 2,
    student: 31,
    questionId: "4.2-2",
    image: "./assets/examples/hw2_student31_q4_2-2.png",
    rawMarkdown: "./assets/examples/hw2_student31_q4_2-2_raw.md",
    rectifiedMarkdown: "./assets/examples/hw2_student31_q4_2-2.md"
  },
  {
    id: "hw4-student4-q6-4-4",
    homework: 4,
    student: 4,
    questionId: "6.4-4",
    image: "./assets/examples/hw4_student4_q6_4-4.png",
    rawMarkdown: "./assets/examples/hw4_student4_q6_4-4_raw.md",
    rectifiedMarkdown: "./assets/examples/hw4_student4_q6_4-4.md"
  },
  {
    id: "hw5-student42-q7-5-4",
    homework: 5,
    student: 42,
    questionId: "7.5-4",
    image: "./assets/examples/hw5_student42_q7_5-4.png",
    rawMarkdown: "./assets/examples/hw5_student42_q7_5-4_raw.md",
    rectifiedMarkdown: "./assets/examples/hw5_student42_q7_5-4.md"
  }
];

const selectEl = document.querySelector("#example-select");
const pillsEl = document.querySelector("#homework-pills");
const metaEl = document.querySelector("#example-meta");
const imageEl = document.querySelector("#example-image");
const transcriptEl = document.querySelector("#transcript-body");
const transcriptTitleEl = document.querySelector("#transcript-title");
const transcriptNoteEl = document.querySelector("#transcript-note");
const toggleButtons = document.querySelectorAll("[data-transcript-mode]");
const navLinks = document.querySelectorAll("[data-nav-link]");
const navSections = document.querySelectorAll("[data-nav-section]");

const transcriptCache = new Map();
const transcriptState = {
  mode: new URL(window.location.href).searchParams.get("view") === "rectified" ? "rectified" : "raw",
  currentExampleId: null
};

let loadSequence = 0;

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatInline(text) {
  return escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

function cleanMarkdownLines(markdown) {
  return markdown
    .replace(/\r/g, "")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("![Source Image]"));
}

function computeChangedIndices(sourceItems, targetItems) {
  const sourceLength = sourceItems.length;
  const targetLength = targetItems.length;
  const dp = Array.from({ length: sourceLength + 1 }, () => Array(targetLength + 1).fill(0));

  for (let sourceIndex = sourceLength - 1; sourceIndex >= 0; sourceIndex -= 1) {
    for (let targetIndex = targetLength - 1; targetIndex >= 0; targetIndex -= 1) {
      if (sourceItems[sourceIndex] === targetItems[targetIndex]) {
        dp[sourceIndex][targetIndex] = dp[sourceIndex + 1][targetIndex + 1] + 1;
      } else {
        dp[sourceIndex][targetIndex] = Math.max(
          dp[sourceIndex + 1][targetIndex],
          dp[sourceIndex][targetIndex + 1]
        );
      }
    }
  }

  const changedIndices = new Set();
  let sourceIndex = 0;
  let targetIndex = 0;

  while (sourceIndex < sourceLength && targetIndex < targetLength) {
    if (sourceItems[sourceIndex] === targetItems[targetIndex]) {
      sourceIndex += 1;
      targetIndex += 1;
      continue;
    }

    if (dp[sourceIndex + 1][targetIndex] >= dp[sourceIndex][targetIndex + 1]) {
      changedIndices.add(sourceIndex);
      sourceIndex += 1;
    } else {
      targetIndex += 1;
    }
  }

  while (sourceIndex < sourceLength) {
    changedIndices.add(sourceIndex);
    sourceIndex += 1;
  }

  return changedIndices;
}

function buildLineComparisons(sourceLines, targetLines) {
  const comparisons = sourceLines.map(() => ({ changed: false, targetLine: null }));
  const sourceLength = sourceLines.length;
  const targetLength = targetLines.length;
  const dp = Array.from({ length: sourceLength + 1 }, () => Array(targetLength + 1).fill(0));

  for (let sourceIndex = sourceLength - 1; sourceIndex >= 0; sourceIndex -= 1) {
    for (let targetIndex = targetLength - 1; targetIndex >= 0; targetIndex -= 1) {
      if (sourceLines[sourceIndex] === targetLines[targetIndex]) {
        dp[sourceIndex][targetIndex] = dp[sourceIndex + 1][targetIndex + 1] + 1;
      } else {
        dp[sourceIndex][targetIndex] = Math.max(
          dp[sourceIndex + 1][targetIndex],
          dp[sourceIndex][targetIndex + 1]
        );
      }
    }
  }

  let sourceIndex = 0;
  let targetIndex = 0;

  while (sourceIndex < sourceLength && targetIndex < targetLength) {
    if (sourceLines[sourceIndex] === targetLines[targetIndex]) {
      comparisons[sourceIndex] = {
        changed: false,
        targetLine: targetLines[targetIndex]
      };
      sourceIndex += 1;
      targetIndex += 1;
      continue;
    }

    if (dp[sourceIndex + 1][targetIndex] >= dp[sourceIndex][targetIndex + 1]) {
      comparisons[sourceIndex] = {
        changed: true,
        targetLine: null
      };
      sourceIndex += 1;
    } else {
      targetIndex += 1;
    }
  }

  while (sourceIndex < sourceLength) {
    comparisons[sourceIndex] = {
      changed: true,
      targetLine: null
    };
    sourceIndex += 1;
  }

  const matcher = new Map();
  let sourceCursor = 0;
  let targetCursor = 0;

  while (sourceCursor < sourceLength && targetCursor < targetLength) {
    if (sourceLines[sourceCursor] === targetLines[targetCursor]) {
      sourceCursor += 1;
      targetCursor += 1;
      continue;
    }

    let nextSource = sourceCursor;
    let nextTarget = targetCursor;

    while (nextSource < sourceLength && nextTarget < targetLength && sourceLines[nextSource] !== targetLines[nextTarget]) {
      if (dp[nextSource + 1][nextTarget] >= dp[nextSource][nextTarget + 1]) {
        nextSource += 1;
      } else {
        nextTarget += 1;
      }
    }

    const sourceBlockLength = nextSource - sourceCursor;
    const targetBlockLength = nextTarget - targetCursor;
    const pairCount = Math.min(sourceBlockLength, targetBlockLength);

    for (let pairIndex = 0; pairIndex < pairCount; pairIndex += 1) {
      matcher.set(sourceCursor + pairIndex, targetCursor + pairIndex);
    }

    sourceCursor = nextSource;
    targetCursor = nextTarget;
  }

  comparisons.forEach((comparison, index) => {
    if (!comparison.changed) {
      return;
    }

    if (matcher.has(index)) {
      comparison.targetLine = targetLines[matcher.get(index)];
    }
  });

  return comparisons;
}

function tokenizeInlineContent(text) {
  const matches = text.match(/(\s+|\$[^$]+\$|[^\s]+)/g);
  const tokens = matches || [text];

  return tokens.map((value) => ({
    value,
    isWhitespace: /^\s+$/.test(value)
  }));
}

function tokenizeMathContent(text) {
  const tokens = [];
  let cursor = 0;

  while (cursor < text.length) {
    const char = text[cursor];

    if (/\s/.test(char)) {
      let nextCursor = cursor + 1;
      while (nextCursor < text.length && /\s/.test(text[nextCursor])) {
        nextCursor += 1;
      }
      tokens.push({ value: text.slice(cursor, nextCursor), isWhitespace: true });
      cursor = nextCursor;
      continue;
    }

    if (char === "\\") {
      let nextCursor = cursor + 1;

      if (/[A-Za-z]/.test(text[nextCursor] || "")) {
        while (nextCursor < text.length && /[A-Za-z]/.test(text[nextCursor])) {
          nextCursor += 1;
        }
      } else {
        nextCursor += 1;
      }

      tokens.push({ value: text.slice(cursor, nextCursor), isWhitespace: false });
      cursor = nextCursor;
      continue;
    }

    if (/[A-Za-z0-9.]/.test(char)) {
      let nextCursor = cursor + 1;
      while (nextCursor < text.length && /[A-Za-z0-9.]/.test(text[nextCursor])) {
        nextCursor += 1;
      }
      tokens.push({ value: text.slice(cursor, nextCursor), isWhitespace: false });
      cursor = nextCursor;
      continue;
    }

    tokens.push({ value: char, isWhitespace: false });
    cursor += 1;
  }

  return tokens;
}

function renderInlineDiff(sourceText, targetText) {
  const sourceTokens = tokenizeInlineContent(sourceText);
  const targetTokens = tokenizeInlineContent(targetText || "");
  const sourceWords = sourceTokens.filter((token) => !token.isWhitespace).map((token) => token.value);
  const targetWords = targetTokens.filter((token) => !token.isWhitespace).map((token) => token.value);
  const changedWordIndices = computeChangedIndices(sourceWords, targetWords);

  if (!changedWordIndices.size) {
    return {
      html: formatInline(sourceText),
      hasDiffTokens: false
    };
  }

  let html = "";
  let sourceWordIndex = 0;
  let tokenIndex = 0;

  while (tokenIndex < sourceTokens.length) {
    const token = sourceTokens[tokenIndex];

    if (token.isWhitespace) {
      html += escapeHtml(token.value);
      tokenIndex += 1;
      continue;
    }

    if (!changedWordIndices.has(sourceWordIndex)) {
      html += formatInline(token.value);
      sourceWordIndex += 1;
      tokenIndex += 1;
      continue;
    }

    let diffRun = token.value;
    sourceWordIndex += 1;
    tokenIndex += 1;

    while (tokenIndex < sourceTokens.length) {
      const nextToken = sourceTokens[tokenIndex];

      if (nextToken.isWhitespace) {
        diffRun += nextToken.value;
        tokenIndex += 1;
        continue;
      }

      if (!changedWordIndices.has(sourceWordIndex)) {
        break;
      }

      diffRun += nextToken.value;
      sourceWordIndex += 1;
      tokenIndex += 1;
    }

    html += `<span class="diff-token">${formatInline(diffRun)}</span>`;
  }

  return {
    html,
    hasDiffTokens: true
  };
}

function renderEquationDiff(sourceLine, targetLine) {
  const sourceContent = sourceLine.replace(/^\$\$\s?/, "").replace(/\s?\$\$$/, "");
  const targetContent = (targetLine || "").replace(/^\$\$\s?/, "").replace(/\s?\$\$$/, "");
  const sourceTokens = tokenizeMathContent(sourceContent);
  const targetTokens = tokenizeMathContent(targetContent);
  const sourceWords = sourceTokens.filter((token) => !token.isWhitespace).map((token) => token.value);
  const targetWords = targetTokens.filter((token) => !token.isWhitespace).map((token) => token.value);
  const changedWordIndices = computeChangedIndices(sourceWords, targetWords);

  if (!changedWordIndices.size) {
    return sourceLine;
  }

  let highlightedContent = "";
  let sourceWordIndex = 0;
  let tokenIndex = 0;

  while (tokenIndex < sourceTokens.length) {
    const token = sourceTokens[tokenIndex];

    if (token.isWhitespace) {
      highlightedContent += token.value;
      tokenIndex += 1;
      continue;
    }

    if (!changedWordIndices.has(sourceWordIndex)) {
      highlightedContent += token.value;
      sourceWordIndex += 1;
      tokenIndex += 1;
      continue;
    }

    let diffRun = token.value;
    sourceWordIndex += 1;
    tokenIndex += 1;

    while (tokenIndex < sourceTokens.length) {
      const nextToken = sourceTokens[tokenIndex];

      if (nextToken.isWhitespace) {
        diffRun += nextToken.value;
        tokenIndex += 1;
        continue;
      }

      if (!changedWordIndices.has(sourceWordIndex)) {
        break;
      }

      diffRun += nextToken.value;
      sourceWordIndex += 1;
      tokenIndex += 1;
    }

    highlightedContent += `\\bbox[2px,border:1.5px solid #b72424]{${diffRun.trim()}}`;
  }

  return `$$ ${highlightedContent} $$`;
}

function renderTranscriptLines(lines, lineComparisons = []) {
  const html = lines
    .map((line, index) => {
      const comparison = lineComparisons[index] || { changed: false, targetLine: null };
      const fallbackClassName = comparison.changed ? ' class="line-diff"' : "";

      if (/^\$\$.*\$\$$/.test(line)) {
        const equationContent =
          comparison.changed && comparison.targetLine
            ? renderEquationDiff(line, comparison.targetLine)
            : line;
        return `<div class="equation${comparison.changed ? " is-diff" : ""}">${equationContent}</div>`;
      }

      if (line.startsWith(">")) {
        const sourceContent = line.replace(/^>\s?/, "");
        const targetContent = (comparison.targetLine || "").replace(/^>\s?/, "");
        const diff = comparison.changed
          ? renderInlineDiff(sourceContent, targetContent)
          : { html: formatInline(sourceContent), hasDiffTokens: false };
        const className = !diff.hasDiffTokens && comparison.changed ? ' class="line-diff"' : "";
        return `<blockquote${className}>${diff.html}</blockquote>`;
      }

      if (/^\*\*.+\*\*$/.test(line)) {
        const diff = comparison.changed
          ? renderInlineDiff(line, comparison.targetLine || "")
          : { html: formatInline(line), hasDiffTokens: false };
        const className = !diff.hasDiffTokens && comparison.changed ? ' class="line-diff"' : "";
        return `<h4${className}>${diff.html}</h4>`;
      }

      const diff = comparison.changed
        ? renderInlineDiff(line, comparison.targetLine || "")
        : { html: formatInline(line), hasDiffTokens: false };
      const className = !diff.hasDiffTokens && comparison.changed ? ' class="line-diff"' : "";
      return `<p${className}>${diff.html}</p>`;
    })
    .join("");

  return html || '<p class="empty-copy">Transcript unavailable.</p>';
}

function syncModeButtons(mode) {
  toggleButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.transcriptMode === mode);
  });
}

function updateMeta(example, mode) {
  const sourceLabel =
    mode === "raw"
      ? "Gemini-2.5-Pro recognition (pre-rectification)"
      : "Observation set expert rectification";

  metaEl.innerHTML = `
    <p><strong>Homework</strong>Homework ${example.homework}</p>
    <p><strong>Student</strong>Student ${example.student}</p>
    <p><strong>Question ID</strong>${example.questionId}</p>
    <p><strong>Source</strong>${sourceLabel}</p>
  `;
}

function syncPills(selectedId) {
  document.querySelectorAll(".homework-pill").forEach((pill) => {
    pill.classList.toggle("is-active", pill.dataset.id === selectedId);
  });
}

function syncNav(sectionId) {
  navLinks.forEach((link) => {
    link.classList.toggle("is-current", link.dataset.navLink === sectionId);
  });
}

function initSectionTracking() {
  if (!("IntersectionObserver" in window)) {
    syncNav("quick-glance");
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      const visibleEntries = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio);

      if (!visibleEntries.length) {
        return;
      }

      syncNav(visibleEntries[0].target.dataset.navSection);
    },
    {
      rootMargin: "-20% 0px -55% 0px",
      threshold: [0.2, 0.45, 0.7]
    }
  );

  navSections.forEach((section) => observer.observe(section));
}

async function typesetMath() {
  if (window.MathJax?.typesetPromise) {
    await window.MathJax.typesetPromise([transcriptEl]);
  }
}

async function fetchTranscriptMarkdown(path) {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(`Failed to load ${path}`);
  }

  return response.text();
}

async function loadTranscriptData(example) {
  if (transcriptCache.has(example.id)) {
    return transcriptCache.get(example.id);
  }

  const [rawMarkdown, rectifiedMarkdown] = await Promise.all([
    fetchTranscriptMarkdown(example.rawMarkdown),
    fetchTranscriptMarkdown(example.rectifiedMarkdown)
  ]);

  const rawLines = cleanMarkdownLines(rawMarkdown);
  const rectifiedLines = cleanMarkdownLines(rectifiedMarkdown);
  const rawLineComparisons = buildLineComparisons(rawLines, rectifiedLines);

  const data = {
    rawMarkdown,
    rectifiedMarkdown,
    rawLines,
    rectifiedLines,
    rawLineComparisons
  };

  transcriptCache.set(example.id, data);
  return data;
}

async function renderCurrentTranscript() {
  const example = examples.find((item) => item.id === transcriptState.currentExampleId);

  if (!example) {
    return;
  }

  const data = transcriptCache.get(example.id);

  if (!data) {
    return;
  }

  const url = new URL(window.location.href);
  url.searchParams.set("example", example.id);
  url.searchParams.set("view", transcriptState.mode);
  window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);

  syncModeButtons(transcriptState.mode);
  updateMeta(example, transcriptState.mode);

  if (transcriptState.mode === "raw") {
    transcriptTitleEl.textContent = "Gemini-2.5-Pro transcript";
    transcriptNoteEl.textContent = data.rawLineComparisons.some((item) => item.changed)
      ? "Red marks highlight mismatched text spans and changed symbol groups in equations."
      : "This example matches the expert-rectified transcript, so no lines are highlighted.";
    transcriptEl.innerHTML = renderTranscriptLines(data.rawLines, data.rawLineComparisons);
  } else {
    transcriptTitleEl.textContent = "Expert-rectified LaTeX transcript";
    transcriptNoteEl.textContent =
      "This is the manually rectified transcript used as the observation-set reference.";
    transcriptEl.innerHTML = renderTranscriptLines(data.rectifiedLines);
  }

  await typesetMath();
}

function buildControls() {
  examples.forEach((example) => {
    const option = document.createElement("option");
    option.value = example.id;
    option.textContent = `Homework ${example.homework} | Q${example.questionId} | Student ${example.student}`;
    selectEl.appendChild(option);

    const pill = document.createElement("button");
    pill.type = "button";
    pill.className = "homework-pill";
    pill.dataset.id = example.id;
    pill.textContent = `HW${example.homework}: Q${example.questionId}`;
    pill.addEventListener("click", () => {
      selectEl.value = example.id;
      void updateExample(example.id);
    });
    pillsEl.appendChild(pill);
  });

  selectEl.addEventListener("change", (event) => {
    void updateExample(event.target.value);
  });

  toggleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.transcriptMode === transcriptState.mode) {
        return;
      }

      transcriptState.mode = button.dataset.transcriptMode;
      void renderCurrentTranscript();
    });
  });
}

async function updateExample(exampleId) {
  const requestId = ++loadSequence;
  const example = examples.find((item) => item.id === exampleId) || examples[0];

  transcriptState.currentExampleId = example.id;
  selectEl.value = example.id;
  syncPills(example.id);
  imageEl.src = example.image;
  imageEl.alt = `Homework ${example.homework}, student ${example.student}, question ${example.questionId}`;
  transcriptEl.innerHTML = '<p class="loading-copy">Loading transcript...</p>';
  transcriptTitleEl.textContent =
    transcriptState.mode === "raw" ? "Gemini-2.5-Pro transcript" : "Expert-rectified LaTeX transcript";
  transcriptNoteEl.textContent = "Loading transcript source...";

  try {
    await loadTranscriptData(example);

    if (requestId !== loadSequence) {
      return;
    }

    await renderCurrentTranscript();
  } catch (error) {
    if (requestId !== loadSequence) {
      return;
    }

    transcriptEl.innerHTML =
      '<p class="empty-copy">The transcript could not be loaded from the copied example assets.</p>';
    transcriptNoteEl.textContent = "Unable to load the transcript source for this example.";
    console.error(error);
  }
}

buildControls();
initSectionTracking();

const initialUrl = new URL(window.location.href);
const initialExampleId = initialUrl.searchParams.get("example");
void updateExample(initialExampleId || examples[0].id);
