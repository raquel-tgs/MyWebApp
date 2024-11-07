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

// Capture checkbox changes and send data to Flask
// document.addEventListener('change', function(e) {
//   if (e.target && e.target.matches('input.checkbox_select')) {
//     let isChecked = e.target.checked;
//     let rowId = e.target.getAttribute('data-id');

//     // Send checkbox state to Flask using fetch
//     fetch('/checkbox_select', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//       },
//       body: JSON.stringify({ rowId: rowId, checked: isChecked })
//     })
//     .then(response => response.json())
//     .then(data => {
//       console.log('Success:', data);
//     })
//     .catch((error) => {
//       console.error('Error:', error);
//     });
//   }
// });

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



// const opModal = document.getElementById('op-modal')
// const modalOpen = opModal.getAttribute('modalOpen');
// if(modalOpen == 'True') {
//   opModal.showModal()
// } else {
//   opModal.close()
// }

// const opModalBtn = document.getElementById('op-modal-btn-close')
// opModalBtn.addEventListener('click', () => {
//   opModal.close()
// })



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
      $('#op-modal-btn-close').removeClass("hide-block")
      $('#op-modal-btn-cancel').removeClass("show-block")

      $('#op-modal-btn-close').addClass("show-block")
      $('#op-modal-btn-cancel').addClass("hide-block")
    } else {
      $('#op-modal-btn-close').removeClass("show-block")
      $('#op-modal-btn-cancel').removeClass("hide-block")

      $('#op-modal-btn-close').addClass("hide-block")
      $('#op-modal-btn-cancel').addClass("show-block")
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
