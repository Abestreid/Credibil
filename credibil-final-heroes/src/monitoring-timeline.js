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

function centerWithin(element, ancestor) {
  let x = element.offsetWidth / 2;
  let y = element.offsetHeight / 2;
  let node = element;

  while (node && node !== ancestor) {
    x += node.offsetLeft;
    y += node.offsetTop;
    node = node.offsetParent;
  }

  if (node === ancestor) return { x, y };

  const ancestorRect = ancestor.getBoundingClientRect();
  const elementRect = element.getBoundingClientRect();
  return {
    x: elementRect.left - ancestorRect.left + elementRect.width / 2,
    y: elementRect.top - ancestorRect.top + elementRect.height / 2,
  };
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
    const firstCenter = centerWithin(firstDot, feed);
    const lastCenter = centerWithin(lastDot, feed);
    const halfLineWidth = line.offsetWidth / 2;

    line.style.left = `${firstCenter.x - halfLineWidth}px`;
    line.style.top = `${firstCenter.y}px`;
    line.style.bottom = "auto";
    line.style.height = `${Math.max(0, lastCenter.y - firstCenter.y)}px`;
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

  const onResize = () => syncGeometry();
  window.addEventListener("resize", onResize, { passive: true });

  const resizeObserver = typeof ResizeObserver === "function"
    ? new ResizeObserver(syncGeometry)
    : null;

  resizeObserver?.observe(feed);
  dots.forEach((dot) => resizeObserver?.observe(dot));

  window.__CREDIBIL_MONITORING_TIMELINE_CLEANUP__ = () => {
    resizeObserver?.disconnect();
    window.removeEventListener("resize", onResize);
    ScrollTrigger.getAll().forEach((trigger) => {
      const targets = trigger.animation?.targets?.() || [];
      if (targets.includes(line)) {
        trigger.animation?.kill();
        trigger.kill();
      }
    });
  };
}
