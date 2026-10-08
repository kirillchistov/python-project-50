(function () {
  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function svgEl(name, attrs) {
    var node = document.createElementNS("http://www.w3.org/2000/svg", name);
    Object.keys(attrs || {}).forEach(function (key) {
      node.setAttribute(key, attrs[key]);
    });
    return node;
  }

  function has(list, value) {
    return (list || []).map(String).indexOf(String(value)) !== -1;
  }

  function renderArray(snapshot, highlight) {
    var wrap = el("div");
    if (snapshot.caption) wrap.appendChild(el("p", "muted", snapshot.caption));
    var row = el("div", "array-row");
    (snapshot.items || []).forEach(function (item, index) {
      var cell = el("div", "array-cell", String(item));
      if (has(highlight.comparing, index)) cell.classList.add("is-compare");
      if (has(highlight.swapping, index)) cell.classList.add("is-swap");
      if (has(highlight.sorted, index) || has(highlight.range, index)) cell.classList.add("is-sorted");
      if (has(highlight.pivot, index)) cell.classList.add("is-pivot");
      if (has(highlight.found, index)) cell.classList.add("is-found");
      row.appendChild(cell);
    });
    wrap.appendChild(row);
    return wrap;
  }

  function renderStack(snapshot, highlight) {
    var list = el("div", "stack-list");
    (snapshot.items || []).forEach(function (item, index) {
      var node = el("div", "stack-item", String(item));
      if (has(highlight.head, index)) node.classList.add("is-head");
      list.appendChild(node);
    });
    if (!(snapshot.items || []).length) list.appendChild(el("div", "muted", "пусто"));
    return list;
  }

  function renderQueue(snapshot, highlight) {
    var row = el("div", "queue-row");
    (snapshot.items || []).forEach(function (item, index) {
      var node = el("div", "queue-item", String(item));
      if (has(highlight.head, index) || index === 0) node.classList.add("is-head");
      if (has(highlight.tail, index)) node.classList.add("is-on");
      row.appendChild(node);
    });
    if (!(snapshot.items || []).length) row.appendChild(el("div", "muted", "очередь пуста"));
    return row;
  }

  function renderList(snapshot, highlight) {
    var svg = svgEl("svg", { viewBox: "0 0 900 140", width: "100%", height: "140" });
    (snapshot.nodes || []).forEach(function (node, index) {
      var x = 40 + index * 140;
      var rect = svgEl("rect", {
        x: x,
        y: 40,
        width: 90,
        height: 48,
        rx: 10,
        fill: has(highlight.comparing, node.id) ? "#dbeafe" : "#fff",
        stroke: "#1c1917",
      });
      var text = svgEl("text", { x: x + 45, y: 70, "text-anchor": "middle" });
      text.textContent = String(node.value);
      svg.appendChild(rect);
      svg.appendChild(text);
      if (node.next != null) {
        svg.appendChild(svgEl("line", {
          x1: x + 90,
          y1: 64,
          x2: x + 140,
          y2: 64,
          stroke: "#1c1917",
          "stroke-width": 2,
        }));
      }
    });
    var wrap = el("div", "svg-wrap");
    wrap.appendChild(svg);
    return wrap;
  }

  function renderHash(snapshot, highlight) {
    var wrap = el("div");
    (snapshot.buckets || []).forEach(function (bucket, index) {
      var row = el("div", "hash-bucket", index + " → [" + bucket.join(", ") + "]");
      if (has(highlight.bucket, index)) row.classList.add("is-on");
      wrap.appendChild(row);
    });
    return wrap;
  }

  function layoutTree(nodes, rootId) {
    var byId = {};
    (nodes || []).forEach(function (node) {
      byId[node.id] = node;
    });
    var pos = {};
    var cursor = 0;
    function kids(node) {
      if (node.children && node.children.length) return node.children;
      return [node.left, node.right].filter(function (id) { return id != null; });
    }
    function walk(id, depth) {
      if (id == null || !byId[id]) return;
      var node = byId[id];
      var children = kids(node);
      if (!children.length) {
        pos[id] = { x: cursor, y: depth };
        cursor += 1;
        return;
      }
      children.forEach(function (child) { walk(child, depth + 1); });
      var xs = children.map(function (child) { return pos[child].x; });
      pos[id] = { x: (Math.min.apply(null, xs) + Math.max.apply(null, xs)) / 2, y: depth };
    }
    walk(rootId, 0);
    return { pos: pos, byId: byId };
  }

  function renderTree(snapshot, highlight) {
    var nodes = snapshot.nodes || [];
    if (!nodes.length) return el("div", "muted", "дерево пусто");
    var laid = layoutTree(nodes, snapshot.root);
    var maxX = 1;
    var maxY = 1;
    Object.keys(laid.pos).forEach(function (id) {
      maxX = Math.max(maxX, laid.pos[id].x + 1);
      maxY = Math.max(maxY, laid.pos[id].y + 1);
    });
    var width = Math.max(640, maxX * 90);
    var height = Math.max(180, maxY * 90);
    var svg = svgEl("svg", {
      viewBox: "0 0 " + width + " " + height,
      width: "100%",
      height: String(Math.min(height, 420)),
    });
    nodes.forEach(function (node) {
      var children = node.children || [node.left, node.right].filter(function (id) { return id != null; });
      children.forEach(function (childId) {
        if (!laid.pos[node.id] || !laid.pos[childId]) return;
        svg.appendChild(svgEl("line", {
          x1: 50 + laid.pos[node.id].x * 80,
          y1: 40 + laid.pos[node.id].y * 80,
          x2: 50 + laid.pos[childId].x * 80,
          y2: 40 + laid.pos[childId].y * 80,
          stroke: "#a8a29e",
        }));
      });
    });
    nodes.forEach(function (node) {
      var p = laid.pos[node.id];
      if (!p) return;
      var cx = 50 + p.x * 80;
      var cy = 40 + p.y * 80;
      var circle = svgEl("circle", {
        cx: cx,
        cy: cy,
        r: 22,
        class: treeClass(node, highlight),
        fill: treeFill(node, highlight),
        stroke: "#1c1917",
      });
      var text = svgEl("text", { x: cx, y: cy + 5, "text-anchor": "middle", "font-size": "13" });
      text.textContent = String(node.value);
      svg.appendChild(circle);
      svg.appendChild(text);
    });
    var wrap = el("div", "svg-wrap");
    wrap.appendChild(svg);
    return wrap;
  }

  function treeFill(node, highlight) {
    if (has(highlight.found, node.value) || has(highlight.found, node.id)) return "#bbf7d0";
    if (has(highlight.pivot, node.value)) return "#fbcfe8";
    if (has(highlight.comparing, node.value) || has(highlight.focus, node.value)) return "#bfdbfe";
    if (node.type === "added") return "#bbf7d0";
    if (node.type === "removed") return "#fecaca";
    if (node.type === "changed") return "#fde68a";
    if (node.type === "nested") return "#bfdbfe";
    return "#fff";
  }

  function treeClass(node, highlight) {
    if (highlight && highlight.key && String(node.value) === String(highlight.key)) return "node-current";
    return "";
  }

  function renderGraph(snapshot, highlight) {
    var svg = svgEl("svg", { viewBox: "0 0 460 260", width: "100%", height: "260" });
    (snapshot.edges || []).forEach(function (edge) {
      var a = byNode(snapshot.nodes, edge.source);
      var b = byNode(snapshot.nodes, edge.target);
      if (!a || !b) return;
      svg.appendChild(svgEl("line", {
        x1: a.x + 40,
        y1: a.y + 20,
        x2: b.x + 40,
        y2: b.y + 20,
        stroke: "#a8a29e",
        "stroke-width": 2,
      }));
      var label = svgEl("text", {
        x: (a.x + b.x) / 2 + 40,
        y: (a.y + b.y) / 2 + 16,
        "font-size": "12",
        fill: "#57534e",
      });
      label.textContent = String(edge.weight);
      svg.appendChild(label);
    });
    (snapshot.nodes || []).forEach(function (node) {
      var current = highlight.current || (snapshot.current ? [snapshot.current] : []);
      var visited = highlight.visited || snapshot.visited || [];
      var fill = "#fff";
      if (has(visited, node.id)) fill = "#ddd6fe";
      if (has(highlight.frontier || snapshot.frontier, node.id)) fill = "#fde68a";
      if (has(current, node.id)) fill = "#93c5fd";
      svg.appendChild(svgEl("circle", {
        cx: node.x + 40,
        cy: node.y + 20,
        r: 28,
        fill: fill,
        stroke: "#1c1917",
      }));
      var text = svgEl("text", { x: node.x + 40, y: node.y + 16, "text-anchor": "middle", "font-size": "11" });
      text.textContent = node.label;
      svg.appendChild(text);
      if (snapshot.dist && snapshot.dist[node.id] != null) {
        var d = svgEl("text", { x: node.x + 40, y: node.y + 32, "text-anchor": "middle", "font-size": "11", fill: "#0f766e" });
        d.textContent = String(snapshot.dist[node.id]);
        svg.appendChild(d);
      }
    });
    var wrap = el("div", "svg-wrap");
    wrap.appendChild(svg);
    return wrap;
  }

  function byNode(nodes, id) {
    for (var i = 0; i < (nodes || []).length; i += 1) {
      if (nodes[i].id === id) return nodes[i];
    }
    return null;
  }

  function renderTable(snapshot, highlight) {
    var table = el("table", "memo");
    var labels = snapshot.labels || [];
    var head = el("thead");
    var hr = el("tr");
    hr.appendChild(el("th", "", ""));
    labels.forEach(function (label) { hr.appendChild(el("th", "", label)); });
    head.appendChild(hr);
    table.appendChild(head);
    var body = el("tbody");
    (snapshot.matrix || []).forEach(function (row, r) {
      var tr = el("tr");
      tr.appendChild(el("th", "", (snapshot.row_labels && snapshot.row_labels[r]) || labels[r] || String(r)));
      row.forEach(function (cell, c) {
        var td = el("td", "cell", cell == null ? "∞" : String(cell));
        if (highlight.cell && highlight.cell[0] === r && highlight.cell[1] === c) {
          td.classList.add("is-on");
        }
        if (highlight.cell && labels[highlight.cell[0]] === snapshot.labels[r]) {
          /* floyd uses node ids in highlight.cell */
        }
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
    table.appendChild(body);
    return table;
  }

  function renderBigo(snapshot) {
    var series = snapshot.series || {};
    var names = Object.keys(series);
    var max = 1;
    names.forEach(function (name) {
      series[name].forEach(function (value) { max = Math.max(max, value); });
    });
    var colors = {
      "O(1)": "#0f766e",
      "O(log n)": "#1d4ed8",
      "O(n)": "#b45309",
      "O(n log n)": "#6d28d9",
      "O(n²)": "#b91c1c",
    };
    var svg = svgEl("svg", { viewBox: "0 0 640 280", width: "100%", height: "280" });
    svg.appendChild(svgEl("line", { x1: 40, y1: 250, x2: 620, y2: 250, stroke: "#a8a29e" }));
    svg.appendChild(svgEl("line", { x1: 40, y1: 20, x2: 40, y2: 250, stroke: "#a8a29e" }));
    names.forEach(function (name) {
      var values = series[name];
      var d = values.map(function (value, index) {
        var x = 40 + (index / Math.max(values.length - 1, 1)) * 560;
        var y = 250 - (value / max) * 220;
        return (index ? "L" : "M") + x + " " + y;
      }).join(" ");
      svg.appendChild(svgEl("path", { d: d, fill: "none", stroke: colors[name] || "#1c1917", "stroke-width": 2.4 }));
    });
    var legend = el("div", "queue-row");
    names.forEach(function (name) {
      var chip = el("span", "stack-item", name);
      chip.style.borderColor = colors[name] || "#1c1917";
      legend.appendChild(chip);
    });
    var wrap = el("div");
    wrap.appendChild(legend);
    var svgWrap = el("div", "svg-wrap");
    svgWrap.appendChild(svg);
    wrap.appendChild(svgWrap);
    return wrap;
  }

  function diffTree(nodes) {
    var out = [];
    var ident = 0;
    function walk(list, parent) {
      (list || []).forEach(function (node) {
        ident += 1;
        var id = ident;
        var item = {
          id: id,
          value: node.key,
          type: node.type,
          children: [],
        };
        out.push(item);
        if (parent) parent.children.push(id);
        if (node.children) walk(node.children, item);
      });
    }
    var root = { id: 0, value: "diff", type: "nested", children: [] };
    out.push(root);
    walk(nodes, root);
    return { kind: "tree", root: 0, nodes: out };
  }

  function renderGendiff(snapshot, highlight) {
    var wrap = el("div");
    var cols = el("div", "gendiff-layout");
    if (snapshot.left && Object.keys(snapshot.left).length) {
      cols.appendChild(el("pre", "", JSON.stringify(snapshot.left, null, 2)));
      cols.appendChild(el("pre", "", JSON.stringify(snapshot.right, null, 2)));
      wrap.appendChild(cols);
    }
    if (snapshot.path) wrap.appendChild(el("p", "muted", "Путь: " + snapshot.path));
    if (snapshot.stack && snapshot.stack.length) {
      wrap.appendChild(el("p", "", "Стек вызовов"));
      wrap.appendChild(renderStack({ items: snapshot.stack }, { head: [snapshot.stack.length - 1] }));
    }
    if (snapshot.tree) {
      wrap.appendChild(renderTree(diffTree(snapshot.tree), highlight));
    }
    return wrap;
  }

  function render(container, step) {
    container.innerHTML = "";
    if (!step || !step.snapshot) return;
    var snapshot = step.snapshot;
    var highlight = step.highlight || {};
    var builders = {
      array: renderArray,
      stack: renderStack,
      queue: renderQueue,
      list: renderList,
      hash: renderHash,
      tree: renderTree,
      graph: renderGraph,
      table: renderTable,
      bigo: renderBigo,
      gendiff: renderGendiff,
    };
    var builder = builders[snapshot.kind] || renderArray;
    container.appendChild(builder(snapshot, highlight));
  }

  window.DsaViz = { render: render };
})();
