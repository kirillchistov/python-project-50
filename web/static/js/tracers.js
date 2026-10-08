(function () {
  function trace(algorithm, complexity, steps) {
    return { meta: { algorithm: algorithm, complexity: complexity }, steps: steps };
  }

  function step(message, snapshot, highlight) {
    return { message: message, snapshot: snapshot, highlight: highlight || {}, focus: {} };
  }

  function parseList(value, fallback) {
    if (value == null || value === "") return (fallback || []).slice();
    if (Array.isArray(value)) return value.map(coerce);
    return String(value).split(/[,;]/).map(function (part) { return part.trim(); }).filter(Boolean).map(coerce);
  }

  function coerce(item) {
    if (typeof item === "number" || typeof item === "boolean") return item;
    var text = String(item).trim();
    if (text === "true") return true;
    if (text === "false") return false;
    if (/^-?\d+$/.test(text)) return parseInt(text, 10);
    var asFloat = Number(text);
    return text !== "" && !isNaN(asFloat) ? asFloat : text;
  }

  function parseIntSafe(value, fallback) {
    if (value == null || value === "") return fallback;
    var number = parseInt(value, 10);
    return isNaN(number) ? fallback : number;
  }

  function arraySnap(items, extra) {
    var snapshot = { kind: "array", items: items.slice() };
    if (extra) Object.keys(extra).forEach(function (key) { snapshot[key] = extra[key]; });
    return snapshot;
  }

  function bigO(payload) {
    var n = Math.max(2, Math.min(parseIntSafe(payload.n, 24), 80));
    var xs = [];
    for (var i = 1; i <= n; i += 1) xs.push(i);
    var series = {
      "O(1)": xs.map(function () { return 1; }),
      "O(log n)": xs.map(function (x) { return Math.max(1, Math.floor(Math.log2(x))); }),
      "O(n)": xs.slice(),
      "O(n log n)": xs.map(function (x) { return Math.floor(x * Math.max(1, Math.log2(x))); }),
      "O(n²)": xs.map(function (x) { return x * x; }),
    };
    return trace("big_o", "зависит от класса", [step(
      "При n = " + n + " линейный проход — это " + series["O(n)"][n - 1] +
        " операций, а вложенный цикл уже " + series["O(n²)"][n - 1] + ".",
      { kind: "bigo", n: n, xs: xs, series: series }
    )]);
  }

  function linearSearch(payload) {
    var items = parseList(payload.array, [8, 3, 5, 1, 9, 2, 7, 4]);
    var target = coerce(payload.target != null ? payload.target : 5);
    var steps = [];
    var found = -1;
    for (var i = 0; i < items.length; i += 1) {
      var highlight = { comparing: [i] };
      if (items[i] === target) {
        found = i;
        highlight.found = [i];
        steps.push(step("Индекс " + i + ": " + items[i] + " совпал с целью.", arraySnap(items), highlight));
        break;
      }
      steps.push(step("Индекс " + i + ": " + items[i] + " ≠ " + target + ".", arraySnap(items), highlight));
    }
    if (found < 0) steps.push(step("Значения " + target + " нет. Худший случай: O(n).", arraySnap(items)));
    return trace("linear_search", "O(n) время, O(1) память", steps);
  }

  function binarySearch(payload) {
    var items = parseList(payload.array, [8, 3, 5, 1, 9, 2, 7, 4]).slice().sort(function (a, b) { return a - b; });
    var target = coerce(payload.target != null ? payload.target : 5);
    var steps = [step("Сначала сортируем: " + items.join(", ") + ".", arraySnap(items), { sorted: items.map(function (_, i) { return i; }) })];
    var lo = 0;
    var hi = items.length - 1;
    var found = -1;
    while (lo <= hi) {
      var mid = Math.floor((lo + hi) / 2);
      var highlight = { range: range(lo, hi), pivot: [mid] };
      if (items[mid] === target) {
        found = mid;
        highlight.found = [mid];
        steps.push(step("Середина [" + mid + "] = " + items[mid] + " — нашли.", arraySnap(items), highlight));
        break;
      }
      if (items[mid] < target) {
        steps.push(step(items[mid] + " < " + target + ", отбрасываем левую половину.", arraySnap(items), highlight));
        lo = mid + 1;
      } else {
        steps.push(step(items[mid] + " > " + target + ", отбрасываем правую половину.", arraySnap(items), highlight));
        hi = mid - 1;
      }
    }
    if (found < 0) steps.push(step(target + " нет в массиве.", arraySnap(items)));
    return trace("binary_search", "O(log n) время, O(1) память", steps);
  }

  function bubbleSort(payload) {
    var items = parseList(payload.array, [8, 3, 5, 1, 9, 2, 7, 4]);
    var steps = [];
    for (var end = items.length - 1; end > 0; end -= 1) {
      var swapped = false;
      for (var i = 0; i < end; i += 1) {
        var highlight = { comparing: [i, i + 1], sorted: range(end + 1, items.length - 1) };
        if (items[i] > items[i + 1]) {
          var tmp = items[i];
          items[i] = items[i + 1];
          items[i + 1] = tmp;
          swapped = true;
          highlight.swapping = [i, i + 1];
          steps.push(step(items[i + 1] + " > " + items[i] + " — меняем местами.", arraySnap(items), highlight));
        } else {
          steps.push(step(items[i] + " ≤ " + items[i + 1] + " — порядок верный.", arraySnap(items), highlight));
        }
      }
      if (!swapped) break;
    }
    steps.push(step("Готово.", arraySnap(items), { sorted: range(0, items.length - 1) }));
    return trace("bubble_sort", "O(n²) время, O(1) память", steps);
  }

  function insertionSort(payload) {
    var items = parseList(payload.array, [8, 3, 5, 1, 9, 2, 7, 4]);
    var steps = [step("Левая часть — уже разложенные карты.", arraySnap(items), items.length ? { sorted: [0] } : {})];
    for (var i = 1; i < items.length; i += 1) {
      var current = items[i];
      var cursor = i;
      steps.push(step("Берём карту " + current + ".", arraySnap(items), { pivot: [i], sorted: range(0, i - 1) }));
      while (cursor > 0 && items[cursor - 1] > current) {
        items[cursor] = items[cursor - 1];
        cursor -= 1;
        items[cursor] = current;
        steps.push(step("Сдвигаем вправо, чтобы освободить место.", arraySnap(items), { swapping: [cursor, cursor + 1], sorted: range(0, i) }));
      }
      items[cursor] = current;
    }
    steps.push(step("Все карты по возрастанию.", arraySnap(items), { sorted: range(0, items.length - 1) }));
    return trace("insertion_sort", "O(n²) время, O(1) память", steps);
  }

  function mergeSort(payload) {
    var items = parseList(payload.array, [8, 3, 5, 1, 9, 2, 7, 4]);
    var steps = [];
    function merge(lo, hi) {
      if (hi - lo <= 1) return;
      var mid = Math.floor((lo + hi) / 2);
      steps.push(step("Делим [" + lo + ":" + hi + "].", arraySnap(items, { ranges: [{ lo: lo, hi: hi - 1 }] }), { range: range(lo, hi - 1) }));
      merge(lo, mid);
      merge(mid, hi);
      var left = items.slice(lo, mid);
      var right = items.slice(mid, hi);
      var merged = [];
      while (left.length && right.length) merged.push(left[0] <= right[0] ? left.shift() : right.shift());
      merged = merged.concat(left, right);
      items.splice.apply(items, [lo, hi - lo].concat(merged));
      steps.push(step("Сливаем [" + lo + ":" + hi + "] → " + merged.join(", ") + ".", arraySnap(items), { sorted: range(lo, hi - 1) }));
    }
    merge(0, items.length);
    steps.push(step("Слияние собрало половины.", arraySnap(items), { sorted: range(0, items.length - 1) }));
    return trace("merge_sort", "O(n log n) время, O(n) память", steps);
  }

  function quickSort(payload) {
    var items = parseList(payload.array, [8, 3, 5, 1, 9, 2, 7, 4]);
    var steps = [];
    function sort(lo, hi) {
      if (lo >= hi) return;
      var pivot = items[hi];
      steps.push(step("Опора — " + pivot + ".", arraySnap(items), { pivot: [hi], range: range(lo, hi) }));
      var boundary = lo;
      for (var i = lo; i < hi; i += 1) {
        var highlight = { pivot: [hi], comparing: [i], range: range(lo, hi - 1) };
        if (items[i] <= pivot) {
          var tmp = items[boundary];
          items[boundary] = items[i];
          items[i] = tmp;
          highlight.swapping = [boundary, i];
          steps.push(step(items[boundary] + " ≤ опоры, влево на " + boundary + ".", arraySnap(items), highlight));
          boundary += 1;
        } else {
          steps.push(step(items[i] + " больше опоры, оставляем справа.", arraySnap(items), highlight));
        }
      }
      var swap = items[boundary];
      items[boundary] = items[hi];
      items[hi] = swap;
      steps.push(step("Опора встала на индекс " + boundary + ".", arraySnap(items), { found: [boundary] }));
      sort(lo, boundary - 1);
      sort(boundary + 1, hi);
    }
    sort(0, items.length - 1);
    steps.push(step("Массив отсортирован.", arraySnap(items), { sorted: range(0, items.length - 1) }));
    return trace("quick_sort", "в среднем O(n log n), память O(log n)", steps);
  }

  function range(from, to) {
    var out = [];
    for (var i = from; i <= to; i += 1) out.push(i);
    return out;
  }

  function splitOp(operation) {
    var text = String(operation);
    if (text.indexOf(":") >= 0) {
      var parts = text.split(":");
      return [parts[0].trim().toLowerCase(), parts.slice(1).join(":").trim()];
    }
    return [text.trim().toLowerCase(), ""];
  }

  function operations(payload, fallback) {
    var raw = payload.operations != null ? payload.operations : fallback;
    if (typeof raw === "string") return raw.split("\n").map(function (line) { return line.trim(); }).filter(Boolean);
    return raw.slice();
  }

  function stackTrace(payload) {
    var ops = operations(payload, ["push:заказ A", "push:заказ B", "push:заказ C", "pop", "push:заказ D"]);
    var items = [];
    var steps = [step("Стек — стопка тарелок (LIFO).", { kind: "stack", items: [] })];
    ops.forEach(function (operation) {
      var pair = splitOp(operation);
      if (pair[0] === "push") {
        items.push(pair[1]);
        steps.push(step("push(" + pair[1] + "): новая тарелка сверху.", { kind: "stack", items: items.slice() }, { head: [items.length - 1] }));
      } else if (pair[0] === "pop") {
        if (!items.length) {
          steps.push(step("pop() на пустом стеке.", { kind: "stack", items: [] }));
          return;
        }
        var taken = items.pop();
        steps.push(step("pop() → " + taken + ".", { kind: "stack", items: items.slice() }, items.length ? { head: [items.length - 1] } : {}));
      }
    });
    return trace("stack", "O(1) push/pop", steps);
  }

  function queueTrace(payload) {
    var ops = operations(payload, ["enqueue:Аня", "enqueue:Борис", "enqueue:Кира", "dequeue", "enqueue:Дима"]);
    var items = [];
    var steps = [step("Очередь в кассу (FIFO).", { kind: "queue", items: [] })];
    ops.forEach(function (operation) {
      var pair = splitOp(operation);
      if (pair[0] === "enqueue" || pair[0] === "push") {
        items.push(pair[1]);
        steps.push(step("enqueue(" + pair[1] + ").", { kind: "queue", items: items.slice() }, { tail: [items.length - 1] }));
      } else if (pair[0] === "dequeue" || pair[0] === "pop") {
        if (!items.length) {
          steps.push(step("dequeue() из пустой очереди.", { kind: "queue", items: [] }));
          return;
        }
        var taken = items.shift();
        steps.push(step("dequeue() → " + taken + ".", { kind: "queue", items: items.slice() }, items.length ? { head: [0] } : {}));
      }
    });
    return trace("queue", "O(1) enqueue, dequeue на deque", steps);
  }

  function linkedList(payload) {
    var values = parseList(payload.array, ["хост", "таймаут", "прокси"]);
    var nodes = [];
    var steps = [step("Односвязный список — вагоны.", { kind: "list", nodes: [] })];
    values.forEach(function (value, index) {
      if (nodes.length) nodes[nodes.length - 1].next = index;
      nodes.push({ id: index, value: value, next: null });
      steps.push(step("Прицепили вагон «" + value + "».", { kind: "list", nodes: nodes.map(copyNode) }, { head: [0], tail: [index] }));
    });
    if (nodes.length >= 2) {
      steps.push(step("Чтобы достать третий элемент, идём по цепочке: O(n).", { kind: "list", nodes: nodes.map(copyNode) }, { comparing: [0, 1, Math.min(2, nodes.length - 1)] }));
    }
    return trace("linked_list", "O(1) вставка с известным узлом, O(n) доступ", steps);
  }

  function copyNode(node) {
    return { id: node.id, value: node.value, next: node.next };
  }

  function hashTable(payload) {
    var keys = parseList(payload.array, ["host", "timeout", "proxy", "verbose", "follow"]);
    var bucketCount = 4;
    var buckets = [[], [], [], []];
    var steps = [step("Хеш-таблица — шкафчики: hash(ключ) mod 4.", { kind: "hash", buckets: [[], [], [], []] })];
    keys.forEach(function (key) {
      var index = hashKey(key, bucketCount);
      var collided = buckets[index].length > 0;
      buckets[index].push(key);
      steps.push(step(
        "Ключ «" + key + "» попал в ячейку " + index + "." + (collided ? " Коллизия: вешаем цепочку." : ""),
        { kind: "hash", buckets: buckets.map(function (bucket) { return bucket.slice(); }) },
        { bucket: [index] }
      ));
    });
    steps.push(step("Поиск host — в среднем O(1), как dict в gendiff.", { kind: "hash", buckets: buckets.map(function (bucket) { return bucket.slice(); }) }, { "found-key": ["host"] }));
    return trace("hash_table", "в среднем O(1) поиск/вставка", steps);
  }

  function hashKey(key, bucketCount) {
    var sum = 0;
    String(key).split("").forEach(function (char) { sum += char.charCodeAt(0); });
    return sum % bucketCount;
  }

  var DEFAULT_LEFT = { host: "hexlet.io", timeout: 50, proxy: "123.234.53.22", common: { setting: "on", doge: { wow: "" } } };
  var DEFAULT_RIGHT = { host: "hexlet.io", timeout: 20, verbose: true, common: { setting: "on", doge: { wow: "so much" } } };

  function asMapping(value, fallback) {
    if (value == null || value === "") return JSON.parse(JSON.stringify(fallback));
    if (typeof value === "object" && !Array.isArray(value)) return value;
    if (typeof value === "string") {
      var loaded = JSON.parse(value);
      if (!loaded || typeof loaded !== "object" || Array.isArray(loaded)) throw new Error("Ожидался JSON-объект");
      return loaded;
    }
    throw new Error("left/right должны быть объектами");
  }

  function isDict(value) {
    return value && typeof value === "object" && !Array.isArray(value);
  }

  function gendiffSnap(left, right, path, stack, tree) {
    return { kind: "gendiff", left: left, right: right, path: path, stack: stack.slice(), tree: JSON.parse(JSON.stringify(tree)) };
  }

  function nodeMessage(node, path) {
    var labels = {
      added: "появился только справа (+)",
      removed: "пропал справа (−)",
      changed: "значение изменилось",
      unchanged: "совпадает — оставляем как якорь",
      nested: "вложенный узел, дети уже собраны",
    };
    return "Ключ «" + path + "»: " + labels[node.type] + ".";
  }

  function silentBuild(data1, data2) {
    var keys = Object.keys(Object.assign({}, data1, data2)).sort();
    return keys.map(function (key) {
      var value1 = data1[key];
      var value2 = data2[key];
      if (!(key in data1)) return { key: key, type: "added", value: value2 };
      if (!(key in data2)) return { key: key, type: "removed", value: value1 };
      if (isDict(value1) && isDict(value2)) return { key: key, type: "nested", children: silentBuild(value1, value2) };
      if (value1 === value2) return { key: key, type: "unchanged", value: value1 };
      return { key: key, type: "changed", old_value: value1, new_value: value2 };
    });
  }

  function gendiffBuild(payload) {
    var left = asMapping(payload.left, DEFAULT_LEFT);
    var right = asMapping(payload.right, DEFAULT_RIGHT);
    var steps = [];
    var stack = [];
    function walk(data1, data2, path) {
      var frame = path || "корень";
      stack.push("build_diff(" + frame + ")");
      var keys = Object.keys(Object.assign({}, data1, data2)).sort();
      steps.push(step("Уровень «" + frame + "»: ключи → " + keys.join(", ") + ".", gendiffSnap(left, right, path, stack, []), { keys: keys }));
      var diff = [];
      keys.forEach(function (key) {
        var childPath = path ? path + "." + key : key;
        var node;
        if (!(key in data1)) node = { key: key, type: "added", value: data2[key] };
        else if (!(key in data2)) node = { key: key, type: "removed", value: data1[key] };
        else if (isDict(data1[key]) && isDict(data2[key])) {
          steps.push(step("И «" + childPath + "», и справа — словари. Ныряем глубже.", gendiffSnap(left, right, childPath, stack, []), { node_type: "nested", key: key }));
          node = { key: key, type: "nested", children: walk(data1[key], data2[key], childPath) };
        } else if (data1[key] === data2[key]) node = { key: key, type: "unchanged", value: data1[key] };
        else node = { key: key, type: "changed", old_value: data1[key], new_value: data2[key] };
        diff.push(node);
        steps.push(step(nodeMessage(node, childPath), gendiffSnap(left, right, childPath, stack, diff), { node_type: node.type, key: key }));
      });
      stack.pop();
      return diff;
    }
    var result = walk(left, right, "");
    steps.push(step("Дерево diff собрано.", gendiffSnap(left, right, "", stack, result), { done: true }));
    return trace("gendiff_build", "O(k log k) на уровень, память — дерево узлов", steps);
  }

  function stylishWalk(payload) {
    var left = asMapping(payload.left, DEFAULT_LEFT);
    var right = asMapping(payload.right, DEFAULT_RIGHT);
    var tree = silentBuild(left, right);
    var steps = [];
    var stack = [];
    function walk(nodes, depth) {
      nodes.forEach(function (node) {
        stack.push("walk(" + node.key + ")");
        steps.push(step("DFS: зашли в «" + node.key + "» (тип " + node.type + "), глубина " + depth + ".", {
          kind: "gendiff", tree: tree, stack: stack.slice(), path: node.key, left: {}, right: {}, focus_key: node.key,
        }, { node_type: node.type, key: node.key }));
        if (node.type === "nested") walk(node.children, depth + 1);
        stack.pop();
      });
    }
    walk(tree, 1);
    steps.push(step("Обход закончен: DFS pre-order, как format_stylish.", {
      kind: "gendiff", tree: tree, stack: [], path: "", left: left, right: right,
    }));
    return trace("stylish_walk", "O(n) по числу узлов дерева", steps);
  }

  function treeSnap(root) {
    var nodes = [];
    function walk(node) {
      if (!node) return null;
      nodes.push({
        id: node.id,
        value: node.key,
        left: node.left ? node.left.id : null,
        right: node.right ? node.right.id : null,
        balance: balance(node),
        height: node.height,
      });
      walk(node.left);
      walk(node.right);
      return node.id;
    }
    return { kind: "tree", root: walk(root), nodes: nodes };
  }

  function height(node) { return node ? node.height : 0; }
  function balance(node) { return node ? height(node.left) - height(node.right) : 0; }
  function updateHeight(node) { node.height = 1 + Math.max(height(node.left), height(node.right)); }

  function rotateLeft(z) {
    var y = z.right;
    z.right = y.left;
    y.left = z;
    updateHeight(z);
    updateHeight(y);
    return y;
  }

  function rotateRight(z) {
    var y = z.left;
    z.left = y.right;
    y.right = z;
    updateHeight(z);
    updateHeight(y);
    return y;
  }

  function bstTrace(payload) {
    var values = parseList(payload.array, [8, 3, 10, 1, 6, 14]);
    var target = coerce(payload.target != null ? payload.target : 6);
    var steps = [];
    var ident = 0;
    var holder = { root: null };
    function insert(node, key) {
      if (!node) {
        ident += 1;
        var created = { key: key, left: null, right: null, height: 1, id: ident };
        steps.push(step("Создаём лист " + key + ".", treeSnap(holder.root || created), { focus: [key] }));
        return created;
      }
      steps.push(step("Сравниваем " + key + " с " + node.key + ".", treeSnap(holder.root), { comparing: [node.key], focus: [key] }));
      if (key < node.key) node.left = insert(node.left, key);
      else if (key > node.key) node.right = insert(node.right, key);
      return node;
    }
    values.forEach(function (value) { holder.root = insert(holder.root, value); });
    steps.push(step("Дерево поиска построено.", treeSnap(holder.root)));
    var current = holder.root;
    while (current) {
      if (current.key === target) {
        steps.push(step("Нашли " + target + ".", treeSnap(holder.root), { found: [target] }));
        return trace("bst", "в среднем O(log n), худший O(n)", steps);
      }
      var goLeft = target < current.key;
      steps.push(step(target + (goLeft ? " < " : " > ") + current.key + " — идём " + (goLeft ? "влево" : "вправо") + ".", treeSnap(holder.root), { comparing: [current.key] }));
      current = goLeft ? current.left : current.right;
    }
    steps.push(step(target + " в дереве нет.", treeSnap(holder.root)));
    return trace("bst", "в среднем O(log n), худший O(n)", steps);
  }

  function avlInsert(payload) {
    var values = parseList(payload.array, [10, 20, 30, 40, 50, 25]);
    var steps = [];
    var ident = 0;
    var holder = { root: null };
    function insert(node, key) {
      if (!node) {
        ident += 1;
        return { key: key, left: null, right: null, height: 1, id: ident };
      }
      if (key < node.key) node.left = insert(node.left, key);
      else if (key > node.key) node.right = insert(node.right, key);
      else return node;
      updateHeight(node);
      var bal = balance(node);
      if (bal > 1 && key < node.left.key) {
        steps.push(step("Левый-левый у " + node.key + ": правый поворот.", treeSnap(holder.root), { pivot: [node.key] }));
        return rotateRight(node);
      }
      if (bal < -1 && key > node.right.key) {
        steps.push(step("Правый-правый у " + node.key + ": левый поворот.", treeSnap(holder.root), { pivot: [node.key] }));
        return rotateLeft(node);
      }
      if (bal > 1 && key > node.left.key) {
        steps.push(step("Левый-правый у " + node.key + ".", treeSnap(holder.root), { pivot: [node.key] }));
        node.left = rotateLeft(node.left);
        return rotateRight(node);
      }
      if (bal < -1 && key < node.right.key) {
        steps.push(step("Правый-левый у " + node.key + ".", treeSnap(holder.root), { pivot: [node.key] }));
        node.right = rotateRight(node.right);
        return rotateLeft(node);
      }
      return node;
    }
    values.forEach(function (value) {
      holder.root = insert(holder.root, value);
      steps.push(step("После вставки " + value + " дерево снова сбалансировано.", treeSnap(holder.root), { focus: [value] }));
    });
    return trace("avl_insert", "O(log n) вставка за счёт поворотов", steps);
  }

  var GRAPH_NODES = [
    { id: "A", label: "Сокол", x: 40, y: 40 },
    { id: "B", label: "Аэропорт", x: 200, y: 40 },
    { id: "C", label: "Динамо", x: 360, y: 40 },
    { id: "D", label: "Белорусская", x: 40, y: 180 },
    { id: "E", label: "Маяковская", x: 200, y: 180 },
    { id: "F", label: "Тверская", x: 360, y: 180 },
  ];
  var GRAPH_EDGES = [
    { source: "A", target: "B", weight: 2 },
    { source: "B", target: "C", weight: 3 },
    { source: "A", target: "D", weight: 1 },
    { source: "B", target: "E", weight: 4 },
    { source: "C", target: "F", weight: 2 },
    { source: "D", target: "E", weight: 2 },
    { source: "E", target: "F", weight: 1 },
  ];

  function graphLabel(id) {
    for (var i = 0; i < GRAPH_NODES.length; i += 1) {
      if (GRAPH_NODES[i].id === id) return GRAPH_NODES[i].label;
    }
    return id;
  }

  function adj() {
    var graph = {};
    GRAPH_NODES.forEach(function (node) { graph[node.id] = []; });
    GRAPH_EDGES.forEach(function (edge) {
      graph[edge.source].push([edge.target, edge.weight]);
      graph[edge.target].push([edge.source, edge.weight]);
    });
    return graph;
  }

  function graphSnap(visited, frontier, current, dist, prev) {
    return {
      kind: "graph",
      nodes: GRAPH_NODES,
      edges: GRAPH_EDGES,
      visited: visited,
      frontier: frontier,
      current: current,
      dist: dist || {},
      prev: prev || {},
    };
  }

  function bfsTrace(payload) {
    var start = payload.start || "A";
    var graph = adj();
    var queue = [start];
    var seen = {};
    seen[start] = true;
    var order = [];
    var steps = [step("BFS — обход волнами.", graphSnap([], [], start), { frontier: [start] })];
    while (queue.length) {
      var current = queue.shift();
      order.push(current);
      steps.push(step("Выходим на станции " + graphLabel(current) + ".", graphSnap(order.slice(), queue.slice(), current), { current: [current], visited: order.slice(), frontier: queue.slice() }));
      graph[current].forEach(function (pair) {
        if (!seen[pair[0]]) {
          seen[pair[0]] = true;
          queue.push(pair[0]);
          steps.push(step("Видим соседа " + graphLabel(pair[0]) + ", в очередь.", graphSnap(order.slice(), queue.slice(), current), { current: [current], visited: Object.keys(seen), frontier: queue.slice() }));
        }
      });
    }
    steps.push(step("Порядок: " + order.map(graphLabel).join(" → ") + ".", graphSnap(order, [], null), { visited: order }));
    return trace("bfs", "O(V + E) время", steps);
  }

  function dfsTrace(payload) {
    var start = payload.start || "A";
    var graph = adj();
    var order = [];
    var seen = {};
    var steps = [];
    function visit(node) {
      seen[node] = true;
      order.push(node);
      steps.push(step("DFS: ныряем в " + graphLabel(node) + ".", graphSnap(order.slice(), [], node), { current: [node], visited: order.slice() }));
      graph[node].forEach(function (pair) {
        if (!seen[pair[0]]) visit(pair[0]);
      });
    }
    visit(start);
    steps.push(step("Порядок DFS: " + order.map(graphLabel).join(" → ") + ".", graphSnap(order, [], null), { visited: order }));
    return trace("dfs", "O(V + E) время", steps);
  }

  function dijkstraTrace(payload) {
    var start = payload.start || "A";
    var graph = adj();
    var nodes = GRAPH_NODES.map(function (node) { return node.id; });
    var dist = {};
    var prev = {};
    var used = {};
    nodes.forEach(function (node) { dist[node] = Infinity; prev[node] = null; });
    dist[start] = 0;
    var steps = [step("Дейкстра: от " + graphLabel(start) + ".", graphSnap([], [], start, plainDist(dist)), { current: [start] })];
    nodes.forEach(function () {
      var current = null;
      var best = Infinity;
      nodes.forEach(function (node) {
        if (!used[node] && dist[node] < best) {
          best = dist[node];
          current = node;
        }
      });
      if (current == null || dist[current] === Infinity) return;
      used[current] = true;
      steps.push(step("Фиксируем " + graphLabel(current) + " с расстоянием " + dist[current] + ".", graphSnap(Object.keys(used), [], current, plainDist(dist)), { current: [current], visited: Object.keys(used) }));
      graph[current].forEach(function (pair) {
        var candidate = dist[current] + pair[1];
        if (candidate < dist[pair[0]]) {
          dist[pair[0]] = candidate;
          prev[pair[0]] = current;
          steps.push(step("Через " + graphLabel(current) + " до " + graphLabel(pair[0]) + " дешевле: " + candidate + ".", graphSnap(Object.keys(used), [], current, plainDist(dist)), { current: [current], focus: [pair[0]], visited: Object.keys(used) }));
        }
      });
    });
    steps.push(step("Кратчайшие расстояния посчитаны.", graphSnap(Object.keys(used), [], start, plainDist(dist), prev), { visited: Object.keys(used) }));
    return trace("dijkstra", "O((V + E) log V) с кучей", steps);
  }

  function plainDist(dist) {
    var out = {};
    Object.keys(dist).forEach(function (key) { out[key] = dist[key] === Infinity ? null : dist[key]; });
    return out;
  }

  function floydTrace() {
    var nodes = GRAPH_NODES.map(function (node) { return node.id; });
    var dist = {};
    nodes.forEach(function (src) {
      dist[src] = {};
      nodes.forEach(function (dst) { dist[src][dst] = src === dst ? 0 : Infinity; });
    });
    GRAPH_EDGES.forEach(function (edge) {
      dist[edge.source][edge.target] = edge.weight;
      dist[edge.target][edge.source] = edge.weight;
    });
    var steps = [step("Флойд — Уоршелл: все пары станций.", { kind: "table", matrix: matrix(dist, nodes), labels: nodes.map(graphLabel) })];
    nodes.forEach(function (mid) {
      nodes.forEach(function (src) {
        nodes.forEach(function (dst) {
          var via = dist[src][mid] + dist[mid][dst];
          if (via < dist[src][dst]) {
            dist[src][dst] = via;
            steps.push(step("Через " + graphLabel(mid) + " путь " + graphLabel(src) + " → " + graphLabel(dst) + " стал " + via + ".", {
              kind: "table", matrix: matrix(dist, nodes), labels: nodes.map(graphLabel),
            }, { cell: [nodes.indexOf(src), nodes.indexOf(dst)], via: mid }));
          }
        });
      });
    });
    steps.push(step("Матрица заполнена.", { kind: "table", matrix: matrix(dist, nodes), labels: nodes.map(graphLabel) }));
    return trace("floyd", "O(V³) время, O(V²) память", steps);
  }

  function matrix(dist, nodes) {
    return nodes.map(function (src) {
      return nodes.map(function (dst) { return dist[src][dst] === Infinity ? null : dist[src][dst]; });
    });
  }

  function greedyCoins(payload) {
    var coins = parseList(payload.array, [1, 3, 4]).slice().sort(function (a, b) { return b - a; });
    var amount = parseIntSafe(payload.amount, 6);
    var left = amount;
    var taken = [];
    var steps = [step("Жадный алгоритм берёт самую крупную монету.", coinsSnap(coins, taken, left))];
    coins.forEach(function (coin) {
      while (left >= coin) {
        taken.push(coin);
        left -= coin;
        steps.push(step("Берём " + coin + ", осталось " + left + ".", coinsSnap(coins, taken, left), { focus: [coin] }));
      }
    });
    steps.push(step(left ? "Не удалось набрать сумму." : "Набрали " + taken.length + " монетами: " + taken.join(", ") + ".", coinsSnap(coins, taken, left)));
    return trace("coin_change_greedy", "O(k) по номиналам", steps);
  }

  function dpCoins(payload) {
    var coins = parseList(payload.array, [1, 3, 4]).slice().sort(function (a, b) { return a - b; });
    var amount = parseIntSafe(payload.amount, 6);
    var inf = amount + 1;
    var table = [];
    var choice = [];
    var i;
    for (i = 0; i <= amount; i += 1) { table.push(inf); choice.push(null); }
    table[0] = 0;
    var steps = [step("DP: dp[x] — минимум монет для суммы x.", { kind: "table", matrix: [table.slice()], labels: labels(amount), row_labels: ["dp"] })];
    for (var current = 1; current <= amount; current += 1) {
      coins.forEach(function (coin) {
        if (coin > current) return;
        var candidate = table[current - coin] + 1;
        if (candidate < table[current]) {
          table[current] = candidate;
          choice[current] = coin;
          steps.push(step("Для суммы " + current + " монета " + coin + " даёт " + candidate + " шт.", {
            kind: "table", matrix: [table.slice()], labels: labels(amount), row_labels: ["dp"],
          }, { cell: [0, current] }));
        }
      });
    }
    var used = [];
    var cursor = amount;
    while (cursor > 0 && choice[cursor] != null) {
      used.push(choice[cursor]);
      cursor -= choice[cursor];
    }
    steps.push(step("Оптимум для " + amount + ": " + table[amount] + " монет " + used.join(", ") + ".", {
      kind: "table", matrix: [table.slice()], labels: labels(amount), row_labels: ["dp"],
    }, { cell: [0, amount] }));
    return trace("coin_change_dp", "O(amount × k) время, O(amount) память", steps);
  }

  function labels(amount) {
    var out = [];
    for (var i = 0; i <= amount; i += 1) out.push(String(i));
    return out;
  }

  function coinsSnap(coins, taken, left) {
    return { kind: "array", items: taken.length ? taken.slice() : ["—"], caption: "номиналы " + coins.join(", ") + ", остаток " + left };
  }

  var ALGORITHMS = {
    big_o: bigO,
    linear_search: linearSearch,
    binary_search: binarySearch,
    bubble_sort: bubbleSort,
    insertion_sort: insertionSort,
    merge_sort: mergeSort,
    quick_sort: quickSort,
    stack: stackTrace,
    queue: queueTrace,
    hash_table: hashTable,
    linked_list: linkedList,
    bst: bstTrace,
    avl_insert: avlInsert,
    bfs: bfsTrace,
    dfs: dfsTrace,
    dijkstra: dijkstraTrace,
    floyd: floydTrace,
    coin_change_greedy: greedyCoins,
    coin_change_dp: dpCoins,
    gendiff_build: gendiffBuild,
    stylish_walk: stylishWalk,
  };

  window.DsaTracers = {
    run: function (algorithm, payload) {
      if (!ALGORITHMS[algorithm]) throw new Error("Неизвестный алгоритм: " + algorithm);
      return ALGORITHMS[algorithm](payload || {});
    },
  };
})();
