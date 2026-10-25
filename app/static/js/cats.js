(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var tilt = 12;
  var shift = 28;
  var period = 3200;

  document.querySelectorAll(".method-card").forEach(function (card) {
    var img = card.querySelector("img");
    if (!img) return;

    var amplitude = 0;
    var frame = 0;

    function tick(now) {
      var target = card.matches(":hover") ? 1 : 0;
      amplitude += (target - amplitude) * 0.06;

      if (target === 0 && amplitude < 0.004) {
        amplitude = 0;
        img.style.transform = "";
        frame = 0;
        return;
      }

      var wave = Math.sin((now / period) * Math.PI * 2);
      var angle = tilt * amplitude * wave;
      var travel = shift * amplitude * wave;
      img.style.transform =
        "translateX(" + travel.toFixed(2) + "px) rotate(" + angle.toFixed(2) + "deg)";
      frame = requestAnimationFrame(tick);
    }

    function start() {
      if (!frame) frame = requestAnimationFrame(tick);
    }

    card.addEventListener("pointerenter", start);
    card.addEventListener("pointerleave", start);
  });
})();
