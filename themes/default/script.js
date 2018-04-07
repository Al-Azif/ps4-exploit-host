function isInArray(value, array) {
  return array.indexOf(value) > -1;
}

function updatePage(title, header, buttons) {
  document.title = title + " | PS4 Exploit Host by Al-Azif";
  document.getElementById("title").innerHTML = title;
  document.getElementById("header").innerHTML = header;
  document.getElementById("buttons").innerHTML = buttons;
}

function resetPage() {
  history.pushState("", document.title, window.location.pathname + window.location.search);
  updatePage("Firmware Selection", "Firmware", firmwares);
}

function getFirmwares() {
  var firmwareSpoofs = {
    "5.05": "4.05",
    "5.51": "4.55"
  };
  var ua = navigator.userAgent;
  var currentFirmware = ua.substring(ua.indexOf("5.0 (") + 19, ua.indexOf(") Apple"));
  if (firmwareSpoofs.hasOwnProperty(currentFirmware)) {
    currentFirmware = firmwareSpoofs[currentFirmware];
  }
  var firmwares = "";
  x = 0;
  for (var i = 0, len = data["firmwares"].length; i < len; i++) {
    x += 1;
    if (currentFirmware == data["firmwares"][i]) {
      firmwares += "<a href=\"#" + data["firmwares"][i] + "\"><button class=\"btn btn-main\">" + data["firmwares"][i] + "</button></a>";
    } else {
      firmwares += "<a href=\"#" + data["firmwares"][i] + "\"><button class=\"btn btn-disabled\">" + data["firmwares"][i] + "</button></a>";
    }
    if (x >= 3) {
      firmwares += "<br>";
      x = 0;
    }
  }
  return firmwares;
}

function getExploits() {
  var hash = window.location.hash.substr(1);
  var exploits = "";
  x = 0;
  for (var i = 0, len = data[hash].length; i < len; i++) {
    x += 1;
    if (data[hash][i] == "[Back]") {
      exploits += "<a href=\"#back\"><button class=\"btn btn-main\">" + data[hash][i] + "</button></a>";
    } else {
      exploits += "<a href=\"" + exploitBase + hash + "/" + data[hash][i] + "/index.html\"><button class=\"btn btn-main\">" + data[hash][i] + "</button></a>";
    }
    if (x >= 3) {
      exploits += "<br>";
      x = 0;
    }
  }
  return exploits;
}

function firmwareSelected() {
  var hash = window.location.hash.substr(1);
  if (!isInArray(hash, firmwares)) {
    resetPage();
  } else {
    var exploits = getExploits();
    updatePage("Exploit Selection", hash, exploits);
  }
}
/*
Copyright (c) 2017-2018 Al Azif, https://github.com/Al-Azif/ps4-exploit-host

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/
