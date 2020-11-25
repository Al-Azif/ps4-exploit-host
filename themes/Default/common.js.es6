function getBasePath() {
  // const port = window.location.port !== '' ? `:${window.location.port}` : '';
  // let url = `${window.location.origin}${port}${window.location.pathname}`;
  let url = `${window.location.origin}${window.location.pathname}`;

  if (url.slice(-1) === '/') {
    url = url.slice(0, -1);
  }

  return url;
}

// --- JS Error Logger --------------------------------------------------------

window.onerror = (msg, errorLocation, lineNo, columnNo, error) => {
  if (errorLocation === document.location.href) {
    // eslint-disable-next-line no-alert
    alert(`User Custom JS Error\n\n${msg}\nLine: ${lineNo}\nColumn: ${columnNo}`);
    return; // Assuming this is a user script error
  }
  const data = JSON.stringify({
    message: msg,
    line: lineNo,
    column: columnNo,
    url: errorLocation,
    useragent: navigator.userAgent,
    stack: error,
  });

  const xhr = new XMLHttpRequest();
  xhr.open('POST', `${getBasePath()}/debug/jserrorlog`, true);
  xhr.setRequestHeader('Content-Type', 'application/json');

  if (navigator.onLine) {
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 400) {
        // eslint-disable-next-line no-alert
        alert(`Successfully Submitted Error Log\n\n${msg}\nFile: ${errorLocation}\nLine: ${lineNo}\nColumn: ${columnNo}`);
      } else {
        // eslint-disable-next-line no-alert
        alert(`Error Submitting Error Log\n\n${msg}\nFile: ${errorLocation}\nLine: ${lineNo}\nColumn: ${columnNo}`);
      }
    };

    xhr.onerror = () => {
      // eslint-disable-next-line no-alert
      alert(`Error Submitting Error Log\n\n${msg}\nFile: ${errorLocation}\nLine: ${lineNo}\nColumn: ${columnNo}`);
    };
  } else {
    // eslint-disable-next-line no-alert
    alert(`Offline, No Error Log Submitted\n\n${msg}\nFile: ${errorLocation}\nLine: ${lineNo}\nColumn: ${columnNo}`);
  }

  xhr.send(data);
};

// --- Common Functions -------------------------------------------------------

function int2Hex(value) {
  return value.toString(16);
}

// eslint-disable-next-line no-unused-vars
function uuid() {
  let random;
  let i;

  let result = '';
  let seed = Date.now();

  for (i = 0; i < 32; i += 1) {
    // eslint-disable-next-line no-bitwise
    random = (seed + Math.random() * 16) % 16 | 0;
    seed = Math.floor(seed / 16);

    if (i === 8 || i === 12 || i === 16 || i === 20) {
      result += '-';
    }

    if (i === 12) {
      result += int2Hex(4);
    } else if (i === 16) {
      // eslint-disable-next-line no-bitwise
      result += int2Hex(random & (3 | 8));
    } else {
      result += int2Hex(random);
    }
  }
  return result;
}

// eslint-disable-next-line no-unused-vars
function sleep(time) {
  return new Promise((resolve) => { setTimeout(resolve, time); });
}

function getJson(inputURL) {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', inputURL, false);
  xhr.setRequestHeader('Content-Type', 'application/json');

  xhr.send();
  if (xhr.readyState === 4 && xhr.status >= 200 && xhr.status < 400) {
    return JSON.parse(xhr.responseText);
  }

  return false;
}

function getJsonAsync(inputURL, callback) {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', inputURL, true);
  xhr.setRequestHeader('Content-Type', 'application/json');

  xhr.onload = () => {
    if (xhr.status >= 200 && xhr.status < 400) {
      callback(JSON.parse(xhr.responseText));
    } else {
      callback(false);
    }
  };

  xhr.onerror = () => {
    callback(false);
  };

  xhr.send();
}

// eslint-disable-next-line no-unused-vars
function getMenu() {
  const url = `${getBasePath()}/api/menu`;
  const result = getJson(url);

  if (result !== undefined && Object.keys(result).length > 0) {
    return result;
  }
  return false;
}

// eslint-disable-next-line no-unused-vars
function getMenuAsync(callback) {
  const url = `${getBasePath()}/api/menu`;

  getJsonAsync(url, (response) => {
    if (response && response !== {}) {
      callback(response);
    } else {
      callback(false);
    }
  });
}

// eslint-disable-next-line no-unused-vars
function getSettings() {
  const url = `${getBasePath()}/api/themes`;
  const result = getJson(url);

  if (result !== undefined && Object.keys(result).length > 0) {
    return result;
  }
  return false;
}

// eslint-disable-next-line no-unused-vars
function getSettingsAsync(callback) {
  const url = `${getBasePath()}/api/themes`;

  getJsonAsync(url, (response) => {
    if (response && response !== {}) {
      callback(response);
    } else {
      callback(false);
    }
  });
}

// eslint-disable-next-line no-unused-vars
function getData(inputURL, cors) {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', cors ? `https://cors.plus/${inputURL}` : inputURL, false);

  xhr.send();
  if (xhr.readyState === 4 && xhr.status >= 200 && xhr.status < 400) {
    return xhr.responseText;
  }

  return false;
}

// eslint-disable-next-line no-unused-vars
function getDataAsync(inputURL, callback, cors) {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', cors ? `https://cors.plus/${inputURL}` : inputURL, true);

  xhr.onload = () => {
    if (xhr.status >= 200 && xhr.status < 400) {
      callback(xhr.responseText);
    } else {
      callback(false);
    }
  };

  xhr.onerror = () => {
    callback(false);
  };

  xhr.send();
}

function loadFrame(url) {
  const ifrObj = document.getElementById('ifr');

  if (ifrObj !== undefined) {
    ifrObj.contentWindow.location.replace(url);
  }
}

// eslint-disable-next-line no-unused-vars
function loadEntry(category, entry, redirect) {
  if (redirect) {
    window.location.href = `${getBasePath()}/exploits/${category}/${entry}/index.html`;
  } else {
    loadFrame(`${getBasePath()}/exploits/${category}/${entry}/index.html`);
  }
}

function clearFrame() {
  loadFrame(`${getBasePath()}/blank.html`);
}

// eslint-disable-next-line no-unused-vars
function safeRedirect(url) {
  clearFrame();

  document.getElementById('ifr').addEventListener('load', () => {
    window.location.href = url;
  });
}

// eslint-disable-next-line no-unused-vars
function cacheTheme() {
  loadFrame(`${getBasePath()}/cache/theme/index.html`);
}

// eslint-disable-next-line no-unused-vars
function cacheCategory(category) {
  loadFrame(`${getBasePath()}/cache/category/${category}/index.html`);
}

// eslint-disable-next-line no-unused-vars
function cacheEntry(category, entry) {
  loadFrame(`${getBasePath()}/cache/entry/${category}/${entry}/index.html`);
}

// eslint-disable-next-line no-unused-vars
function cacheAll() {
  loadFrame(`${getBasePath()}/cache/all/index.html`);
}

// eslint-disable-next-line no-unused-vars
function setStorage(key, value, datatype) {
  if (typeof datatype === 'string') {
    // Don't need to lint for valid-typeof on next line as we solved the issue above
    // eslint-disable-next-line valid-typeof
    if (typeof value === datatype) {
      localStorage.setItem(key, value);
      return true;
    }
  }
  return false;
}

// eslint-disable-next-line no-unused-vars
function getStorage(key) {
  if (localStorage.getItem(key) !== null) {
    return localStorage.getItem(key);
  }
  return false;
}

// eslint-disable-next-line no-unused-vars
function deleteStorage(key) {
  localStorage.removeItem(key);
}

function setCookie(key, value, days) {
  let expires = '';
  if (days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = `; expires=${date.toUTCString()}`;
  }

  document.cookie = `${key}=${encodeURIComponent(value)}${expires}; domain=${window.location.hostname}; path=${window.location.pathname};`;
}

function deleteCookie(key) {
  document.cookie = `${key}=; expires=Thu, 01 Jan 1970 00:00:00 UTC;`;
}

function getCookie(key) {
  const name = `${key}=`;
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookies = decodedCookie.split(';');

  for (let i = 0; i < cookies.length; i += 1) {
    let cookie = cookies[i];

    while (cookie.charAt(0) === ' ') {
      cookie = cookie.substring(1);
    }
    if (cookie.indexOf(name) === 0) {
      return decodeURI(cookie.substring(name.length, cookie.length));
    }
  }

  return undefined;
}

// eslint-disable-next-line no-unused-vars
function setAutoload(category, entry) {
  setCookie('autoload', `${category}/${entry}`, 100 * 365);
}

// eslint-disable-next-line no-unused-vars
function autoloadCookie(menu) {
  const autoload = getCookie('autoload');

  if (autoload) {
    try {
      const category = autoload.split('/')[0];
      const entry = autoload.split('/')[1];

      if (!(category in menu) || !(entry in menu[category].entries)) {
        deleteCookie('autoload');
      } else {
        return autoload;
      }
    } catch (e) {
      deleteCookie('autoload');
    }
  }
  return false;
}

// eslint-disable-next-line no-unused-vars
function imageToBackground(inputURL, callback, cors, outputFormat) {
  const img = new Image();
  img.crossOrigin = 'Anonymous';
  img.onload = function onImageLoad() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.height = this.naturalHeight;
    canvas.width = this.naturalWidth;
    ctx.drawImage(this, 0, 0);
    const dataURL = canvas.toDataURL(outputFormat);
    callback(dataURL);
  };
  img.src = cors ? `https://cors.plus/${inputURL}` : inputURL;
}

// eslint-disable-next-line no-unused-vars
function checkUAMatch(validUAs) {
  const currentUA = navigator.userAgent;

  if (validUAs.indexOf(currentUA) > -1) {
    return true;
  }

  for (let i = 0; i < validUAs.length; i += 1) {
    const pattern = new RegExp(validUAs[i]);
    if (pattern.test(currentUA)) {
      return true;
    }
  }

  return false;
}
/*
Copyright (c) 2017-2020 Al Azif, https://github.com/Al-Azif/ps4-exploit-host

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
