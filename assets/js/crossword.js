function drawCrossword(element, crossword) {
  const rows = crossword.split('\n');

  const table = $('<table />');
  for (let y = 0; y < rows.length; y++) {
    const row = rows[y];
    const tableRow = $('<tr />');
    for (let x = 0; x < row.length; x++) {
      const cell = $('<td />');
      const val = row[x];
      let displayVal = val;
      if (val !== ' ') {
        cell.addClass('ltr');
      }
      if (val === '*') {
        cell.addClass('edit');
        cell.prop('contentEditable', true);
        cell.on('keydown', function (event) {
          if (event.key.length === 1) {
            cell.text('');
          }
        });
        cell.on('keyup', function (event) {
          let cell = $(this);
          if (event.key.length === 1) {
            cell.text(event.key);
            let next = cell.nextAll('.edit').first();
            if (next.length === 0) {
              const nextRow = cell.parent().nextAll('tr:has(.edit)').first();
              next = nextRow.find('.edit').first();
            }
            next.focus();
          }
        });
        cell.bind('cut copy paste', function (e) {
          e.preventDefault();
        });
        displayVal = ' ';
      }
      cell.text(displayVal);
      tableRow.append(cell);
    }
    table.append(tableRow);
  }
  element.html(table);
}

function grabCrossword(element) {
  let crossword = '';
  let missing = 0;
  element.find('tr').each(function (y, tableRow) {
    $(tableRow).find('td').each(function (x, cell) {
      const $cell = $(cell);
      const val = $cell.text();
      crossword += val;
      if ($cell.hasClass('edit') && (val.length === 0 || val === ' ')) {
        missing += 1;
      }
    });
    crossword += '\n';
  });
  return {
    crossword: crossword,
    missing: missing,
  };
}


function sendCrossword(url, data) {
  return $.ajax({
    url: url,
    type: 'PUT',
    data: data,
    contentType: 'text/plain',
  });
}

function setupCrossword(url, element, messageBox) {
  function setMessage(message, type = 'info') {
    const msgDiv = $('<div class="alert"/>');
    msgDiv.addClass(`alert-${type}`);
    msgDiv.append($('<span />').text(
      `${new Date().toLocaleTimeString()} ${message}`
    ));
    messageBox.html(msgDiv);
  }

  $.ajax({
    url: url,
    type: 'GET',
    dataType: 'text',
  }).done((data) => {
    drawCrossword(element, data);
    element.find('.edit').keyup(
      _.debounce(() => {
        const snapshot = grabCrossword($('#crossword'));
        if (snapshot.missing === 0) {
          sendCrossword(url, snapshot.crossword).done((data, textStatus, jqXHR) => {
            setMessage('Success!', 'success');
            window.setTimeout(() => location.reload(), 500); // somewhat ugly, but backend will redirect us to next challenge
          }).fail((jqXHR, textStatus, errorThrown) => {
            let msg;
            if (jqXHR.responseJSON.message) {
              msg = `${jqXHR.responseJSON.message}`;
            } else {
              msg = `${textStatus} ${errorThrown} ${jqXHR.status}`;
            }
            setMessage(msg, 'danger');
          });
        } else {
          setMessage(`You have yet to fill ${snapshot.missing} spots`, 'info');
        }
      }, 1500)
    )
  });
}

window.setupCrossword = setupCrossword;
