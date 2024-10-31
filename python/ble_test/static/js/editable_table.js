// Load Tag Table ---
const tableDiv = null //document.getElementById('table');

const updateUrl = (prev, query) => {
  return prev + (prev.indexOf('?') >= 0 ? '&' : '?') + new URLSearchParams(query).toString();
};

const editableCellAttributes = (data, row, col) => {
    if (row) {
      return {contentEditable: 'true', 'data-element-id': row.cells[1].data};
    }
    else {
      return {};
    }
};

// Function to check/uncheck the checkbox based on Flask response
function updateCheckboxState(rowId, checkbox) {
  fetch(`/checkbox_state?rowId=${rowId}`)
    .then(response => response.json())
    .then(data => {
      if (data.checked) {
        checkbox.checked = true;
      } else {
        checkbox.checked = false;
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

if(tableDiv) {
  const grid = new gridjs.Grid({
    columns: [
      { id: 'select', name: 'select',width: '80px;',sort: true, 'attributes': editableCellAttributes,
                formatter: (cell, row) => {
        return gridjs.html(`<input type="checkbox" class="checkbox_select" data-id="${row.cells[1].data}" />`);
      }
  
      },
      { id: 'mac', name: 'MAC', sort: true, formatter: (cell) => gridjs.html(`
        <a href="/tag-details/${cell}">${cell}</a>
      `)},
      { id: 'name', name: 'Name', sort: false},
      { id: 'tag_id', name: 'Tag ID', sort: true ,  'attributes': editableCellAttributes},
      { id: 'asset_id', name: 'Asset ID',  'attributes': editableCellAttributes, sort: true },
      { id: 'certificate_id', name: 'Certificate ID',  'attributes': editableCellAttributes, sort: false },
      { id: 'type', name: 'Type',  'attributes': editableCellAttributes, sort: true },
      { id: 'expiration_date', name: 'Expiration Date',  'attributes': editableCellAttributes, sort: false },
      { id: 'color', name: 'Color', 'attributes': editableCellAttributes, sort: true },
      { id: 'series', name: 'Series', 'attributes': editableCellAttributes, sort: true },
      { id: 'asset_images_file_extension', name: 'Asset Images',  'attributes': editableCellAttributes, sort: true, 
        formatter: (cell, row) => gridjs.html(`
          <div class="upload-container">
            <span>${cell}</span>
            <form class="upload-form" action="/api/image" method="post" enctype=multipart/form-data>
              <input type="file" id="file-input" name="image" accept="image/*">
              <input type="hidden" name="certificate_id" value="${row.cells[5].data}" />
              <input type="hidden" name="mac" value="${row.cells[1].data}" />
              <button class="upload-btn" type="submit">Upload</button>
            </form>
  
          </div>
        `) 
      },
      { id: 'read_nfc', name: 'Read NFC',  'attributes': editableCellAttributes, sort: true ,
        formatter: (cell, row) => {
          return gridjs.html(`<input type="checkbox" class="checkbox_read_nfc" data-id="${row.cells[1].data}" />`);
        }
      },
      { id: 'x', name: 'X', sort: false },
      { id: 'y', name: 'Y', sort: false },
      { id: 'test', name: 'Test', sort: false}
    ],
    server: {
      url: '/api/data',
      then: results => results.data,
      total: results => results.total,
    },
    search: {
      enabled: true,
      server: {
        url: (prev, search) => {
          return updateUrl(prev, {search});
        },
      },
    },
  
    sort: {
      enabled: true,
      multiColumn: true,
      server: {
        url: (prev, columns) => {
          const columnIds = [  'select','mac', 'name','tag_id','asset_id','certificate_id','type','expiration_date','color','series','asset_images_file_extension','read_nfc','x','y'];
          const sort = columns.map(col => (col.direction === 1 ? '+' : '-') + columnIds[col.index]);
          return updateUrl(prev, {sort});
        },
      },
    },
    pagination: {
      enabled: true,
      server: {
        url: (prev, page, limit) => {
          return updateUrl(prev, {start: page * limit, length: limit});
        },
      },
    },
  
  }).render(tableDiv);
  
  let savedValue;
  
  tableDiv.addEventListener('focusin', ev => {
    if (ev.target.tagName === 'TD') {
      savedValue = ev.target.textContent;
    }
  });
  
  tableDiv.addEventListener('focusout', ev => {
    if (ev.target.tagName === 'TD') {
      if (savedValue !== ev.target.textContent) {
        fetch('/api/data', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            id: ev.target.dataset.elementId,
            [ev.target.dataset.columnId]: ev.target.textContent
          }),
        });
      }
      savedValue = undefined;
    }
  });
  
  tableDiv.addEventListener('keydown', ev => {
    if (ev.target.tagName === 'TD') {
      if (ev.key === 'Escape') {
        ev.target.textContent = savedValue;
        ev.target.blur();
      }
      else if (ev.key === 'Enter') {
        ev.preventDefault();
        ev.target.blur();
      }
    }
  });
}

// Capture checkbox changes and send data to Flask
document.addEventListener('change', function(e) {
  if (e.target && e.target.matches('input.checkbox_select')) {
    let isChecked = e.target.checked;
    let rowId = e.target.getAttribute('data-id');

    // Send checkbox state to Flask using fetch
    fetch('/checkbox_select', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ rowId: rowId, checked: isChecked })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  }
});

const tagCheckboxes = document.getElementsByClassName('tag-checkbox')
for(tagCheckbox of tagCheckboxes) {
  tagCheckbox.addEventListener('change', function(e) {
    const isChecked = e.target.checked;
    const rowId = e.target.getAttribute('data-id');
    checkboxSelect(isChecked, rowId)
  })
}
const selectAll = document.getElementById('select-all')
selectAll.addEventListener('click', function() {
  for(tagCheckbox of tagCheckboxes) {
    tagCheckbox.checked = !tagCheckbox.checked;
    const isChecked = tagCheckbox.checked;
    const rowId = tagCheckbox.getAttribute('data-id');
    checkboxSelect(isChecked, rowId)
  }
})

function checkboxSelect(isChecked, rowId) {
  fetch('/checkbox_select', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ rowId: rowId, checked: isChecked })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}

// Capture checkbox changes and send data to Flask
document.addEventListener('change', function(e) {
  if (e.target && e.target.matches('input.checkbox_read_nfc')) {
    let isChecked = e.target.checked;
    let rowId = e.target.getAttribute('data-id');

    // Send checkbox state to Flask using fetch
    fetch('/checkbox_read_nfc', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ rowId: rowId, checked: isChecked })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  }
});

function updater() {
  $.get('/data', function(data) {
    var splitData = data.split('#');
    $('#time').html(splitData[0]);  // update page with new data

    if (splitData[1] === "Enabled") {
        $('#Scan').removeClass("disabled");
        $('#Update').removeClass("disabled");
        $('#Location').removeClass("disabled");
        $('#Scan').removeClass("bold-border");
        $('#Update').removeClass("bold-border");
        $('#Location').removeClass("bold-border");
    } else {
        $('#Scan').addClass("disabled");
        $('#Update').addClass("disabled");
        $('#Location').addClass("disabled");
        if (splitData[2] === "Scan") {
          $('#Scan').addClass("bold-border")
        }
        if (splitData[2] === "Update") {
          $('#Update').addClass("bold-border")
        }
        if (splitData[2] === "Location") {
          $('#Location').addClass("bold-border")
        }
    }

    if (splitData[3] === "True") {
        grid.updateConfig({ search: true}).forceRender();
    }

  });
};

function updater_bar() {
  $.get('/databar', function(data) {
    $('#myprogressBar').css('width', data);;  // update page with new data
  });
};

function updater_statuslog() {
  $.get('/data_statuslog', function(data) {
    $('#statuslog').text(data);  // update page with new data
  });
};

setInterval(updater, 1000);  // run `updater()` every 1000ms (1s)
setInterval(updater_bar, 2000);  // run `updater_bar()` every 2000ms (2s)
setInterval(updater_statuslog, 1000);  // run `updater_statuslog()` every 1000ms (1s)

function submitFormGateway() {
  document.getElementById('formGateway').submit();
}