// --- Theme Functions --------------------------------------------------------

function myAlert(type, message, wait) {
  let safeWait;

  const alertID = `alert-${uuid()}`;
  let alertString = `<div class="alert alert-${type} alert-dismissible fade collapse" id="${alertID}" role="alert">`;

  if (wait === undefined) {
    safeWait = 3000;
  } else {
    safeWait = wait;
  }
  alertString += message;
  alertString += '<button type="button" class="close" data-dismiss="alert">';
  alertString += '<span>&times;</span>';
  alertString += '</button>';
  alertString += '</div>';
  $('#alert-box').append(alertString);
  $(`#${alertID}`).collapse('show');
  // TODO: Alert systems to show multiple alerts that shift up when closed
  // Calculate top
  // $(`#alert-${randomID}`).css('top', ($('.alert').length));
  if (safeWait !== 0) {
    sleep(safeWait).then(() => {
      $(`#${alertID}`).alert('close');
      // TODO: Shift remaining alerts up
    });
  }
}

function newsAlert() {
  getJsonAsync(`${getBasePath()}/news.json`, (response) => {
    if (response) {
      const news = response;
      const date = getCookie('newsDate');
      if (news !== undefined && (date === undefined || news.Date > date)
        && news.Message !== undefined && news.Severity !== undefined) {
        if (autoloadCookie(window.Menu)) {
          // Alert will pause execution on the autoload redirect allowing users to see new news
          // eslint-disable-next-line no-alert
          alert(news.Message);
          setCookie('newsDate', news.Date, 30);
        } else {
          myAlert(`${news.Severity} alert-news`, news.Message, 0);
          $('.alert-news [data-dismiss="alert"]').on('click', () => {
            setCookie('newsDate', news.Date, 30);
          });
        }
      }
    }
  });
}

function buildHTML() {
  let htmlString = '';
  let buttonCount = 0;

  if ($.isEmptyObject(window.Menu)) {
    htmlString += '<div class="btn-group">';
    htmlString += '<button class="btn btn-primary btn-custom-main btn-custom-full">No Categories Found</button>';
    htmlString += '</div>';
    $('#buttons').html(htmlString);
    return;
  }

  if ('error' in window.Menu && window.Menu.error === true && 'message' in window.Menu) {
    htmlString += '<div class="btn-group">';
    htmlString += `<button class="btn btn-primary btn-custom-main btn-custom-full">${window.Menu.message}</button>`;
    htmlString += '</div>';
    $('#buttons').html(htmlString);
    return;
  }

  if (window.Menu !== undefined) {
    htmlString += '<div id="category-buttons">';
    $.each(window.Menu, (i, field) => {
      htmlString += '<div class="btn-group">';
      htmlString += `<button class="btn btn-primary btn-custom-main category-button" data-category="${field.title}">${field.title}</button>`;
      htmlString += '<button type="button" class="btn btn-primary btn-custom-dropdown dropdown-toggle dropdown-toggle-split" data-toggle="dropdown"></button>';
      htmlString += '<div class="dropdown-menu">';
      htmlString += `<a class="dropdown-item about-button" href="javascript:void(0)" data-category="${field.title}">About</a>`;
      if (navigator.onLine && field.offline) {
        htmlString += '<div class="dropdown-divider"></div>';
        htmlString += `<a class="dropdown-item cache-button" href="javascript:void(0)" data-category="${field.title}">Cache</a>`;
      }
      htmlString += '</div>';
      htmlString += '</div>';
      buttonCount += 1;
      if (buttonCount % 3 === 0) {
        htmlString += '<br>';
      }
    });
    if (navigator.onLine) {
      htmlString += '<div class="btn-group">';
      htmlString += '<button class="btn btn-primary btn-custom-main btn-custom-full cache-all-button">[Cache All]</button>';
      htmlString += '</div>';
    }
    htmlString += '</div>';
    buttonCount = 0;

    $.each(window.Menu, (i, field) => {
      htmlString += `<div class="category-page" data-category="${field.title}">`;
      if ('error' in field.entries && field.entries.error === true && 'message' in field.entries) {
        htmlString += '<div class="btn-group">';
        htmlString += `<button class="btn btn-primary btn-custom-main btn-custom-full">${field.entries.message}</button>`;
        htmlString += '</div>';
      } else {
        $.each(field.entries, (j, entry) => {
          htmlString += '<div class="btn-group">';
          htmlString += `<button class="btn btn-primary btn-custom-main entry-button" data-category="${field.title}" data-entry="${entry.title}">${entry.title}</button>`;
          htmlString += '<button type="button" class="btn btn-primary btn-custom-dropdown dropdown-toggle dropdown-toggle-split" data-toggle="dropdown"></button>';
          htmlString += '<div class="dropdown-menu">';
          htmlString += `<a class="dropdown-item about-button" href="javascript:void(0)" data-category="${field.title}" data-entry="${entry.title}">About</a>`;
          htmlString += `<a class="dropdown-item autoload-button" href="javascript:void(0)" data-category="${field.title}" data-entry="${entry.title}">Autoload</a>`;
          if (navigator.onLine && field.offline) {
            htmlString += '<div class="dropdown-divider"></div>';
            htmlString += `<a class="dropdown-item cache-button" href="javascript:void(0)" data-category="${field.title}" data-entry="${entry.title}">Cache</a>`;
          }
          htmlString += '</div>';
          htmlString += '</div>';
          buttonCount += 1;
          if (buttonCount % 3 === 0) {
            htmlString += '<br>';
          }
        });
        if (navigator.onLine && field.offline) {
          htmlString += '<div class="btn-group">';
          htmlString += `<button class="btn btn-primary btn-custom-main btn-custom-full cache-all-button" data-category="${field.title}">[Cache All]</button>`;
          htmlString += '</div>';
          buttonCount += 1;
          if (buttonCount % 3 === 0) {
            htmlString += '<br>';
          }
        }
        if (window.Failsafe) {
          htmlString += '<div class="btn-group">';
          htmlString += '<button class="btn btn-primary btn-custom-main btn-custom-full back-button">[Back]</button>';
          htmlString += '</div>';
        }
        htmlString += '</div>';
        buttonCount = 0;
      }
    });
  }

  $('#buttons').html(htmlString);
}

function clearOverlays() {
  $('#cache-overlay').hide();
  $('#bar-text').hide();
  $('#bar-back').hide();
  $('#bar-load').hide();
  $('#bar-load').html('');
  $('#bar-load').width('0%');
  $('#exploit-overlay').hide();
  $('#exploit-message').hide();
  $('#exploit-message').html('');
  $('#exploit-loader').hide();
}

function showCaching() {
  $('#cache-overlay').show();
  $('#bar-text').show();
  $('#bar-back').show();
  $('#bar-load').show();
}

function showLoader() {
  $('#exploit-overlay').show();
  $('#exploit-loader').show();
  $('#exploit-message').show();
}

// eslint-disable-next-line no-unused-vars
function exploitDone(message) {
  $('#exploit-loader').hide();
  $('#exploit-message').html(message);
  const pattern = /^https?:\/\/.*\/exploits\/(.*)\/(.*)\/index.html$/;
  const match = pattern.exec($('#ifr')[0].contentDocument.URL);
  const category = decodeURIComponent(match[1]);
  const entry = decodeURIComponent(match[2]);

  if (window.Menu[category].entries[entry].reload === true) {
    sleep(3000).then(() => {
      clearFrame();
      clearOverlays();
    });
  }
}

function displayHome() {
  $(document).prop('title', 'Category Selection | Exploit Host by Al Azif');
  window.history.replaceState({ location: '', modal: false }, null, ' ');

  $('#title').text('Category Selection');
  $('#header').text('Categories');

  $('.category-page').hide();
  $('#category-buttons').show();
}

function displayCategory(category) {
  $(document).prop('title', 'Exploit Selection | Exploit Host by Al Azif');
  window.history.pushState({ location: category, modal: false }, null, `#${category}`);

  $('#title').text('Exploit Selection');
  $('#header').text(category);

  $('#category-buttons').hide();
  $('.category-page').hide();

  $('.category-page').each((i, field) => {
    if (String($(field).data('category')) === String(category)) {
      $(field).show();
    }
  });
}

function exploitLoader(category, entry) {
  showLoader();
  loadEntry(category, entry, window.Menu[category].entries[entry].redirect);
}

function triggerAutoload(category, entry, cached) {
  if (cached === undefined && category && entry) {
    setAutoload(category, entry);
  }

  const autoload = autoloadCookie(window.Menu);
  if (autoload) {
    const autoloadCategory = autoload.split('/')[0];
    const autoloadEntry = autoload.split('/')[1];

    if (!navigator.onLine && (!window.Menu[autoloadCategory].offline
      || !window.Menu[autoloadCategory].entries[autoloadEntry].offline)) {
      myAlert('danger', 'Could not autoload, payload is online only (Currently offline)');
    } else if (navigator.onLine && !cached && window.Menu[autoloadCategory].offline
      && window.Menu[autoloadCategory].entries[autoloadEntry].offline) {
      cacheEntry(autoloadCategory, autoloadEntry);
    } else {
      exploitLoader(autoloadCategory, autoloadEntry);
    }
  }
}

function addCacheStatus(type, category, entry) {
  // Unsure if the recursive option is better, looks better, but performance is
  // unknown because of ths repeating localStorage access vs all at once
  let categoryKeys = [];
  let entryKeys = [];
  const cacheStatusChanges = {};

  if (!getStorage('cache-status')) {
    setStorage('cache-status', '{}', 'string');
  }

  const existingCacheStatus = JSON.parse(getStorage('cache-status'));

  if (type === 'all') {
    categoryKeys = Object.keys(window.Menu);
    for (let i = 0; i < categoryKeys.length; i += 1) {
      // Recursive Option:
      //   addCacheStatus('category', categoryKeys[i], undefined)
      entryKeys = Object.keys(window.Menu[categoryKeys[i]].entries);
      for (let j = 0; j < entryKeys.length; j += 1) {
        $.extend(true, cacheStatusChanges, {
          [categoryKeys[i]]: {
            [window.Menu[categoryKeys[i]].entries[entryKeys[j]].title]: new Date().toISOString(),
          },
        });
      }
    }
    setStorage('cache-status', JSON.stringify($.extend({}, existingCacheStatus, cacheStatusChanges)), 'string');
  } else if (type === 'category') {
    entryKeys = Object.keys(window.Menu[category].entries);
    for (let i = 0; i < entryKeys.length; i += 1) {
      // Recursive Option:
      //   addCacheStatus('entry', category, window.Menu[category].entries[entryKeys[i]].title);
      $.extend(true, cacheStatusChanges, {
        [category]: {
          [window.Menu[category].entries[entryKeys[i]].title]: new Date().toISOString(),
        },
      });
    }
    setStorage('cache-status', JSON.stringify($.extend(true, {}, existingCacheStatus, cacheStatusChanges)), 'string');
  } else if (type === 'entry') {
    setStorage('cache-status', JSON.stringify($.extend(true, {}, existingCacheStatus, {
      [category]: {
        [entry]: new Date().toISOString(),
      },
    })), 'string');
  }
}

function removeCacheStatus(type, category, entry) {
  if (!navigator.onLine) {
    return;
  }

  if (!getStorage('cache-status')) {
    setStorage('cache-status', '{}', 'string');
    return;
  }

  const existingCacheStatus = JSON.parse(getStorage('cache-status'));

  if (type === 'all') {
    setStorage('cache-status', '{}', 'string');
  } else if (type === 'category') {
    delete existingCacheStatus[category];
    setStorage('cache-status', JSON.stringify(existingCacheStatus), 'string');
  } else if (type === 'entry') {
    delete existingCacheStatus[category][entry];
    setStorage('cache-status', JSON.stringify(existingCacheStatus), 'string');
  }
}

// eslint-disable-next-line no-unused-vars
function cacheInterface(callback) {
  let matches;
  let categoryMatch;
  let entryMatch;

  if (callback === 'ondownloading') {
    $('#bar-text').html('Caching...');
    showCaching();
  } else if (callback === 'ondownloading-theme') {
    $('#bar-text').html('Caching Theme...');
    showCaching();
  } else {
    const iFrameURL = String($('#ifr')[0].contentDocument.URL);
    const typePattern = /\/cache\/(theme|category|entry|all)\/.*index\.html$/;
    const categoryPattern = /\/cache\/category\/(.*)\/index\.html$/;
    const entryPattern = /\/cache\/entry\/(.*)\/(.*)\/index\.html$/;
    const typeMatch = typePattern.exec(iFrameURL);
    if (typeMatch[1] === 'category') {
      matches = categoryPattern.exec(iFrameURL);
      categoryMatch = decodeURIComponent(matches[1]);
    } else if (typeMatch[1] === 'entry') {
      matches = entryPattern.exec(iFrameURL);
      categoryMatch = decodeURIComponent(matches[1]);
      entryMatch = decodeURIComponent(matches[2]);
    }

    clearFrame();
    clearOverlays();
    if (callback === 'oncached') {
      myAlert('success', 'Cached Successfully');
      addCacheStatus(typeMatch[1], categoryMatch, entryMatch);
      triggerAutoload(undefined, undefined, true);
    } else if (callback === 'onupdateready') {
      myAlert('success', 'Cache updated');
      addCacheStatus(typeMatch[1], categoryMatch, entryMatch);
      triggerAutoload(undefined, undefined, true);
    } else if (callback === 'onnoupdate') {
      myAlert('primary', 'No update available');
      addCacheStatus(typeMatch[1], categoryMatch, entryMatch);
      triggerAutoload(undefined, undefined, true);
    } else if (callback === 'onerror') {
      myAlert('danger', 'Error caching resources');
      removeCacheStatus(typeMatch[1], categoryMatch, entryMatch);
      triggerAutoload(undefined, undefined, true);
    } else if (callback === 'onobsolete') {
      myAlert('danger', 'Manifest returned a 404, cache was deleted');
      removeCacheStatus(typeMatch[1], categoryMatch, entryMatch);
      triggerAutoload(undefined, undefined, true);
    } else if (callback === 'oncached-theme' || callback === 'onnoupdate-theme') {
      /* Purposely Left Blank */
    } else if (callback === 'onupdateready-theme') {
      deleteCookie('newsDate');
      window.location.reload(true);
    } else if (callback === 'onerror-theme') {
      myAlert('danger', 'Error caching theme resources');
    } else if (callback === 'onobsolete-theme') {
      myAlert('danger', 'Manifest returned a 404, theme cache was deleted');
    } else if (callback === 'onerror-appcache') {
      myAlert('danger', 'Browser does not support AppCache, nothing was cached');
      removeCacheStatus('all', undefined, undefined);
      triggerAutoload(undefined, undefined, true);
    }
  }
}

// eslint-disable-next-line no-unused-vars
function cacheProgress(percent) {
  $('#bar-load').width(`${percent}%`);
  $('#bar-load').html(`${percent}%`);
}

function categoryMeta(category) {
  let lang;
  let modalBody;
  let notes;
  const meta = window.Menu[category];

  if (typeof meta === 'undefined') {
    myAlert('danger', 'Unable to retrieve metadata');
    return;
  }

  $.extend(true, {
    title: '',
    device: '',
    firmware: '',
    user_agents: '',
    notes: {
      default: '',
    },
  }, meta);

  const uaMatch = checkUAMatch(meta.user_agents) ? '<span class="badge badge-success">Match</span>' : '<span class="badge badge-danger">Mismatch</span>';

  lang = getCookie('language');
  if (typeof lang !== 'string') {
    setCookie('language', 'default', 100 * 365);
    lang = 'default';
  }

  if (typeof meta.notes[lang] === 'string') {
    notes = meta.notes[lang];
  } else {
    notes = meta.notes.default;
  }

  modalBody = `<div class="row"><div class="col-sm-3">Device:</div><div class="col-sm-9">${meta.device}</div></div>`;
  modalBody += `<div class="row"><div class="col-sm-3">Firmware:</div><div class="col-sm-9">${meta.firmware}</div></div>`;
  modalBody += `<div class="row"><div class="col-sm-3">UA Match?:</div><div class="col-sm-9">${uaMatch}</div></div>`;
  modalBody += `<div class="row"><div class="col-sm-3">Notes:</div><div class="col-sm-9">${notes}</div></div>`;

  $('#meta-modal-title').html(meta.title);
  $('#meta-modal-body').html(modalBody);

  if (!window.Failsafe) {
    if (window.location.hash) {
      window.history.pushState({ location: window.history.state.location, modal: true }, null, `#${window.history.state.location}`);
    } else {
      window.history.pushState({ location: window.history.state.location, modal: true }, null, ' ');
    }

    $('#meta-modal').on('hide.bs.modal', () => {
      if (window.history.state.location === '') {
        displayHome();
      } else {
        displayCategory(window.history.state.location);
      }
    });
  }

  $('#meta-modal').modal('show');
}

function isValidDate(inputDate) {
  const compiledDate = new Date(inputDate);
  return compiledDate instanceof Date && !Number.isNaN(Number(compiledDate));
}

function entryMeta(category, entry) {
  let updatedDate;
  let lang;
  let description;
  let modalBody;
  let cacheCheck = '<span class="badge badge-warning">Not Cached</span>';
  const meta = window.Menu[category].entries[entry];

  let cacheStatus = JSON.parse(getStorage('cache-status'));

  if (!cacheStatus) {
    cacheStatus = {};
  }

  if (typeof meta === 'undefined') {
    myAlert('danger', 'Unable to retrieve metadata');
    return;
  }

  $.extend(true, {
    title: '',
    version: '',
    updated: '',
    device: '',
    firmware: '',
    description: {
      default: '',
    },
    author: '',
    url: '',
  }, meta);

  if (!meta.updated || !isValidDate(meta.updated)) {
    updatedDate = 'Invalid Date';
    if (category in cacheStatus && entry in cacheStatus[category]
      && !isValidDate(new Date(updatedDate))) {
      cacheCheck = '<span class="badge badge-warning">Unknown</span>';
    }
  } else {
    updatedDate = new Date(meta.updated).toLocaleString();
    if (category in cacheStatus && entry in cacheStatus[category]) {
      if (new Date(updatedDate) <= new Date(cacheStatus[category][entry])) {
        cacheCheck = '<span class="badge badge-success">Up to Date</span>';
      } else {
        cacheCheck = '<span class="badge badge-danger">Out of Date</span>';
      }
    }
  }

  lang = getCookie('language');
  if (typeof lang !== 'string') {
    setCookie('language', 'default', 100 * 365);
    lang = 'default';
  }

  if (typeof meta.description[lang] === 'string') {
    description = meta.description[lang];
  } else {
    description = meta.description.default;
  }

  modalBody = `<div class="row"><div class="col-sm-3">Version:</div><div class="col-sm-9">${meta.version}</div></div>`;
  modalBody += `<div class="row"><div class="col-sm-3">Updated:</div><div class="col-sm-9">${updatedDate}</div></div>`;
  modalBody += `<div class="row"><div class="col-sm-3">Cache Check:</div><div class="col-sm-9">${cacheCheck}</div></div>`;
  modalBody += `<div class="row"><div class="col-sm-3">Device:</div><div class="col-sm-9">${meta.device}</div></div>`;
  modalBody += `<div class="row"><div class="col-sm-3">Firmware:</div><div class="col-sm-9">${meta.firmware}</div></div>`;
  modalBody += `<div class="row"><div class="col-sm-3">Description:</div><div class="col-sm-9">${description}</div></div>`;
  modalBody += `<div class="row"><div class="col-sm-3">Author(s):</div><div class="col-sm-9">${meta.author}</div></div>`;
  modalBody += `<div class="row"><div class="col-sm-3">URL:</div><div class="col-sm-9"><a href="${meta.url}">${meta.url}</a></div></div>`;

  $('#meta-modal-title').html(meta.title);
  $('#meta-modal-body').html(modalBody);

  if (!window.Failsafe) {
    if (window.location.hash) {
      window.history.pushState({ location: window.history.state.location, modal: true }, null, `#${window.history.state.location}`);
    } else {
      window.history.pushState({ location: window.history.state.location, modal: true }, null, ' ');
    }

    $('#meta-modal').on('hide.bs.modal', () => {
      if (window.history.state.location === '') {
        displayHome();
      } else {
        displayCategory(window.history.state.location);
      }
    });
  }

  $('#meta-modal').modal('show');
}

function settingsModal() {
  if ($('#settings-modal').is(':visible')) {
    return;
  }

  $('.modal').modal('hide');

  getSettingsAsync((settingsArray) => {
    if (settingsArray) {
      const currentLanguage = getCookie('language');
      const currentTheme = getCookie('theme');

      const languageKeys = Object.keys(settingsArray.languages);
      $('#language-selection').html('');
      for (let i = 0; i < languageKeys.length; i += 1) {
        $('#language-selection').append(`<option value="${settingsArray.languages[languageKeys[i]]}">${languageKeys[i]}</option>`);
      }

      try {
        $(`#language-selection option[value='${currentLanguage}']`).attr('selected', true);
      } catch (e) { /* Purposely Left Blank */ }

      $('#theme-selection').html('');
      for (let i = 0; i < settingsArray.themes.length; i += 1) {
        $('#theme-selection').append(`<option value="${settingsArray.themes[i]}">${settingsArray.themes[i]}</option>`);
      }

      try {
        $(`#theme-selection option[value='${currentTheme}']`).attr('selected', true);
      } catch (e) { /* Purposely Left Blank */ }
    }

    if (navigator.onLine) {
      $('#custom-theme-options').show();
    } else {
      $('#custom-theme-options').hide();
    }

    const backgroundURL = getStorage('background-image-url');
    const cssURL = getStorage('custom-css-url');
    const jsURL = getStorage('custom-js-url');

    if (backgroundURL) {
      $('#background-image-url').val(backgroundURL);
    }
    if (cssURL) {
      $('#custom-css-url').val(cssURL);
    }
    if (jsURL) {
      $('#custom-js-url').val(jsURL);
    }

    $('#submit-language').on('click', () => {
      setCookie('language', $('#language-selection').val(), 100 * 365);
    });

    $('#submit-theme').on('click', () => {
      if (getCookie('theme') !== $('#theme-selection').val()) {
        setCookie('theme', $('#theme-selection').val(), 100 * 365);
        window.location.reload();
      }
    });

    // Just a quick check to see if the URL is at least http(s)://*.*
    const urlRegex = /^https?:\/\/.+\..+/i;

    $('#submit-background-image').on('click', () => {
      if ($('#background-image-url').val() === '') {
        $('body').css('background-image', '');
        deleteStorage('background-image-url');
        deleteStorage('background-image');
      } else if (($('#background-image-url').val()).match(urlRegex)) {
        imageToBackground($('#background-image-url').val(), (backgroundData) => {
          setStorage('background-image-url', $('#background-image-url').val(), 'string');
          setStorage('background-image', backgroundData, 'string');
          $('body').css('background-image', `url('${backgroundData}')`);
        }, false);
      }
    });

    $('#submit-css').on('click', () => {
      $('style').remove();
      if ($('#custom-css-url').val() === '') {
        deleteStorage('custom-css-url');
        deleteStorage('custom-css');
      } else if (($('#custom-css-url').val()).match(urlRegex)) {
        getDataAsync($('#custom-css-url').val(), (cssData) => {
          setStorage('custom-css', cssData, 'string');
          setStorage('custom-css-url', $('#custom-css-url').val(), 'string');
          $('head').append(`<style>${cssData}</style>`);
        }, true);
      }
    });

    $('#submit-js').on('click', () => {
      if ($('#custom-js-url').val() === '') {
        deleteStorage('custom-js-url');
        deleteStorage('custom-js');
        window.location.reload();
      } else if (($('#custom-js-url').val()).match(urlRegex)) {
        getDataAsync($('#custom-js-url').val(), (jsData) => {
          setStorage('custom-js', jsData, 'string');
          setStorage('custom-js-url', $('#custom-js-url').val(), 'string');
          window.location.reload();
        }, true);
      }
    });

    $('#reload-page').on('click', () => {
      window.location.reload();
    });

    $('#reset-defaults').on('click', () => {
      deleteStorage('background-image-url');
      deleteStorage('background-image');
      deleteStorage('custom-css-url');
      deleteStorage('custom-css');
      deleteStorage('custom-js-url');
      deleteStorage('custom-js');
      window.location.reload();
    });

    if (!window.Failsafe) {
      if (window.location.hash) {
        window.history.pushState({ location: window.history.state.location, modal: true }, null, `#${window.history.state.location}`);
      } else {
        window.history.pushState({ location: window.history.state.location, modal: true }, null, ' ');
      }

      $('#settings-modal').on('hide.bs.modal', () => {
        if (window.history.state.location === '') {
          displayHome();
        } else {
          displayCategory(window.history.state.location);
        }
      });
    }

    $('#settings-modal').modal('show');
  });
}

function randomBackground() {
  // TODO: Holiday images for certain dates
  const imageArray = [
    `url("${getBasePath()}/themes/Default/images/0.png")`,
    `url("${getBasePath()}/themes/Default/images/1.png")`,
    `url("${getBasePath()}/themes/Default/images/2.png")`,
    `url("${getBasePath()}/themes/Default/images/3.png")`,
  ];

  $('body').css('background-image', imageArray[Math.floor(Math.random() * imageArray.length)]);
}

// --- On Ready ---------------------------------------------------------------

$(() => {
  if (window.history.state === null) {
    window.history.replaceState({}, null, window.location.hash ? window.location.hash : ' ');
    if (window.history.state === null && getCookie('session-warning') !== 'true') {
      document.cookie = `session-warning=true; domain=${window.location.hostname}; path=${window.location.pathname};`;
      // eslint-disable-next-line no-alert
      alert('This session is bugged. The circle button will close the browser rather than going back in the menu. Use the on screen controls.');
    }
  }

  window.Failsafe = window.history.state === null;

  // randomBackground();
  const customBackgroundImage = getStorage('background-image');
  const customCSS = getStorage('custom-css');
  const customJS = getStorage('custom-js');

  if (customBackgroundImage) {
    $('body').css('background-image', `url(${customBackgroundImage})`);
  }
  if (customCSS) {
    $('head').append(`<style>${customCSS}</style>`);
  }
  if (customJS) {
    $('head').append(`<script>${customJS}</script>`);
  }

  // Blank out iFrame
  $('#ifr').attr('src', `${getBasePath()}/blank.html`);

  // Cache theme
  if (navigator.onLine) {
    cacheTheme();
  }

  // Build window.Menu
  getMenuAsync((response) => {
    if (response !== undefined) {
      window.Menu = response;

      // Display new alert if online.
      if (navigator.onLine) {
        newsAlert();
      }

      // Modify Menu for cache
      if (!navigator.onLine) {
        const cacheStatus = JSON.parse(getStorage('cache-status'));
        $.each(window.Menu, (i, category) => {
          $.each(category.entries, (j, entry) => {
            if (!entry.offline) {
              delete window.Menu[i].entries[j];
            } else if (!{}.hasOwnProperty.call(cacheStatus, i)
              || !{}.hasOwnProperty.call(cacheStatus[i], j)) {
              delete window.Menu[i].entries[j];
            }
          });
          if ($.isEmptyObject(window.Menu[i].entries)) {
            delete window.Menu[i];
          }
        });
      }

      // Try to autoload
      triggerAutoload();

      // Build HTML
      buildHTML();

      // Load preselected page based on URI hash and redirect to category if there is only one.
      if (window.location.hash) {
        if (decodeURIComponent(window.location.hash.substr(1)) in window.Menu) {
          displayCategory(decodeURIComponent(window.location.hash.substr(1)));
        } else {
          displayHome();
        }
      } else if (Object.keys(window.Menu).length === 1) {
        displayCategory(Object.keys(window.Menu)[0]);
      } else {
        displayHome();
      }

      // --- Handlers ---------------------------------------------------------

      $(window).on('keyup', (event) => {
        if (event.keyCode === 27) {
          clearFrame();
          clearOverlays();
          if ($('.modal').is(':visible')) {
            $('.modal').modal('hide');
          } else {
            displayHome();
          }
        }
        if (event.keyCode === 118) {
          $('#settings-modal').modal('show');
        }
      });

      $('.category-button').on('click', (event) => {
        displayCategory($(event.target).data('category'));
      });

      $('.entry-button').on('click', (event) => {
        exploitLoader($(event.target).data('category'), $(event.target).data('entry'));
      });

      $('.about-button').on('click', (event) => {
        if ($(event.target).data('entry')) {
          entryMeta($(event.target).data('category'), $(event.target).data('entry'));
        } else {
          categoryMeta($(event.target).data('category'));
        }
      });

      $('.autoload-button').on('click', (event) => {
        triggerAutoload($(event.target).data('category'), $(event.target).data('entry'));
      });

      $('.cache-button').on('click', (event) => {
        if ($(event.target).data('entry')) {
          cacheEntry($(event.target).data('category'), $(event.target).data('entry'));
        } else {
          cacheCategory($(event.target).data('category'));
        }
      });

      $('.cache-all-button').on('click', (event) => {
        if ($(event.target).data('category')) {
          cacheCategory($(event.target).data('category'));
        } else {
          cacheAll();
        }
      });

      $('.back-button').on('click', () => {
        displayHome();
      });

      $('#settings-modal').on('show.bs.modal', settingsModal);
    } else {
      $(document).prop('title', 'Menu Error | Exploit Host by Al Azif');

      $('#title').text('Menu Error');
      $('#header').text('');

      let htmlString = '<div class="btn-group">';
      htmlString += '<button class="btn btn-primary btn-custom-main btn-custom-full">Unable to Retrieve Menu</button>';
      htmlString += '</div>';
      $('#buttons').html(htmlString);
    }
  });
});
/*
Copyright (c) 2017-2019 Al Azif, https://github.com/Al-Azif/ps4-exploit-host

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
