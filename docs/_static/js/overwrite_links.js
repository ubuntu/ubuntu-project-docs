// Replace oldDomain with newDomain
const oldDomain = "canonical-ubuntu-projectubuntu.readthedocs-hosted.com";
const newDomain = "ubuntu.com/project/docs";

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function overwriteMatchingAnchorUrls(container) {
  if (!container) return;

  const anchors = container.querySelectorAll("a[href]");
  const oldDomainRegex = new RegExp(escapeRegExp(oldDomain), "g");

  anchors.forEach((anchor) => {
    anchor.href = anchor.href.replace(oldDomainRegex, newDomain);
  });
}

overwriteMatchingAnchorUrls(document.querySelector("header"));

// Use a MutationObserver to wait for the RTD flyout element to appear in the DOM
const observer = new MutationObserver(function (mutations, obs) {
  overwriteMatchingAnchorUrls(document.querySelector("header"));

  const rtdFlyout = document.querySelector("readthedocs-flyout");
  if (!rtdFlyout) return;

  obs.disconnect();

  rtdFlyout.addEventListener("click", function () {
    const shadowRoot = rtdFlyout.shadowRoot;
    if (!shadowRoot) return;

    overwriteMatchingAnchorUrls(shadowRoot);
  });
});

observer.observe(document.body, { childList: true, subtree: true });
