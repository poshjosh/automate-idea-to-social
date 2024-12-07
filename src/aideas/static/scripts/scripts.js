function Aideas() { }

Aideas.prototype.toggle_display = function (selector, flip = 'none', flop = 'block') {
  const element = document.querySelector(selector);
  if (element.style.display !== flip) {
    element.style.display = flip;
  } else {
    element.style.display = flop;
  }
}

Aideas.prototype.toggle_text = function (selector, flip, flop) {
  const element = document.querySelector(selector);
  if (element.innerText !== flip) {
    element.innerText = flip;
  } else {
    element.innerText = flop
  }
  if (element.value !== flip) {
    element.value = flip;
  } else {
    element.value = flop
  }
}

const aideas = new Aideas();
