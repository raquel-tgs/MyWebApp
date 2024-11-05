let savedValue;
editableFields = document.getElementsByClassName('editable-field')
for(editableField of editableFields) {
  
  editableField.addEventListener('focusin', ev => {
    savedValue = ev.target.value
  })

  editableField.addEventListener('focusout', ev => {

    const mac = ev.target.getAttribute('mac')
    const name = ev.target.name
    const value = ev.target.value

    if(savedValue != value) {
      fetch('/api/data', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          id: mac,
          [name]: value
        }),
      });
    }
  });
}
