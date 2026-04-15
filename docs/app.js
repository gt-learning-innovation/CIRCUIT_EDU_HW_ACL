const examples = [
  {
    id: "hw1-student21-q1-5-2",
    homework: 1,
    student: 21,
    questionId: "1.5-2",
    image: "./assets/examples/hw1_student21_q1_5-2.png",
    markdown: "./assets/examples/hw1_student21_q1_5-2.md"
  },
  {
    id: "hw2-student31-q4-2-2",
    homework: 2,
    student: 31,
    questionId: "4.2-2",
    image: "./assets/examples/hw2_student31_q4_2-2.png",
    markdown: "./assets/examples/hw2_student31_q4_2-2.md"
  },
  {
    id: "hw4-student4-q6-4-4",
    homework: 4,
    student: 4,
    questionId: "6.4-4",
    image: "./assets/examples/hw4_student4_q6_4-4.png",
    markdown: "./assets/examples/hw4_student4_q6_4-4.md"
  },
  {
    id: "hw5-student42-q7-5-4",
    homework: 5,
    student: 42,
    questionId: "7.5-4",
    image: "./assets/examples/hw5_student42_q7_5-4.png",
    markdown: "./assets/examples/hw5_student42_q7_5-4.md"
  },
  {
    id: "hw6-student16-q8-7-3",
    homework: 6,
    student: 16,
    questionId: "8.7-3",
    image: "./assets/examples/hw6_student16_q8_7-3.png",
    markdown: "./assets/examples/hw6_student16_q8_7-3.md"
  },
  {
    id: "hw7-student35-q9-7-2",
    homework: 7,
    student: 35,
    questionId: "9.7-2",
    image: "./assets/examples/hw7_student35_q9_7-2.png",
    markdown: "./assets/examples/hw7_student35_q9_7-2.md"
  },
  {
    id: "hw8-student41-q10-6-1",
    homework: 8,
    student: 41,
    questionId: "10.6-1",
    image: "./assets/examples/hw8_student41_q10_6-1.png",
    markdown: "./assets/examples/hw8_student41_q10_6-1.md"
  }
];

const selectEl = document.querySelector("#example-select");
const pillsEl = document.querySelector("#homework-pills");
const metaEl = document.querySelector("#example-meta");
const imageEl = document.querySelector("#example-image");
const transcriptEl = document.querySelector("#transcript-body");
const navLinks = document.querySelectorAll("[data-nav-link]");
const navSections = document.querySelectorAll("[data-nav-section]");

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

function renderTranscript(markdown) {
  const normalized = markdown
    .replace(/\r/g, "")
    .split("\n")
    .filter((line) => !line.startsWith("![Source Image]"));

  const html = normalized
    .map((line) => {
      const trimmed = line.trim();

      if (!trimmed) {
        return "";
      }

      if (/^\$\$.*\$\$$/.test(trimmed)) {
        return `<div class="equation">${trimmed}</div>`;
      }

      if (trimmed.startsWith(">")) {
        return `<blockquote>${formatInline(trimmed.replace(/^>\s?/, ""))}</blockquote>`;
      }

      if (/^\*\*.+\*\*$/.test(trimmed)) {
        return `<h4>${formatInline(trimmed)}</h4>`;
      }

      return `<p>${formatInline(trimmed)}</p>`;
    })
    .filter(Boolean)
    .join("");

  return html || '<p class="empty-copy">Transcript unavailable.</p>';
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
}

function updateMeta(example) {
  metaEl.innerHTML = `
    <p><strong>Homework</strong>Homework ${example.homework}</p>
    <p><strong>Student</strong>Student ${example.student}</p>
    <p><strong>Question ID</strong>${example.questionId}</p>
    <p><strong>Source</strong>Observation set expert rectification</p>
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

async function updateExample(exampleId) {
  const example = examples.find((item) => item.id === exampleId) || examples[0];
  const url = new URL(window.location.href);

  selectEl.value = example.id;
  syncPills(example.id);
  updateMeta(example);
  imageEl.src = example.image;
  imageEl.alt = `Homework ${example.homework}, student ${example.student}, question ${example.questionId}`;
  transcriptEl.innerHTML = '<p class="loading-copy">Loading transcript...</p>';
  url.searchParams.set("example", example.id);
  window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);

  try {
    const response = await fetch(example.markdown);

    if (!response.ok) {
      throw new Error(`Failed to load ${example.markdown}`);
    }

    const markdown = await response.text();
    transcriptEl.innerHTML = renderTranscript(markdown);
    await typesetMath();
  } catch (error) {
    transcriptEl.innerHTML =
      '<p class="empty-copy">The transcript could not be loaded from the copied example assets.</p>';
    console.error(error);
  }
}

buildControls();
initSectionTracking();

const initialId = new URL(window.location.href).searchParams.get("example");
void updateExample(initialId || examples[0].id);
