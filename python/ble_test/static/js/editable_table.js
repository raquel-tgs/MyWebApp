// Checkbox Logic

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

// Rescan Zone Logic (Needs Refactoring, Use HTML form element to submit)

function submitFormGateway() {
  document.getElementById('formGateway').submit();
}

// Read NFC logic

// Capture checkbox changes and send data to Flask
// document.addEventListener('change', function(e) {
//   if (e.target && e.target.matches('input.checkbox_read_nfc')) {
//     let isChecked = e.target.checked;
//     let rowId = e.target.getAttribute('data-id');

//     // Send checkbox state to Flask using fetch
//     fetch('/checkbox_read_nfc', {
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
