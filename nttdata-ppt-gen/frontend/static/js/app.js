/* NTT DATA AI Presentation Generator — app.js v3 */
(function () {
  "use strict";

  let currentStep = 0;
  let selectedTheme = "light";

  const stepTabs   = document.querySelectorAll(".step-tab");
  const stepPanels = document.querySelectorAll(".step-panel");

  window.goStep = function (n) {
    stepPanels[currentStep].classList.remove("active");
    stepTabs[currentStep].classList.remove("active");
    if (currentStep < n) stepTabs[currentStep].classList.add("done");
    currentStep = n;
    stepPanels[currentStep].classList.add("active");
    stepTabs[currentStep].classList.remove("done");
    stepTabs[currentStep].classList.add("active");
  };

  window.selectTheme = function (t) {
    selectedTheme = t;
    document.getElementById("theme-light").classList.toggle("selected", t === "light");
    document.getElementById("theme-dark").classList.toggle("selected",  t === "dark");
  };

  window.handleCustom = function (selectId, fieldId) {
    const sel = document.getElementById(selectId);
    document.getElementById(fieldId).classList.toggle("show", sel.value === "custom");
  };

  window.updateSlideCount = function () {
    const sel  = document.getElementById("duration");
    const pill = document.getElementById("slidePill");
    const txt  = document.getElementById("slideCountText");
    if (!sel.value) { pill.classList.remove("show"); return; }
    txt.textContent = sel.value.split("|")[1] + " slides";
    pill.classList.add("show");
  };

  window.toggleChip = function (el) { el.classList.toggle("selected"); };

  function getSelectVal(id) {
    const el = document.getElementById(id);
    if (!el) return "";
    if (el.value === "custom") {
      const ct = document.getElementById(id + "CustomText");
      return ct ? ct.value.trim() : "";
    }
    return el.value;
  }

  function getChips(containerId) {
    return Array.from(document.querySelectorAll(`#${containerId} .chip.selected`))
      .map(c => c.dataset.value || c.textContent.trim());
  }

  function validate() {
    return (
      document.getElementById("topic").value.trim() &&
      getSelectVal("objective") &&
      getSelectVal("audience") &&
      document.getElementById("duration").value
    );
  }

  function buildConfig() {
    const durEl = document.getElementById("duration");
    return {
      topic:         document.getElementById("topic").value.trim(),
      objective:     getSelectVal("objective"),
      audience:      getSelectVal("audience"),
      duration:      durEl.options[durEl.selectedIndex]?.text || "",
      slide_range:   durEl.value ? durEl.value.split("|")[1] : "12-15",
      tech_level:    document.getElementById("techLevel")?.value || "Advanced",
      theme:         selectedTheme,
      language:      document.getElementById("language")?.value || "English",
      speaker_notes: document.getElementById("speakerNotes")?.checked || false,
    };
  }

  const STATUS_STEPS = [
    "Analysing requirements",
    "Generating slide plan via Groq",
    "Building PowerPoint file",
    "Preparing download"
  ];

  function renderStatusSteps(activeIdx, errMsg, containerId) {
    const c = document.getElementById(containerId);
    if (!c) return;
    c.innerHTML = STATUS_STEPS.map((label, i) => {
      let cls = "status-step", dot = i + 1, spin = "";
      if (errMsg && i === activeIdx)      { cls += " error"; dot = "✕"; }
      else if (i < activeIdx)             { cls += " done";  dot = "✓"; }
      else if (i === activeIdx)           { cls += " active"; spin = '<span class="spinner"></span>'; dot = ""; }
      return `<div class="${cls}"><div class="step-dot">${spin || dot}</div>${label}</div>`;
    }).join("");
  }

  function setProgress(pct, barId) {
    const b = document.getElementById(barId);
    if (b) b.style.width = pct + "%";
  }

  function showError(msg, bannerId) {
    const el = document.getElementById(bannerId);
    if (el) { el.textContent = "⚠️  " + msg; el.classList.add("show"); }
  }

  function clearError(bannerId) {
    const el = document.getElementById(bannerId);
    if (el) el.classList.remove("show");
  }

  async function _doGenerate(btnEl, btnTextEl, progressAreaId, progressBarId, statusStepsId, errorBannerId) {
    clearError(errorBannerId);
    if (!validate()) {
      showError("Please fill in: Topic, Objective, Audience, and Duration.", errorBannerId);
      return;
    }

    btnEl.disabled = true;
    btnTextEl.textContent = "Generating…";

    const progressArea = document.getElementById(progressAreaId);
    progressArea.classList.add("show");
    setProgress(5, progressBarId);
    renderStatusSteps(0, null, statusStepsId);

    const config = buildConfig();

    try {
      renderStatusSteps(1, null, statusStepsId);
      setProgress(25, progressBarId);

      const response = await fetch("/api/generate", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(config),
      });

      renderStatusSteps(2, null, statusStepsId);
      setProgress(65, progressBarId);

      if (!response.ok) {
        let errMsg = "Server error";
        try { const d = await response.json(); errMsg = d.error || errMsg; } catch(_){}
        throw new Error(errMsg);
      }

      renderStatusSteps(3, null, statusStepsId);
      setProgress(90, progressBarId);

      const blob     = await response.blob();
      const topic    = config.topic.slice(0,40).replace(/\s+/g,"_").replace(/\//g,"-");
      const filename = `NTT_DATA_${topic}.pptx`;
      const url      = URL.createObjectURL(blob);
      const a        = document.createElement("a");
      a.href = url; a.download = filename;
      document.body.appendChild(a); a.click();
      document.body.removeChild(a); URL.revokeObjectURL(url);

      setProgress(100, progressBarId);
      renderStatusSteps(4, null, statusStepsId);
      btnTextEl.textContent = "✓ Downloaded!";
      setTimeout(() => {
        btnTextEl.textContent = btnEl.id === "quickGenBtn" ? "⚡ Generate Now" : "✦ Generate NTT DATA Presentation";
        btnEl.disabled = false;
      }, 3000);

    } catch (err) {
      renderStatusSteps(2, err.message, statusStepsId);
      showError(err.message, errorBannerId);
      btnTextEl.textContent = btnEl.id === "quickGenBtn" ? "⚡ Generate Now" : "✦ Generate NTT DATA Presentation";
      btnEl.disabled = false;
    }
  }

  window.generatePresentation = function () {
    // Determine which button/progress area to use based on current step
    if (currentStep === 0) {
      _doGenerate(
        document.getElementById("quickGenBtn"),
        document.getElementById("quickGenText"),
        "progressArea0", "progressBar0", "statusSteps0", "errorBanner0"
      );
    } else {
      _doGenerate(
        document.getElementById("generateBtn"),
        document.getElementById("genBtnText"),
        "progressArea", "progressBar", "statusSteps", "errorBanner"
      );
    }
  };

})();
