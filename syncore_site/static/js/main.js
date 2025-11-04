// ===== SMOOTH ANCHOR SCROLL =====
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", (e) => {
    const id = anchor.getAttribute("href").slice(1);
    const element = document.getElementById(id);
    if (element) {
      e.preventDefault();
      element.scrollIntoView({ behavior: "smooth" });
    }
  });
});

// ===== BASIC REVEAL ON SCROLL =====
const basicRevealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("show");
      }
    });
  },
  { threshold: 0.2 }
);

document
  .querySelectorAll(".reveal")
  .forEach((el) => basicRevealObserver.observe(el));

// ===== SEQUENTIAL REVEAL =====
const seqObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const group = [...document.querySelectorAll(".reveal-seq")];
      group.forEach((el, i) =>
        setTimeout(() => el.classList.add("show"), i * 120)
      );
      seqObserver.disconnect();
    });
  },
  { threshold: 0.2 }
);

const firstSeqElement = document.querySelector(".reveal-seq");
if (firstSeqElement) {
  seqObserver.observe(firstSeqElement);
}

// ===== RESULT TILES - ONE BY ONE SCROLL ANIMATION =====
const resultTiles = document.querySelectorAll(".result-tile");
let currentActiveResult = -1;

// Create observer for result tiles
const resultObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const tiles = Array.from(resultTiles);
        const index = tiles.indexOf(entry.target);

        // Only show this card and previous cards
        tiles.forEach((tile, i) => {
          if (i <= index) {
            setTimeout(() => {
              tile.classList.add("visible");
            }, (i - (currentActiveResult + 1)) * 200); // Stagger animation
          }
        });

        currentActiveResult = Math.max(currentActiveResult, index);
      }
    });
  },
  {
    threshold: 0.3,
    rootMargin: "-50px 0px -100px 0px",
  }
);

// Observe each result tile
resultTiles.forEach((tile) => {
  resultObserver.observe(tile);
});

// ===== STEP CARDS - ONE BY ONE SCROLL ANIMATION =====
const stepCards = document.querySelectorAll(".step-card");
let stepsActivated = false;

// Create observer for step cards
const stepObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting && !stepsActivated) {
        const cards = Array.from(stepCards);

        // Animate all step cards in sequence
        cards.forEach((card, index) => {
          setTimeout(() => {
            card.classList.add("visible");
          }, index * 200); // 200ms delay between each card
        });

        stepsActivated = true;
        stepObserver.disconnect(); // Stop observing once activated
      }
    });
  },
  {
    threshold: 0.2,
    rootMargin: "-50px 0px",
  }
);

// Observe the first step card to trigger the sequence
if (stepCards.length > 0) {
  stepObserver.observe(stepCards[0]);
}

// ===== SCROLL DIRECTION DETECTION (Enhanced) =====
let lastScrollTop = window.pageYOffset || document.documentElement.scrollTop;
let ticking = false;

function handleScroll() {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const scrollingDown = scrollTop > lastScrollTop;

  // Check each result tile
  resultTiles.forEach((tile, index) => {
    const rect = tile.getBoundingClientRect();
    const windowHeight = window.innerHeight;

    // More precise viewport detection
    const isInViewport =
      rect.top < windowHeight * 0.75 && rect.bottom > windowHeight * 0.25;

    if (isInViewport && !tile.classList.contains("visible")) {
      tile.classList.add("visible");
    }
  });

  lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
  ticking = false;
}

window.addEventListener(
  "scroll",
  () => {
    if (!ticking) {
      window.requestAnimationFrame(handleScroll);
      ticking = true;
    }
  },
  { passive: true }
);

// ===== INITIAL CHECK ON PAGE LOAD =====
window.addEventListener("load", () => {
  handleScroll();

  // Log debug info
  console.log("🎯 Scroll Animation System Loaded");
  console.log(`📊 Result Tiles: ${resultTiles.length}`);
  console.log(`📋 Step Cards: ${stepCards.length}`);
});

// ===== UTILITY: Reset animations (for testing) =====
function resetAnimations() {
  resultTiles.forEach((tile) => tile.classList.remove("visible"));
  stepCards.forEach((card) => card.classList.remove("visible"));
  stepsActivated = false;
  currentActiveResult = -1;
  console.log("🔄 Animations reset");
}

// Expose reset function for debugging
window.resetAnimations = resetAnimations;
