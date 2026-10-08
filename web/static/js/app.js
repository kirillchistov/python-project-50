(function () {
  function requestTrace(algorithm, payload) {
    if (window.DSA_STATIC && window.DsaTracers) {
      return Promise.resolve(window.DsaTracers.run(algorithm, payload));
    }
    var prefix = window.DSA_BASE || "";
    return fetch(prefix + "/api/trace/" + algorithm, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) {
          throw new Error(data.detail || "Ошибка API");
        }
        return data;
      });
    });
  }

  function collectPayload(section) {
    var payload = {};
    section.querySelectorAll("[data-field]").forEach(function (field) {
      var name = field.getAttribute("data-field");
      var value = field.value;
      if (field.getAttribute("data-json") === "1") {
        payload[name] = JSON.parse(value);
        return;
      }
      if (field.type === "number" || field.type === "range") {
        payload[name] = Number(value);
        return;
      }
      payload[name] = value;
    });
    return payload;
  }

  document.querySelectorAll("[data-playground]").forEach(function (section) {
    var algorithm = section.getAttribute("data-algorithm");
    var viz = section.querySelector("[data-viz]");
    var errorBox = section.querySelector("[data-error]");
    var player = window.DsaPlayer(section, function (step) {
      window.DsaViz.render(viz, step);
    });

    section.querySelector("[data-run]").addEventListener("click", function () {
      errorBox.hidden = true;
      var payload;
      try {
        payload = collectPayload(section);
      } catch (error) {
        errorBox.hidden = false;
        errorBox.textContent = "Не удалось прочитать ввод: " + error.message;
        return;
      }
      requestTrace(algorithm, payload)
        .then(function (trace) {
          player.load(trace);
        })
        .catch(function (error) {
          errorBox.hidden = false;
          errorBox.textContent = error.message;
        });
    });

    section.querySelectorAll("input[type='range']").forEach(function (field) {
      field.addEventListener("change", function () {
        section.querySelector("[data-run]").click();
      });
    });
    section.querySelector("[data-run]").click();
  });

  document.querySelectorAll("[data-question]").forEach(function (question) {
    var answer = Number(question.getAttribute("data-answer"));
    var explain = question.querySelector(".explain");
    question.querySelectorAll("[data-option]").forEach(function (button) {
      button.addEventListener("click", function () {
        var choice = Number(button.getAttribute("data-option"));
        question.querySelectorAll("[data-option]").forEach(function (other) {
          other.disabled = true;
        });
        if (choice === answer) {
          button.classList.add("is-ok");
        } else {
          button.classList.add("is-bad");
          var correct = question.querySelector('[data-option="' + answer + '"]');
          if (correct) correct.classList.add("is-ok");
        }
        if (explain) explain.hidden = false;
      });
    });
  });
})();
