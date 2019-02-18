class TMDB {
  constructor() {
    this.url = '';
    this.json = '';
  }

  update(url) {
    if (url !== this.url) {
      this.url = url;
      this.json = $.ajax({
        dataType: 'json',
        url: this.url,
        async: false,
      }).responseJSON;
    }
  }

  get icon() {
    if (this.json !== undefined) {
      return this.json.icons[0].icon;
    }
    return undefined;
  }

  get name() {
    if (this.json !== undefined) {
      return this.json.names[0].name;
    }
    return undefined;
  }
}

function clearInputRPI() {
  $('#meta-info').hide();
  $('#installURL').val('http://');
  $('#pkgSearch').val('');
  $('#uninstallID').val('');
  $('#uninstallRadioGame').prop('checked', true);
  $('#taskContentID').val('');
  $('#taskRadioGame').prop('checked', true);
  $('#taskID').val('');
}

function getPKGListRPI() {
  return $.ajax({
    dataType: 'json',
    url: '/api/pkglist',
    async: false,
  }).responseJSON;
}

function showResponseRPI(type, message) {
  let color = '';

  if (type === 'fail') {
    color = ' text-danger';
  } else if (type === 'success') {
    color = ' text-success';
  }
  $('#responseText').html(`<p class="text-center${color}">${JSON.stringify(message)}</p>`);
}

function getTMDBURLRPI(tid) {
  let sha1HMAC;
  let tmdbHash;
  let tmdbURL;

  // Insert key here (In hex format). It will be automatically checked against the correct hash
  let key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX';

  key = key.toUpperCase();

  const sha256 = new jsSHA('SHA-256', 'TEXT');
  sha256.update(key);
  const keyHash = sha256.getHash('HEX');

  if (keyHash.toUpperCase() === '2AB0555FABF50901A5D7CD56962769F0274374FA56C7E81E77EC386B22834AFB') {
    sha1HMAC = new jsSHA('SHA-1', 'TEXT');

    sha1HMAC.setHMACKey(key, 'HEX');
    sha1HMAC.update(tid);
    tmdbHash = sha1HMAC.getHMAC('HEX');
    tmdbHash = tmdbHash.toUpperCase();

    tmdbURL = `https://tmdb.np.dl.playstation.net/tmdb2/${tid}_${tmdbHash}/${tid}.json`;
  } else {
    tmdbURL = 'http://0.0.0.0';
  }

  return tmdbURL;
}

function displayTIDMetaRPI(tid) {
  window.Meta.update(getTMDBURLRPI(tid));
  if (window.Meta.icon !== undefined) {
    $('#meta-icon').attr('src', window.Meta.icon);
  }
  if (window.Meta.name !== undefined) {
    $('#meta-name').text(window.Meta.name);
  }

  if (window.Meta.icon === undefined && window.Meta.name === undefined) {
    $('#meta-info').hide();
  } else {
    $('#meta-info').show();
  }
}

function setLastIPRPI(element) {
  let result;

  const decodedCookie = decodeURIComponent(document.cookie);
  const cookies = decodedCookie.split(';');

  $.each(cookies, (i, field) => {
    while (field.charAt(0) === ' ') {
      field = field.substring(1);
    }
    if (field.indexOf('last_ip=') === 0) {
      result = field.substring('last_ip='.length, field.length);
    }
  });

  if (result !== undefined) {
    $(element).val(result);
  } else {
    $(element).val('0.0.0.0');
    document.cookie = 'last_ip=0.0.0.0; expires=Tue, 19 Jan 2038 03:14:07 UTC;';
  }
}

function validateInputRPI(inputType, value) {
  let pattern;

  if (inputType === 'IP') {
    pattern = /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/;
  } else if (inputType === 'URL') {
    pattern = /^http[s]?:\/\/.+/i;
  } else if (inputType === 'ContentID') {
    pattern = /^[A-Z]{2}[0-9]{4}-[A-Z]{4}[0-9]{5}_[0-9]{2}-[A-Z0-9]{16}$/;
  } else if (inputType === 'TitleID') {
    pattern = /^[A-Z]{4}[0-9]{5}$/;
  } else if (inputType === 'TaskID') {
    pattern = /^(?:[1-9][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[0-9])$/;
  } else {
    return false;
  }
  return pattern.test(value);
}

function sendCommandRPI(ip, endpoint, command) {
  const compiledURL = `http://${ip}:12800/api/${endpoint}`;

  if (validateInputRPI('IP', ip)) {
    document.cookie = `last_ip=${ip}; expires=Tue, 19 Jan 2038 03:14:07 UTC;`;
    return $.ajax({
      type: 'POST',
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      url: compiledURL,
      data: command,
      async: false,
      beforeSend: () => {
        $('#sendingOverlay').show();
      },
      complete: () => {
        $('#sendingOverlay').hide();
      },
    }).responseJSON;
  }
  // eslint-disable-next-line no-alert
  alert('Invalid IP');
  return undefined;
}

function isExistsRPI(ip, tid) {
  let response;
  let type;

  if (validateInputRPI('TitleID', tid.toUpperCase())) {
    response = sendCommandRPI(ip, 'is_exists', `{"title_id": "${tid.toUpperCase()}"}`);
    type = response.status;
    // TODO: Parse response
    showResponseRPI(type, response);
    return;
  }
  // eslint-disable-next-line no-alert
  alert('Validation Error');
}

function installRPI(ip, urlType, url) {
  let response;
  let type;

  if (validateInputRPI('URL', url)) {
    if (urlType === 'direct') {
      response = sendCommandRPI(ip, 'install', `{"type": "direct", "packages": ["${url}"]}`);
    } else if (urlType === 'ref_pkg_url') {
      response = sendCommandRPI(ip, 'install', `{"type": "ref_pkg_url", "url": "${url}"}`);
    }
    type = response.status;
    // TODO: Parse response
    showResponseRPI(type, response);
    return;
  }
  // eslint-disable-next-line no-alert
  alert('Validation Error');
}

function uninstallRPI(ip, endpoint, uid) {
  let response;
  let type;

  if (endpoint === 'uninstall_game' || endpoint === 'uninstall_patch') {
    if (validateInputRPI('TitleID', uid.toUpperCase())) {
      response = sendCommandRPI(ip, endpoint, `{"title_id": "${uid.toUpperCase()}"}`);
      type = response.status;
      // TODO: Parse response
      showResponseRPI(type, response);
      return;
    }
  } else if (endpoint === 'uninstall_ac' || endpoint === 'uninstall_theme') {
    if (validateInputRPI('ContentID', uid.toUpperCase())) {
      response = sendCommandRPI(ip, endpoint, `{"content_id": "${uid.toUpperCase()}"}`);
      type = response.status;
      // TODO: Parse response
      showResponseRPI(type, response);
      return;
    }
  }
  // eslint-disable-next-line no-alert
  alert('Validation Error');
}

function findTaskRPI(ip, taskType, cid) {
  let response;
  let type;

  if (validateInputRPI('ContentID', cid.toUpperCase())) {
    response = sendCommandRPI(ip, 'find_task', `{"content_id": "${cid.toUpperCase()}", "sub_type": ${taskType}}`);
    type = response.status;
    // TODO: Parse response
    showResponseRPI(type, response);
    return;
  }
  // eslint-disable-next-line no-alert
  alert('Validation Error');
}

function taskRPI(ip, taskType, taskID) {
  let response;
  let type;

  if (validateInputRPI('TaskID', taskID)) {
    response = sendCommandRPI(ip, taskType, `{"task_id": ${taskID}}`);
    type = response.status;
    // TODO: Parse response
    showResponseRPI(type, response);
    return;
  }
  // eslint-disable-next-line no-alert
  alert('Validation Error');
}

function makePkgButtonRPI(pkgName, pkgSize, pkgURL) {
  let output;

  const truncateLength = 43;
  let truncatedName = pkgName.substring(0, truncateLength - 3);

  if (pkgName.length > truncateLength) {
    truncatedName += '...';
  }

  const i = pkgSize === 0 ? 0 : Math.floor(Math.log(pkgSize) / Math.log(1024));
  const formattedSize = `${(pkgSize / (1024 ** i)).toFixed(2) * 1} ${['B', 'kB', 'MB', 'GB', 'TB'][i]}`;
  output = '<button type="button" class="btn-pkg-list list-group-item list-group-item-action p-0 pb-1 pl-2" ';
  output += `data-pkg-url="${pkgURL}">`;
  output += `${truncatedName}<span class="badge badge-primary ml-1">${formattedSize}</span></button>`;

  return output;
}

function makePkgArrayRPI(pkgJson) {
  let output = '';

  if (pkgJson !== undefined) {
    $.each(pkgJson, (i, field) => {
      if (field === 'No PKGs Found') {
        output = '<p class="text-center text-danger">No PKGs found on host</p>';
      } else if (field === 'I/O Error on Host') {
        output = '<p class="text-center text-danger">I/O error on host</p>';
      } else if (field === 'No results') {
        output = '<p class="text-center text-danger">No results</p>';
      } else {
        output += makePkgButtonRPI(field.Filename, field.Filesize, field.File_URL);
      }
    });
  }

  if (output === '') {
    output = '<p class="text-center text-danger">Error connecting to host</p>';
  }
  return output;
}

function checkPkgLink() {
  let match;

  const patternCID = /[A-Z]{2}[0-9]{4}-([A-Z]{4}[0-9]{5}_[0-9]{2})-[A-Z0-9]{16}/i;
  const patternTID = /([A-Z]{4}[0-9]{5})/i;

  if (patternCID.test($('#installURL').val())) {
    match = patternCID.exec($('#installURL').val());
    match = match[1].toUpperCase();
    displayTIDMetaRPI(match);
  } else if (patternTID.test($('#installURL').val())) {
    match = patternTID.exec($('#installURL').val());
    match = `${match[1].toUpperCase()}_00`;
    displayTIDMetaRPI(match);
  } else {
    $('#meta-info').hide();
  }
}

$(() => {
  let searchJson;
  let searchTerm;

  window.Meta = new TMDB();

  if (!navigator.onLine) {
    $('#offlineOverlay').show();
    return;
  }

  setLastIPRPI('#ip');
  clearInputRPI();
  const pkgJson = getPKGListRPI();

  $('a[data-toggle="pill"]').click(() => {
    clearInputRPI();
    $('#header').text($(this).text());
  });

  $('#pkgSearch').keyup(() => {
    searchJson = [];
    if (pkgJson !== 'No PKGs Found' && pkgJson !== 'I/O Error on Host') {
      searchTerm = $('#pkgSearch').val().toUpperCase();
      $.each(pkgJson, (i, field) => {
        if (field.Filename.toUpperCase().indexOf(searchTerm) > -1) {
          searchJson.push(field);
        }
      });

      if (pkgJson !== undefined && searchJson.length === 0) {
        searchJson = ['No results'];
      }
      $('#pkg-list').html(makePkgArrayRPI(searchJson));
    }
  });

  $('#installURL').keyup(checkPkgLink);

  $('#btn-exists').click(() => {
    isExistsRPI($('#ip').val(), $('#existID').val());
  });

  $('#btn-install-cdn').click(() => {
    installRPI($('#ip').val(), 'ref_pkg_url', $('#installURL').val());
  });

  $('#btn-install-url').click(() => {
    installRPI($('#ip').val(), 'direct', $('#installURL').val());
  });

  $('#btn-uninstall').click(() => {
    uninstallRPI($('#ip').val(), $('input[name=\'uninstallRadios\']:checked').val(), $('#uninstallID').val());
  });

  $('#btn-task-find').click(() => {
    findTaskRPI($('#ip').val(), $('input[name=\'taskRadios\']:checked').val(), $('#taskContentID').val());
  });

  $('#btn-task-star').click(() => {
    taskRPI($('#ip').val(), 'start_task', $('#taskID').val());
  });

  $('#btn-task-stop').click(() => {
    taskRPI($('#ip').val(), 'stop_task', $('#taskID').val());
  });

  $('#btn-task-pause').click(() => {
    taskRPI($('#ip').val(), 'pause_task', $('#taskID').val());
  });

  $('#btn-task-resume').click(() => {
    taskRPI($('#ip').val(), 'resume_task', $('#taskID').val());
  });

  $('#btn-task-unregister').click(() => {
    taskRPI($('#ip').val(), 'unregister_task', $('#taskID').val());
  });

  $('#btn-task-progress').click(() => {
    taskRPI($('#ip').val(), 'get_task_progress', $('#taskID').val());
  });

  $('#pkg-list').html(makePkgArrayRPI(pkgJson));

  $('.btn-pkg-list').click((event) => {
    $('#installURL').val($(event.target).data('pkg-url'));
    checkPkgLink();
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
