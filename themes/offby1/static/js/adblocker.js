function ready(fn) {
  if (document.readyState != "loading") {
    fn();
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}

ready(function () {
  const e = document.createElement("div");
  e.id = "ftf-dma-target";
  e.style.display = "none";
  document.body.appendChild(e);
});

ready(() => {
  const cookieNameValue = "ftf-dma-notice=shown";
  const note = document.getElementById("ftf-dma-note");
  const noteCloseButton = document.getElementById("ftf-dma-close-btn");

  if (note !== null && noteCloseButton !== null) {
    noteCloseButton.onclick = (ev) => {
      note.classList.add("d-none");
      document.cookie = cookieNameValue;
    };
  }

  if (document.cookie.indexOf(cookieNameValue) === -1) {
    if (note !== null) {
      note.classList.remove("d-none");
    }
  }
});
