const FEED_SELECTOR = ".landing #monitoring .event-feed";

function waitForMonitoringRuntime(maxFrames = 180) {
  return new Promise((resolve) => {
    let frames = 0;

    const check = () => {
      const feed = document.querySelector(FEED_SELECTOR);
      const line = feed?.querySelector(".event-line");
      const dots = feed ? [...feed.querySelectorAll(".event-dot")] : [];

      if (feed && line && dots.length >= 2 && window.gsap && window.ScrollTrigger) {
        resolve({
          feed,
          line,
          dots,
          gsap: window.gsap,
          ScrollTrigger: window.ScrollTrigger,
        });
        return;
      }

      if (frames >= maxFrames) {
        resolve(null);
        return;
      }

      frames += 1;
      window.requestAnimationFrame(check);
    };

    check();
  });
}

function killPreviousLineAnimation(ScrollTrigger, feed, line) {
  ScrollTrigger.getAll().forEach((trigger) => {
    const targets = trigger.animation?.targets?.() || [];
    const controlsLine = trigger.trigger === feed && targets.includes(line);

    if (!controlsLine) return;
    trigger.animation?.kill();
    trigger.kill();
  });
}

export async function initializeMonitoringTimeline() {
  if (window.__CREDIBIL_MONITORING_TIMELINE_INITIALIZED__) return;
  window.__CREDIBIL_MONITORING_TIMELINE_INITIALIZED__ = true;

  const runtime = await waitForMonitoringRuntime();
  if (!runtime) return;

  const {
    feed,
    line,
    dots,
    gsap,
    ScrollTrigger,
  } = runtime;

  const firstDot = dots[0];
  const lastDot = dots[dots.length - 1];

  const syncGeometry = () => {
    const feedRect = feed.getBoundingClientRect();
    const firstRect = firstDot.getBoundingClientRect();
    const lastRect = lastDot.getBoundingClientRect();

    const firstCenterX = firstRect.left - feedRect.left + firstRect.width / 2;
    const firstCenterY = firstRect.top - feedRect.top + firstRect.height / 2;
    const lastCenterY = lastRect.top - feedRect.top + lastRect.height / 2;

    line.style.left = `${firstCenterX}px`;
    line.style.top = `${firstCenterY}px`;
    line.style.bottom = "auto";
    line.style.height = `${Math.max(0, lastCenterY - firstCenterY)}px`;
  };

  killPreviousLineAnimation(ScrollTrigger, feed, line);
  syncGeometry();

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    gsap.set(line, {
      x: 0,
      scaleY: 1,
      transformOrigin: "50% 0%",
    });
    return;
  }

  gsap.fromTo(
    line,
    {
      x: 0,
      scaleY: 0,
      transformOrigin: "50% 0%",
    },
    {
      x: 0,
      scaleY: 1,
      ease: "none",
      scrollTrigger: {
        trigger: firstDot,
        start: "center 72%",
        endTrigger: lastDot,
        end: "center 72%",
        scrub: 0.35,
        invalidateOnRefresh: true,
        onRefreshInit: syncGeometry,
        onRefresh: syncGeometry,
      },
    },
  );

  const resizeObserver = new ResizeObserver(() => {
    syncGeometry();
  });
  resizeObserver.observe(feed);
  dots.forEach((dot) => resizeObserver.observe(dot));

  window.__CREDIBIL_MONITORING_TIMELINE_CLEANUP__ = () => {
    resizeObserver.disconnect();
    ScrollTrigger.getAll().forEach((trigger) => {
      const targets = trigger.animation?.targets?.() || [];
      if (targets.includes(line)) {
        trigger.animation?.kill();
        trigger.kill();
      }
    });
  };
}
