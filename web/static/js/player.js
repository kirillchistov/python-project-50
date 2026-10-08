window.DsaPlayer = function createPlayer(root, renderStep) {
  var steps = [];
  var index = 0;
  var timer = null;
  var msg = root.querySelector("[data-step-msg]");
  var counter = root.querySelector("[data-step-counter]");

  function current() {
    return steps[index] || null;
  }

  function paint() {
    var step = current();
    if (msg) {
      msg.textContent = step ? step.message : "Нет шагов.";
    }
    if (counter) {
      counter.textContent = steps.length ? index + 1 + " / " + steps.length : "0 / 0";
    }
    renderStep(step);
  }

  function load(trace) {
    pause();
    steps = (trace && trace.steps) || [];
    index = 0;
    paint();
  }

  function next() {
    if (index < steps.length - 1) {
      index += 1;
      paint();
    } else {
      pause();
    }
  }

  function prev() {
    if (index > 0) {
      index -= 1;
      paint();
    }
  }

  function play() {
    if (!steps.length) return;
    pause();
    timer = setInterval(next, 900);
  }

  function pause() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  root.querySelector("[data-prev]").addEventListener("click", prev);
  root.querySelector("[data-next]").addEventListener("click", next);
  root.querySelector("[data-play]").addEventListener("click", play);
  root.querySelector("[data-pause]").addEventListener("click", pause);

  return { load: load, next: next, prev: prev, play: play, pause: pause };
};
